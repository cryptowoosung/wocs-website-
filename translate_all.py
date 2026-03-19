#!/usr/bin/env python3
"""
WOCS Full Translation Builder (translate_all.py)
================================================
Translates ALL English body text to 13 languages using Gemini API.
Run ONCE → translations embedded in HTML → works offline forever.

Usage:
  1. Set Gemini API key in config.json
  2. pip install google-genai
  3. python translate_all.py
"""

import re, glob, json, os, time, sys

# ═══ CONFIG ═══
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, 'config.json')
CACHE_FILE = os.path.join(SITE_DIR, 'data', 'translations_cache.json')
LANGS = ['ja','zh','es','fr','de','pt','it','ar','ru','tr','tw','id','th']
LANG_NAMES = {
    'ja':'Japanese','zh':'Simplified Chinese','es':'Spanish','fr':'French',
    'de':'German','pt':'Portuguese','it':'Italian','ar':'Arabic',
    'ru':'Russian','tr':'Turkish','tw':'Traditional Chinese',
    'id':'Indonesian','th':'Thai'
}
BATCH_SIZE = 20
RATE_LIMIT_DELAY = 6

# ═══ LOAD CONFIG ═══
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

API_KEY = config.get('gemini_api_key', '')
if not API_KEY or 'API' in API_KEY or '여기' in API_KEY:
    print("❌ config.json에 Gemini API 키를 설정하세요!")
    print("   https://aistudio.google.com/apikey 에서 무료 발급")
    print('   config.json: {"gemini_api_key": "YOUR_KEY_HERE"}')
    sys.exit(1)

# ═══ INIT GEMINI ═══
call_gemini = None
try:
    from google import genai
    client = genai.Client(api_key=API_KEY)
    MODEL = 'gemini-2.5-flash'
    def _call(prompt):
        resp = client.models.generate_content(model=MODEL, contents=prompt)
        return resp.text
    call_gemini = _call
    print("✅ Gemini 2.5 Flash connected (google-genai)")
except ImportError:
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        def _call(prompt):
            resp = model.generate_content(prompt)
            return resp.text
        call_gemini = _call
        print("✅ Gemini 2.5 Flash connected (google-generativeai)")
    except ImportError:
        print("❌ 패키지 설치 필요:")
        print("   pip install google-genai")
        print("   또는: pip install google-generativeai")
        sys.exit(1)

# ═══ LOAD CACHE ═══
cache = {}
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f"📦 Cache loaded: {len(cache)} strings")

def save_cache():
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ═══ COLLECT STRINGS ═══
html_files = glob.glob(os.path.join(SITE_DIR, '**', '*.html'), recursive=True)
html_files = [f for f in html_files if os.path.basename(f) != 'index.html' or os.path.dirname(f) != SITE_DIR]
html_files = [f for f in html_files if f != os.path.join(SITE_DIR, 'index.html')]

print(f"\n📄 Scanning {len(html_files)} pages...")

all_ko_strings = set()
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'WOCS_PAGE_TR' not in content:
        continue
    tr = content[content.find('WOCS_PAGE_TR='):content.find(';\n', content.find('WOCS_PAGE_TR='))]
    ko_m = re.search(r'ko:\{([^}]*)\}', tr)
    if ko_m:
        for k, v in re.findall(r'(\w+):"([^"]*)"', ko_m.group(1)):
            if v.strip() and len(v) >= 2:
                all_ko_strings.add(v)

to_translate = [s for s in all_ko_strings if s not in cache]
print(f"📊 Total unique KO strings: {len(all_ko_strings)}")
print(f"   Already cached: {len(all_ko_strings) - len(to_translate)}")
print(f"   Need translation: {len(to_translate)}")

