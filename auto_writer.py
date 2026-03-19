#!/usr/bin/env python3
"""
WOCS AI 블로그 자동 작성기
=============================
실행: python auto_writer.py
옵션: python auto_writer.py --topic "글램핑 시공 단가" --dry-run

기능:
1. Gemini API로 SEO 최적화 블로그 글 자동 생성
2. blog-data.js에 자동 추가 (기존 시스템과 완벽 호환)
3. content/ 폴더에 txt 백업 저장
4. 매일 자동 실행 가능 (작업 스케줄러 / GitHub Actions)
"""

import os
import sys
import json
import random
import re
from datetime import datetime
from pathlib import Path

# ============================================================
# 설정
# ============================================================

# API 키 — 아래 3가지 방법 중 하나로 설정
# 방법1: 환경변수 (권장) → set GEMINI_API_KEY=여기에키
# 방법2: 이 파일에 직접 입력
# 방법3: config.json 파일에서 읽기
API_KEY = os.environ.get('GEMINI_API_KEY', '')

# API 키가 환경변수에 없으면 config.json에서 시도
if not API_KEY:
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            API_KEY = cfg.get('gemini_api_key', '')

# 경로 설정 (이 스크립트가 wocs-site 폴더와 같은 위치에 있다고 가정)
SCRIPT_DIR = Path(__file__).parent
BLOG_DATA_JS = SCRIPT_DIR / 'wocs-site' / 'assets' / 'js' / 'blog-data.js'
CONTENT_DIR = SCRIPT_DIR / 'content'

# blog-data.js가 없으면 다른 경로 시도
if not BLOG_DATA_JS.exists():
    BLOG_DATA_JS = SCRIPT_DIR / 'assets' / 'js' / 'blog-data.js'
if not BLOG_DATA_JS.exists():
    # 현재 폴더 기준
    BLOG_DATA_JS = Path('wocs-site/assets/js/blog-data.js')

CONTENT_DIR.mkdir(exist_ok=True)

# ============================================================
# SEO 타겟 키워드 30개 + 제목 템플릿
# ============================================================

