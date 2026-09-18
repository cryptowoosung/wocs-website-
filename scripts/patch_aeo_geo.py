"""auto_writer.py에 yanglim 수준 AEO/GEO 이식 (1회성 패치 스크립트, 멱등).

- 프롬프트: 질문형 # 제목 + ## 소제목 5개, GEO 인용 단문, E-E-A-T 경험 신호, 환각 방지 지침
- generate_aeo_extras(): tldr + FAQ 3 + key_quotes 3 (JSON) — 실패 시 빈 dict, 발행은 계속
- render_key_quotes(): '한 줄로 정리하면' 블록 + CSS
- main(): extras 생성 → save_to_blog_data/save_to_html에 extra 전달 (FAQPage JSON-LD·TL;DR·FAQ 섹션은 기존 Phase 5 렌더러 재사용)
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "auto_writer.py"
s = P.read_text(encoding="utf-8")
if "def generate_aeo_extras" in s:
    print("이미 패치됨")
    sys.exit(0)

BS = "\\"  # 소스 안의 리터럴 백슬래시-n 표현을 조립하기 위한 헬퍼
NL = BS + "n"


def rep(old, new, label):
    global s
    assert s.count(old) == 1, f"anchor '{label}' matched {s.count(old)}x"
    s = s.replace(old, new)


# 1) 프롬프트 구조 블록 교체
old_struct = (
    '        "### 구조 (단락별)' + NL + '"\n'
    '        "1단락: 훅 — " + topic["region"] + " 또는 전남권 관련 구체적 상황/질문 (광고 아닌 현장 느낌)' + NL + '"\n'
    '        "2단락: 핵심 정보 1 — 이 주제의 가장 중요한 실용 정보' + NL + '"\n'
    '        "3단락: 핵심 정보 2 — 수치, 사례, 비교 중 하나 포함' + NL + '"\n'
    '        "4단락: 전문가 시각 — 16년 경력에서 나온 현장 경험담' + NL + '"\n'
    '        "5단락: 지역 특화 팁 — " + topic["region"] + " 또는 전남권 특성에 맞는 구체적 조언' + NL + '"\n'
    '        + cta_instruction + "' + NL + NL + '"\n'
)
new_struct = (
    '        "### 구조 (반드시 이 마크다운 형식)' + NL + '"\n'
    '        "첫 줄: \'# \' + 질문형 제목 (60자 이내, 예: \'광주 글램핑 창업 비용은 얼마나 드나요?\')' + NL + '"\n'
    '        "이후 소제목은 모두 \'## \' + 질문형 (예: \'## 부지 선정에서 무엇을 먼저 확인해야 하나요?\'). 소제목 5개, 각 소제목 아래 문단 1~2개' + NL + '"\n'
    '        "## 1: 훅 — " + topic["region"] + " 또는 전남권 관련 구체적 상황/질문 (광고 아닌 현장 느낌)' + NL + '"\n'
    '        "## 2: 핵심 정보 1 — 이 주제의 가장 중요한 실용 정보' + NL + '"\n'
    '        "## 3: 핵심 정보 2 — 수치, 규격, 비교 중 하나 포함' + NL + '"\n'
    '        "## 4: 전문가 시각 — 16년 현장 경력에서 나온 관찰 (\'16년 현장 경력\', \'전남 현장에서\' 같은 경험 신호 2회 이상)' + NL + '"\n'
    '        "## 5: 지역 특화 팁 — " + topic["region"] + " 또는 전남권 특성에 맞는 구체적 조언' + NL + '"\n'
    '        + cta_instruction.replace("6단락", "마지막 문단") + "' + NL + NL + '"\n'
    '        "### 인용 가능 문장 (GEO)' + NL + '"\n'
    '        "- 본문 안에 AI 검색엔진이 그대로 발췌할 수 있는 독립 단문 2~3개 포함 (각 40~70자, 규격·수치·기준 1개 이상, 앞뒤 문맥 없이도 성립)' + NL + NL + '"\n'
    '        "### 환각 방지 (필수)' + NL + '"\n'
    '        "- 확실하지 않은 단가·가격·법규 수치는 구체적 숫자 대신 \'현장 확인 필요\' 또는 \'견적 시 확정\'으로 표기' + NL + '"\n'
    '        "- 존재하지 않는 시공 사례를 실제 사례처럼 쓰지 말 것 (\'○○에 시공했다\' 금지) → 일반론·가이드형으로만 작성' + NL + '"\n'
    '        "- 보증 기간·성능 단정(\'절대 누수 없음\', \'N년 무상 A/S\') 금지, 타사 비방 금지' + NL + NL + '"\n'
)
rep(old_struct, new_struct, "prompt-structure")
rep('        "- HTML 태그 없이 순수 텍스트만 출력' + NL + NL + '"\n        "제목(H1)과 본문만 출력. 설명이나 메타 정보는 출력하지 마시오.' + NL + '"',
    '        "- HTML 태그 금지 (마크다운 #, ## 만 사용)' + NL + NL + '"\n        "제목(# 한 줄)과 본문(## 소제목 + 문단)만 출력. 설명이나 메타 정보는 출력하지 마시오.' + NL + '"',
    "prompt-tail")

# 2) AEO/GEO 확장 생성 함수
aeo_fn = '''# ─── AEO/GEO 확장: 즉답(tldr) + FAQ 3문항 + 인용형 단문 3개 (yanglim prompts.py 이식) ───

def generate_aeo_extras(title, content, topic):
    """글 본문을 바탕으로 {tldr, faq[3], key_quotes[3]} JSON 생성. 실패 시 빈 dict (발행은 계속)."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from llm_json import parse_llm_json
    prompt = (
        "다음 블로그 글을 읽고 JSON 객체만 출력하세요 (설명·코드펜스 금지).''' + NL + '''"
        "{''' + NL + '''"
        '  "tldr": "제목 질문에 대한 즉답 40~60자 한 문장 (글 최상단 핵심 답변 블록에 노출)",''' + NL + '''\'
        '  "faq": [{"q": "실무 질문", "a": "답변 2~3문장"}, {"q": "...", "a": "..."}, {"q": "...", "a": "..."}],''' + NL + '''\'
        '  "key_quotes": ["인용 가능한 독립 단문 (40~70자, 수치/규격/기준 포함)", "...", "..."]''' + NL + '''\'
        "}''' + NL + '''"
        "규칙: faq는 정확히 3개, 본문과 겹치지 않는 질문. 불확실한 단가·법규는 '현장 확인 필요'로 표기. "
        "가상의 시공 사례 금지. 키워드 '" + topic.get("keyword", "") + "'와 지역 '" + topic.get("region", "") + "'를 자연스럽게 반영.''' + NL + NL + '''"
        "## 제목''' + NL + '''" + title + "''' + NL + NL + '''## 본문''' + NL + '''" + content[:3500]
    )
    for attempt in range(2):
        raw = gemini_generate_with_retry(prompt, label="aeo-extras")
        if not raw:
            continue
        try:
            data = parse_llm_json(raw)
        except Exception as e:
            print("AEO JSON 파싱 실패 (" + str(e)[:80] + ") → 재시도")
            continue
        faq = [x for x in (data.get("faq") or []) if isinstance(x, dict) and x.get("q") and x.get("a")][:3]
        quotes = [str(x).strip() for x in (data.get("key_quotes") or []) if str(x).strip()][:3]
        tldr = str(data.get("tldr") or "").strip()
        if len(faq) == 3 and tldr:
            return {"tldr": tldr[:120], "faq": faq, "key_quotes": quotes}
        print("AEO 결과 불충분 (faq=" + str(len(faq)) + ", tldr=" + str(bool(tldr)) + ") → 재시도")
    print("AEO 확장 생성 실패 — 즉답/FAQ 없이 발행")
    return {}


'''
rep("# ─── meta description 생성 ───", aeo_fn + "# ─── meta description 생성 ───", "aeo-fn")

# 3) 인용 단문 렌더러 + CSS + 조립
quotes_fn = '''def render_key_quotes(quotes):
    if not quotes:
        return ""
    items = "".join("      <li>" + _esc(q) + "</li>''' + NL + '''" for q in quotes[:3])
    return ('  <div class="keypoints">''' + NL + '''    <span class="keypoints-label">한 줄로 정리하면</span>''' + NL + '''\'
            '    <ul>''' + NL + '''\' + items + '    </ul>''' + NL + '''  </div>''' + NL + '''\')


def render_references(references):'''
rep("def render_references(references):", quotes_fn, "quotes-fn")
rep("    faq_html = render_faq(faq)\n", "    faq_html = render_faq(faq)\n    quotes_html = render_key_quotes(extra.get(\"key_quotes\", []) or [])\n", "quotes-var")
rep("        + body_html + '" + NL + "'\n", "        + body_html + '" + NL + "'\n        + quotes_html +\n", "quotes-assembly")
css_anchor = "        '.faq{margin:48px 0}" + NL + "'\n"
css_new = (
    "        '.keypoints{margin:36px 0;padding:20px 24px;background:rgba(201,169,110,0.08);border:1px solid rgba(201,169,110,0.2)}" + NL + "'\n"
    "        '.keypoints-label{display:block;font-size:11px;letter-spacing:1px;color:var(--gold);margin-bottom:10px}" + NL + "'\n"
    "        '.keypoints ul{margin:0;padding-left:18px}" + NL + "'\n"
    "        '.keypoints li{font-family:var(--font-body);font-size:14px;color:rgba(240,235,224,0.85);line-height:1.8;margin:4px 0}" + NL + "'\n"
)
rep(css_anchor, css_new + css_anchor, "css")

# 4) main() 연결
old_main = (
    "    # 저장\n"
    "    save_to_blog_data(post_id, title, content, topic, meta_desc)\n"
    "    save_to_html(post_id, title, content, topic, meta_desc)\n"
)
new_main = (
    "    # AEO/GEO 확장 (즉답·FAQ·인용 단문) — 실패해도 발행은 계속\n"
    "    print(\"AEO/GEO 확장 생성 중...\")\n"
    "    extra = generate_aeo_extras(title, content, topic)\n"
    "    extra[\"focus_keyword\"] = topic.get(\"keyword\", \"\")\n"
    "    print(\"즉답: \" + (extra.get(\"tldr\") or \"(없음)\")[:60] + \" | FAQ \" + str(len(extra.get(\"faq\") or [])) + \"개 | 인용 \" + str(len(extra.get(\"key_quotes\") or [])) + \"개\")\n"
    "\n"
    "    # 저장\n"
    "    save_to_blog_data(post_id, title, content, topic, meta_desc, extra=extra)\n"
    "    save_to_html(post_id, title, content, topic, meta_desc, extra=extra)\n"
)
rep(old_main, new_main, "main")

P.write_text(s, encoding="utf-8")
print("auto_writer.py 패치 완료")