if to_translate:
    batches = [to_translate[i:i+BATCH_SIZE] for i in range(0, len(to_translate), BATCH_SIZE)]
    total_batches = len(batches)
    print(f"\n🔄 Translating {len(to_translate)} strings in {total_batches} batches...")
    
    for batch_idx, batch in enumerate(batches):
        strings_json = json.dumps(batch, ensure_ascii=False)
        prompt = f"""Translate each Korean string to English AND these languages: {', '.join(LANG_NAMES.values())}.
Context: B2B glamping/modular structure business website (WOCS brand).

Korean input: {strings_json}

Respond ONLY valid JSON array:
[{{"ko":"original korean","en":"English","ja":"Japanese","zh":"Simplified Chinese","es":"Spanish","fr":"French","de":"German","pt":"Portuguese","it":"Italian","ar":"Arabic","ru":"Russian","tr":"Turkish","tw":"Traditional Chinese","id":"Indonesian","th":"Thai"}}]

Rules:
- Keep brand names (WOCS, S-Classic, S-Lodge, Signature-O, D-Series, D-Pro, D-600, D-800) in English
- Keep numbers, units (m, kg, ㎡, mm) unchanged
- Keep technical terms where standard (PVC, LED, A/C, Wi-Fi, CNC, FEA, ROI, EPS)
- tw = Traditional Chinese (繁體), zh = Simplified Chinese (简体)
- Translate naturally, not word-by-word
- Return ONLY valid JSON, no markdown fences"""

        success = False
        for attempt in range(3):
            try:
                response_text = call_gemini(prompt)
                text = response_text.strip()
                text = re.sub(r'^```json\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
                results = json.loads(text)
                
                for item in results:
                    ko_val = item.get('ko', '')
                    if ko_val:
                        cache[ko_val] = {}
                        for lang in ['en'] + LANGS:
                            if lang in item and item[lang]:
                                cache[ko_val][lang] = item[lang]
                
                save_cache()
                pct = (batch_idx + 1) / total_batches * 100
                print(f"  [{batch_idx+1}/{total_batches}] {pct:.0f}% — {len(batch)} strings ✅")
                success = True
                break
                
            except Exception as e:
                err = str(e)
                if '429' in err or 'quota' in err.lower() or 'rate' in err.lower():
                    wait = 45
                    retry_match = re.search(r'retry in (\d+)', err)
                    if retry_match:
                        wait = int(retry_match.group(1)) + 5
                    print(f"  ⏳ Batch {batch_idx+1}: 할당량 대기 {wait}초... (시도 {attempt+1}/3)")
                    time.sleep(wait)
                else:
                    print(f"  ❌ Batch {batch_idx+1}: {str(e)[:100]}")
                    time.sleep(10)
        
        if not success:
            print(f"  ⚠️ Batch {batch_idx+1} 실패 — 나중에 다시 실행하면 이어서 진행")
        
        time.sleep(RATE_LIMIT_DELAY)

    print(f"\n📦 Cache: {len(cache)} strings saved")
else:
    print("\n✅ All strings already translated!")

# ═══ WRITE TO HTML ═══
print(f"\n📝 Writing translations to HTML...")
updated = 0

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'WOCS_PAGE_TR' not in content:
        continue
    
    tr_start = content.find('WOCS_PAGE_TR={')
    tr_end = content.find(';\n', tr_start) + 2
    tr_block = content[tr_start:tr_end]
    
    ko_m = re.search(r'ko:\{([^}]*)\}', tr_block)
    en_m = re.search(r'en:\{([^}]*)\}', tr_block)
    if not ko_m or not en_m:
        continue
    
    ko_items = dict(re.findall(r'(\w+):"([^"]*)"', ko_m.group(1)))
    en_items = dict(re.findall(r'(\w+):"([^"]*)"', en_m.group(1)))
    
    lang_items = {lang: {} for lang in ['en'] + LANGS}
    for key, ko_val in ko_items.items():
        if ko_val in cache:
            for lang in ['en'] + LANGS:
                if lang in cache[ko_val]:
                    tr = cache[ko_val][lang]
                    if tr and tr != ko_val:
                        tr = tr.replace('"', '\\"')
                        lang_items[lang][key] = tr
    
    all_langs = ['ko', 'en'] + LANGS
    parts = []
    for lang in all_langs:
        if lang == 'ko':
            s = ','.join(f'{k}:"{v}"' for k, v in ko_items.items())
        elif lang == 'en':
            # Use translated EN from cache where available, else keep existing
            merged_en = dict(en_items)
            for k, v in lang_items.get('en', {}).items():
                merged_en[k] = v
            s = ','.join(f'{k}:"{v}"' for k, v in merged_en.items())
        else:
            items = lang_items.get(lang, {})
            s = ','.join(f'{k}:"{v}"' for k, v in items.items()) if items else ''
        parts.append(f'{lang}:{{{s}}}')
    
    new_tr = 'WOCS_PAGE_TR={' + ',\n'.join(parts) + '\n};\n'
    content = content[:tr_start] + new_tr + content[tr_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    updated += 1

print(f"""
{'='*50}
✅ 완료!
   업데이트된 페이지: {updated}
   언어: 15개 (ko + en + 13)
   캐시: {len(cache)} strings → {CACHE_FILE}
   
   이제 모든 페이지가 15개 언어로 번역됩니다.
   file:// 로컬에서도 100% 작동합니다.
{'='*50}
""")