TOPICS = [
    {"keyword": "글램핑 시공 단가", "title_hint": "2026년 글램핑 시공 단가 총정리 — 업체가 안 알려주는 원가 구조"},
    {"keyword": "글램핑장 인허가", "title_hint": "글램핑장 인허가 절차 완벽 가이드 — 야영장업 등록 A to Z"},
    {"keyword": "겨울 글램핑 난방", "title_hint": "겨울 글램핑 난방 해결법 — 영하 20도에서도 실내 20도 유지하는 비밀"},
    {"keyword": "풀빌라 글램핑 수익률", "title_hint": "풀빌라형 글램핑 투자 수익률 — 실제 숫자로 검증하는 ROI 분석"},
    {"keyword": "글램핑 창업 비용", "title_hint": "글램핑 창업 비용 얼마면 될까? 5천만 원부터 시작하는 현실적 가이드"},
    {"keyword": "글램핑 텐트 종류", "title_hint": "글램핑 텐트 종류 완전 비교 — 사파리 vs 돔 vs 코쿤, 뭘 골라야 할까"},
    {"keyword": "글램핑장 부지 선정", "title_hint": "글램핑장 부지 고르기 — 계약 전 반드시 확인할 7가지 함정"},
    {"keyword": "글램핑 에어비앤비", "title_hint": "글램핑 에어비앤비로 월 500만 원 버는 구조 — 1인 무인 운영 시스템"},
    {"keyword": "모듈러 글램핑", "title_hint": "모듈러 글램핑이란? 레고처럼 조립하는 차세대 시공 방식"},
    {"keyword": "글램핑 데크 시공", "title_hint": "글램핑 데크 시공 — 콘크리트 기초 없이 토목비 50% 절감하는 법"},
    {"keyword": "글램핑장 마케팅", "title_hint": "글램핑장 마케팅 전략 — 오픈 3개월 만에 예약률 80% 달성한 비결"},
    {"keyword": "글램핑 프레임 소재", "title_hint": "글램핑 프레임 알루미늄 vs 스틸 — 16년 현장 전문가의 최종 결론"},
    {"keyword": "글램핑 화장실 설치", "title_hint": "글램핑 화장실·욕실 — 프리팹 모듈로 호텔급 시설을 만드는 법"},
    {"keyword": "글램핑 조경 설계", "title_hint": "글램핑 조경이 객단가를 결정한다 — 사계절 포토존 만드는 조경 전략"},
    {"keyword": "글램핑 운영 노하우", "title_hint": "글램핑장 1인 운영 노하우 — 무인 체크인부터 청소 자동화까지"},
    {"keyword": "글램핑 수익 공유", "title_hint": "땅은 있고 돈은 없다? 글램핑 수익 공유 파트너십이라는 해법"},
    {"keyword": "글램핑 정부 보조금", "title_hint": "2026년 글램핑 정부 보조금 총정리 — 최대 9,600만 원 받는 법"},
    {"keyword": "글램핑 PVC 캔버스", "title_hint": "글램핑 PVC vs 캔버스 — 커버 소재 선택이 수명과 비용을 좌우한다"},
    {"keyword": "글램핑 단열", "title_hint": "글램핑 단열의 과학 — 4겹 구조가 영하 20도를 이기는 원리"},
    {"keyword": "글램핑 태풍 안전", "title_hint": "글램핑 태풍 안전 — 풍속 160km/h를 견디는 구조 설계의 비밀"},
    {"keyword": "글램핑 리조트 기획", "title_hint": "글램핑 리조트 기획 전략 — 8동 이상 하이엔드 마스터플랜"},
    {"keyword": "글램핑 B2B 납품", "title_hint": "지자체·리조트 B2B 글램핑 납품 — 국내 공장 다이렉트로 30% 절감"},
    {"keyword": "글램핑 전기 인입", "title_hint": "글램핑장 전기 인입 비용 — 전봇대 거리가 돈을 결정한다"},
    {"keyword": "에코 글램핑", "title_hint": "에코 글램핑 트렌드 — 친환경 구조물로 MZ세대 공략하는 법"},
    {"keyword": "글램핑 복층 텐트", "title_hint": "복층 글램핑 텐트 — 1층 거실+2층 침실, 객단가 50만 원의 비밀"},
    {"keyword": "글램핑 스마트락", "title_hint": "글램핑 무인 운영 시스템 — 스마트락·IoT·CCTV 완전 가이드"},
    {"keyword": "글램핑 용접 단점", "title_hint": "글램핑 프레임 용접의 치명적 단점 3가지 — 무용접이 답인 이유"},
    {"keyword": "글램핑 객단가 높이기", "title_hint": "글램핑 객단가 올리는 5가지 방법 — 같은 텐트로 2배 더 받는 전략"},
    {"keyword": "관광농원 글램핑", "title_hint": "관광농원 + 글램핑 복합 모델 — 농촌에서 연 매출 5억 만드는 구조"},
    {"keyword": "글램핑 A/S 관리", "title_hint": "글램핑 유지보수 완전 가이드 — 프레임 15년, 커버 5년 쓰는 관리법"},
]

# ============================================================
# 시스템 프롬프트 (세일즈 DNA)
# ============================================================

SYSTEM_PROMPT = """당신은 WOCS(우성어닝천막캠프시스템)의 대표이자 16년 현장 시공 경력의 글램핑/어닝 전문가입니다.

## 절대 규칙
1. 인터넷에 널린 뻔한 소리, 추상적 조언 금지. 반드시 숫자와 구체적 사례로 말할 것.
2. 모든 글에 WOCS의 핵심 차별점을 자연스럽게 녹일 것:
   - 국내 자체 공장 직영 생산 → 중간 유통 마진 제거 → 타사 대비 30% 원가 절감
   - 무용접 다방향 유니버설 조인트 (직접 출원 특허) → 풍속 160km/h, 내구성 2배, 공기 절반
   - 1동당 최소 80평(264㎡) 황금비율 배치 → 밀집 배치 거부 → 객단가 2~3배 상승
   - 화순 O4O 쇼룸 방문 시 Fusion 360 기반 3D 가설계 무료 제공
3. 단호하고 자신감 있는 톤. "~인 것 같습니다" 같은 애매한 표현 금지.

## 글 구조 (반드시 이 순서)
1. [도발적 질문 또는 충격적 팩트로 시작] — 독자의 고정관념을 깨는 오프닝
2. [문제의 원인 분석] — 왜 대부분 실패하는지, 업계의 구조적 문제점
3. [WOCS의 해결책] — 특허 기술, 원가 구조, 배치 전략으로 문제 해결
4. [구체적 숫자와 비교] — 투자비, 수익률, 회수 기간 등 실제 데이터
5. [CTA] — "화순 쇼룸 방문 예약" 또는 "자동 견적 계산기 이용" 유도

## HTML 포맷
- <h2>로 소제목 (3~4개)
- <p>로 본문 단락
- <strong>으로 핵심 강조 (골드색으로 표시됨)
- <blockquote>로 핵심 인용/요약
- <ul><li>로 리스트
- <a href="../contact/index.html">화순 쇼룸 방문 예약</a> 형태로 CTA 링크
- 전체 분량: 1,500~2,500자 (한글 기준)
"""

# ============================================================
# Gemini API 호출
# ============================================================

def call_gemini(prompt, system=SYSTEM_PROMPT):
    """Gemini 1.5 Flash API 호출"""
    import urllib.request
    import urllib.error

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        print(f"❌ API 에러 {e.code}: {error_body[:300]}")
        return None
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return None


def call_openai(prompt, system=SYSTEM_PROMPT):
    """OpenAI API 대안 (OPENAI_API_KEY 환경변수 필요)"""
    import urllib.request

    key = os.environ.get('OPENAI_API_KEY', '')
    if not key:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    })

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ OpenAI 요청 실패: {e}")
        return None


def generate_content(topic):
    """AI로 블로그 글 생성"""
    prompt = f"""아래 주제로 WOCS 블로그 글을 작성해주세요.

주제: {topic['title_hint']}
SEO 타겟 키워드: {topic['keyword']}

요구사항:
1. 제목은 SEO 키워드를 포함하되, 클릭하고 싶게 작성
2. 본문은 HTML 태그(<h2>, <p>, <strong>, <blockquote>, <ul><li>) 사용
3. 반드시 WOCS의 차별점(국내 공장 직영 30% 절감, 무용접 특허, 80평 황금비율, 화순 쇼룸)을 자연스럽게 녹일 것
4. 마지막에 화순 쇼룸 방문 또는 자동 견적 계산기 CTA 포함
5. 분량: 1,500~2,500자

출력 형식 (정확히 이 형식으로):
---TITLE---
글 제목
---EXCERPT---
2~3줄 요약
---CONTENT---
HTML 본문
"""

    # Gemini 우선, 실패하면 OpenAI 시도
    result = call_gemini(prompt)
    if not result:
        print("⚠ Gemini 실패, OpenAI 시도...")
        result = call_openai(prompt)

    return result


# ============================================================
# 파싱 & 저장
# ============================================================

def parse_ai_output(raw_text):
    """AI 출력을 제목/요약/본문으로 파싱"""
    title = excerpt = content = ""

    # ---TITLE--- 파싱
    m = re.search(r'---TITLE---\s*\n(.+?)(?:\n---|\Z)', raw_text, re.DOTALL)
    if m:
        title = m.group(1).strip()

    # ---EXCERPT--- 파싱
    m = re.search(r'---EXCERPT---\s*\n(.+?)(?:\n---|\Z)', raw_text, re.DOTALL)
    if m:
        excerpt = m.group(1).strip()

    # ---CONTENT--- 파싱
    m = re.search(r'---CONTENT---\s*\n(.+)', raw_text, re.DOTALL)
    if m:
        content = m.group(1).strip()
        # 마크다운 코드블록 제거
        content = re.sub(r'^```html?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

    return title, excerpt, content


def get_next_id():
    """blog-data.js에서 현재 최대 id를 찾아 +1 반환"""
    if not BLOG_DATA_JS.exists():
        return 100  # 기존 1~10과 충돌 방지

    text = BLOG_DATA_JS.read_text(encoding='utf-8')
    ids = [int(x) for x in re.findall(r'\bid:\s*(\d+)', text)]
    return max(ids) + 1 if ids else 100


def get_used_topics():
    """이미 사용된 토픽 키워드 확인"""
    used = set()
    if BLOG_DATA_JS.exists():
        text = BLOG_DATA_JS.read_text(encoding='utf-8')
        for t in TOPICS:
            if t['keyword'] in text or t['title_hint'][:20] in text:
                used.add(t['keyword'])

    # content/ 폴더의 txt 파일도 확인
    for f in CONTENT_DIR.glob('auto_post_*.txt'):
        txt = f.read_text(encoding='utf-8')
        for t in TOPICS:
            if t['keyword'] in txt:
                used.add(t['keyword'])

    return used


def pick_topic():
    """아직 안 쓴 주제 하나 선택"""
    used = get_used_topics()
    available = [t for t in TOPICS if t['keyword'] not in used]

    if not available:
        print("⚠ 모든 주제를 소진했습니다. 전체 리스트에서 랜덤 선택합니다.")
        available = TOPICS

    return random.choice(available)


def save_to_blog_data_js(post_id, title, excerpt, content, topic, image):
    """blog-data.js에 새 포스트 추가"""
    if not BLOG_DATA_JS.exists():
        print(f"⚠ {BLOG_DATA_JS} 파일을 찾을 수 없습니다. txt 백업만 저장합니다.")
        return False

    today = datetime.now().strftime('%Y-%m-%d')

    # content 내 따옴표 이스케이프
    safe_content = content.replace("'", "\\'").replace("\n", "\\n")
    safe_title = title.replace("'", "\\'")
    safe_excerpt = excerpt.replace("'", "\\'")

    new_entry = f"""{{
  id:{post_id}, title:'{safe_title}',
  date:'{today}', category:'{topic.get("category", "창업가이드")}', featured:false,
  image:'{image}',
  excerpt:'{safe_excerpt}',
  content:'{safe_content}'
}},
"""

    text = BLOG_DATA_JS.read_text(encoding='utf-8')
    # 'var BLOG_POSTS = [' 다음에 삽입
    marker = 'var BLOG_POSTS = [\n'
    if marker in text:
        text = text.replace(marker, marker + new_entry)
        BLOG_DATA_JS.write_text(text, encoding='utf-8')
        print(f"✅ blog-data.js에 id:{post_id} 추가 완료")
        return True
    else:
        print("⚠ blog-data.js 형식 불일치. txt 백업만 저장합니다.")
        return False


def save_to_txt(post_id, title, excerpt, content, image):
    """content/ 폴더에 txt 백업 저장"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"auto_post_{today}_{post_id}.txt"
    filepath = CONTENT_DIR / filename

    txt = f"""{title}
{today}
{image}
---
{excerpt}
---
{content}
"""
    filepath.write_text(txt, encoding='utf-8')
    print(f"✅ {filepath} 저장 완료")
    return filepath


# ============================================================
# 이미지 매칭
# ============================================================

IMAGES = {
    "시공": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=500&fit=crop&q=85",
    "단가": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&h=500&fit=crop&q=85",
    "인허가": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&h=500&fit=crop&q=85",
    "겨울": "https://images.unsplash.com/photo-1517299321609-52687d1bc55a?w=800&h=500&fit=crop&q=85",
    "수익": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop&q=85",
    "부지": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop&q=85",
    "에어비앤비": "https://images.unsplash.com/photo-1499696010180-025ef6e1a8f9?w=800&h=500&fit=crop&q=85",
    "리조트": "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=500&fit=crop&q=85",
    "텐트": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=500&fit=crop&q=85",
    "조경": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800&h=500&fit=crop&q=85",
    "기술": "https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&h=500&fit=crop&q=85",
    "default": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=500&fit=crop&q=85",
}

CATEGORY_MAP = {
    "시공": "시공기술", "단가": "수익분석", "인허가": "인허가",
    "겨울": "시공기술", "수익": "수익분석", "부지": "창업가이드",
    "에어비앤비": "사례", "리조트": "사례", "텐트": "시공기술",
    "조경": "창업가이드", "기술": "시공기술", "마케팅": "창업가이드",
    "창업": "창업가이드", "운영": "창업가이드", "정부": "수익분석",
    "A/S": "시공기술", "관리": "시공기술",
}


def match_image(keyword):
    for key, url in IMAGES.items():
        if key in keyword:
            return url
    return IMAGES["default"]


def match_category(keyword):
    for key, cat in CATEGORY_MAP.items():
        if key in keyword:
            return cat
    return "창업가이드"


# ============================================================
# 메인 실행
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='WOCS AI 블로그 자동 작성기')
    parser.add_argument('--topic', type=str, help='직접 주제 지정 (예: "글램핑 시공 단가")')
    parser.add_argument('--dry-run', action='store_true', help='API 호출 없이 주제 선정만 테스트')
    parser.add_argument('--count', type=int, default=1, help='생성할 글 수 (기본: 1)')
    args = parser.parse_args()

    # API 키 확인
    if not API_KEY and not args.dry_run:
        print("=" * 50)
        print("❌ API 키가 설정되지 않았습니다!")
        print()
        print("방법 1: 환경변수 설정")
        print("  Windows: set GEMINI_API_KEY=여기에키입력")
        print("  Mac/Linux: export GEMINI_API_KEY=여기에키입력")
        print()
        print("방법 2: config.json 파일 생성")
        print('  {"gemini_api_key": "여기에키입력"}')
        print()
        print("Gemini API 키 발급: https://aistudio.google.com/apikey")
        print("=" * 50)
        sys.exit(1)

    for i in range(args.count):
        print(f"\n{'='*50}")
        print(f"📝 글 {i+1}/{args.count} 생성 시작")
        print(f"{'='*50}")

        # 1. 주제 선정
        if args.topic:
            topic = {"keyword": args.topic, "title_hint": args.topic}
        else:
            topic = pick_topic()

        topic["category"] = match_category(topic["keyword"])
        image = match_image(topic["keyword"])
        post_id = get_next_id() + i

        print(f"📌 주제: {topic['title_hint']}")
        print(f"🏷  키워드: {topic['keyword']}")
        print(f"📂 카테고리: {topic['category']}")
        print(f"🆔 ID: {post_id}")

        if args.dry_run:
            print("🔸 --dry-run 모드: API 호출 생략")
            continue

        # 2. AI 글 생성
        print("🤖 AI 글 생성 중...")
        raw = generate_content(topic)
        if not raw:
            print("❌ AI 응답 없음. 스킵합니다.")
            continue

        # 3. 파싱
        title, excerpt, content = parse_ai_output(raw)
        if not title or not content:
            print("⚠ 파싱 실패. 원본을 txt로 저장합니다.")
            save_to_txt(post_id, topic['title_hint'], topic['keyword'], raw, image)
            continue

        print(f"✍  제목: {title}")
        print(f"📄 본문: {len(content)}자")

        # 4. 저장
        save_to_blog_data_js(post_id, title, excerpt, content, topic, image)
        save_to_txt(post_id, title, excerpt, content, image)

    print(f"\n{'='*50}")
    print("🎉 완료!")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
