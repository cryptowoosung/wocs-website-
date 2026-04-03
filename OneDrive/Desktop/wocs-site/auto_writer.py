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
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            API_KEY = cfg.get('gemini_api_key', '')

# 경로 설정 (이 스크립트가 wocs-site 폴더와 같은 위치에 있다고 가정)
SCRIPT_DIR = Path(__file__).parent
CONTENT_DIR = SCRIPT_DIR / 'content'

# blog-data.js 경로: 스크립트가 wocs-site 루트에 있으므로 assets/ 직접 참조
BLOG_DATA_JS = SCRIPT_DIR / 'assets' / 'js' / 'blog-data.js'
if not BLOG_DATA_JS.exists():
    BLOG_DATA_JS = SCRIPT_DIR / 'wocs-site' / 'assets' / 'js' / 'blog-data.js'
if not BLOG_DATA_JS.exists():
    BLOG_DATA_JS = Path('assets/js/blog-data.js')

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

## SEO 키워드 배치 규칙 (필수)
1. 제목(H1)에 타겟 키워드를 반드시 포함
2. 첫 문단 100자 이내에 타겟 키워드를 자연스럽게 1회 포함
3. H2 소제목 중 최소 1개에 타겟 키워드 또는 변형 키워드 포함
4. 키워드 밀도는 본문 전체의 1~2% 수준 유지 (과도한 반복 금지)

## 검색 의도별 글 구조
키워드의 검색 의도를 판단하여 구조를 선택할 것:

### A. 정보성 키워드 (설치, 방법, 종류, 비교, 가이드)
1. [도발적 질문/충격적 팩트] — 독자의 고정관념을 깨는 오프닝
2. [단계별 설명] — Step 1, Step 2... 또는 항목별 상세 설명
3. [WOCS의 전문가 팁] — 16년 현장 경험에서 나온 실전 조언
4. [비교표 또는 체크리스트] — 한눈에 보는 정리
5. [내부링크 + CTA] — 관련 글 연결 + 상담 유도

### B. 상업성 키워드 (견적, 비용, 단가, 업체, 가격)
1. [시장 현실 폭로] — "대부분의 견적서에 숨겨진 함정"
2. [비교표] — WOCS vs 일반업체 원가 구조 비교 (HTML <table> 사용)
3. [WOCS 원가 절감 구조] — 왜 30% 저렴한지 근거 제시
4. [실제 사례/숫자] — 투자비, 수익률, 회수 기간
5. [강력한 CTA] — 견적 요청/쇼룸 방문 유도

## 내부링크 슬롯 (필수 2개)
본문 중간과 후반에 아래 플레이스홀더를 자연스러운 문맥 속에 삽입:
- [INTERNAL_LINK_1] — 본문 중간 (관련 주제 연결)
- [INTERNAL_LINK_2] — 본문 후반 (심화 주제 연결)
예시: "자세한 내용은 [INTERNAL_LINK_1]에서 확인하실 수 있습니다."

## 본문 마무리 (필수)
글의 마지막 단락에 다음 정보를 자연스러운 문장으로 포함:
- 상호: WOCS (우성어닝천막공사캠프시스템)
- 전화: 010-4337-0582
- 웹사이트: wocs.kr
- 위치: 전남 화순군 (쇼룸)
예시: "WOCS(우성어닝천막공사캠프시스템)는 전남 화순에서 16년간 글램핑 구조물을 직접 제조·시공해왔습니다. 무료 상담은 010-4337-0582 또는 wocs.kr에서 신청하실 수 있습니다."

## HTML 포맷
- <h2>로 소제목 (3~4개, 최소 1개에 키워드 포함)
- <p>로 본문 단락
- <strong>으로 핵심 강조 (골드색으로 표시됨)
- <blockquote>로 핵심 인용/요약
- <ul><li>로 리스트
- <table>로 비교표 (상업성 키워드 시)
- <a href="../contact/index.html">화순 쇼룸 방문 예약</a> 형태로 CTA 링크
- 전체 분량: 1,500~2,500자 (한글 기준)
"""

# ============================================================
# 내부링크 매핑 (키워드 → 관련 페이지)
# ============================================================

INTERNAL_LINKS = {
    "시공": ('<a href="https://wocs.kr/resources/blog-post.html?id=4">무용접 특허 조인트 기술 상세 보기</a>',
             '<a href="https://wocs.kr/resources/blog-post.html?id=10">프레임·캔버스 관리 노하우</a>'),
    "비용": ('<a href="https://wocs.kr/resources/blog-post.html?id=5">객단가 3배 높이는 80평 황금비율</a>',
             '<a href="https://wocs.kr/contact/quote.html">무료 견적 요청하기</a>'),
    "단가": ('<a href="https://wocs.kr/resources/blog-post.html?id=5">객단가 3배 높이는 80평 황금비율</a>',
             '<a href="https://wocs.kr/contact/quote.html">무료 견적 요청하기</a>'),
    "창업": ('<a href="https://wocs.kr/resources/blog-post.html?id=6">야영장 인허가 체크리스트</a>',
             '<a href="https://wocs.kr/resources/blog-post.html?id=8">수익 공유 파트너십</a>'),
    "텐트": ('<a href="https://wocs.kr/resources/blog-post.html?id=4">무용접 특허 조인트 기술</a>',
             '<a href="https://wocs.kr/resources/blog-post.html?id=10">텐트 수명 15년 관리법</a>'),
    "수익": ('<a href="https://wocs.kr/resources/blog-post.html?id=5">80평 황금비율 수익 구조</a>',
             '<a href="https://wocs.kr/resources/blog-post.html?id=9">B2B 대단지 기획 전략</a>'),
    "인허가": ('<a href="https://wocs.kr/resources/blog-post.html?id=7">화순 쇼룸 3D 가설계</a>',
              '<a href="https://wocs.kr/contact/index.html">인허가 무료 상담 신청</a>'),
    "default": ('<a href="https://wocs.kr/resources/blog.html">WOCS 블로그 전체 보기</a>',
                '<a href="https://wocs.kr/contact/quote.html">무료 견적 요청하기</a>'),
}


def resolve_internal_links(content, keyword):
    """[INTERNAL_LINK_1], [INTERNAL_LINK_2] 플레이스홀더를 실제 링크로 치환"""
    link1, link2 = INTERNAL_LINKS.get("default")
    for key, links in INTERNAL_LINKS.items():
        if key != "default" and key in keyword:
            link1, link2 = links
            break
    content = content.replace("[INTERNAL_LINK_1]", link1)
    content = content.replace("[INTERNAL_LINK_2]", link2)
    return content


# ============================================================
# JSON-LD Schema Markup 자동 생성
# ============================================================

WOCS_LOCAL_BUSINESS = {
    "@type": "LocalBusiness",
    "name": "WOCS (우성어닝천막공사캠프시스템)",
    "telephone": "010-4337-0582",
    "email": "info@wocs.kr",
    "url": "https://wocs.kr",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "화순군",
        "addressRegion": "전남",
        "addressCountry": "KR",
        "streetAddress": "사평면 유마로 592"
    },
    "priceRange": "₩₩₩",
    "image": "https://wocs.kr/assets/images/og-image.jpg"
}

# 키워드 → schema 유형 매핑
SCHEMA_TYPE_KEYWORDS = {
    "HowTo": ["설치", "방법", "시공", "만드는", "절차", "가이드", "관리"],
    "Product": ["텐트", "프레임", "소재", "PVC", "캔버스", "조인트", "모듈러", "데크"],
    "Review": ["비교", "수익률", "단점", "장점", "vs", "리뷰"],
}


def detect_schema_type(keyword, title):
    """키워드+제목 분석하여 적절한 schema 유형 반환"""
    text = f"{keyword} {title}".lower()
    for schema_type, triggers in SCHEMA_TYPE_KEYWORDS.items():
        if any(t in text for t in triggers):
            return schema_type
    return "Article"


def generate_schema_markup(title, excerpt, keyword, image, post_date):
    """JSON-LD 구조화 데이터 생성"""
    schema_type = detect_schema_type(keyword, title)

    # 기본 Article 스키마
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            WOCS_LOCAL_BUSINESS,
            {
                "@type": schema_type if schema_type != "Article" else "BlogPosting",
                "headline": title,
                "description": excerpt[:120],
                "image": image,
                "datePublished": post_date,
                "dateModified": post_date,
                "author": {
                    "@type": "Person",
                    "name": "김우성",
                    "jobTitle": "WOCS 대표",
                    "url": "https://wocs.kr"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "WOCS",
                    "url": "https://wocs.kr"
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": f"https://wocs.kr/resources/blog-post.html?id={{post_id}}"
                },
                "keywords": keyword
            }
        ]
    }

    # HowTo 추가 필드
    if schema_type == "HowTo":
        schema["@graph"][1]["supply"] = [{"@type": "HowToSupply", "name": "글램핑 구조물 자재"}]
        schema["@graph"][1]["tool"] = [{"@type": "HowToTool", "name": "WOCS 무용접 조인트 시스템"}]

    # Product 추가 필드
    if schema_type == "Product":
        schema["@graph"][1]["brand"] = {"@type": "Brand", "name": "WOCS"}
        schema["@graph"][1]["manufacturer"] = {"@type": "Organization", "name": "WOCS (우성어닝천막공사캠프시스템)"}
        schema["@graph"][1]["offers"] = {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "KRW",
            "priceValidUntil": "2026-12-31",
            "availability": "https://schema.org/InStock",
            "url": "https://wocs.kr/contact",
            "description": "견적 문의",
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {
                    "@type": "MonetaryAmount",
                    "value": "0",
                    "currency": "KRW"
                },
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {
                        "@type": "QuantitativeValue",
                        "minValue": 1,
                        "maxValue": 3,
                        "unitCode": "DAY"
                    }
                }
            },
            "hasMerchantReturnPolicy": {
                "@type": "MerchantReturnPolicy",
                "applicableCountry": "KR",
                "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted"
            }
        }

    return schema

# ============================================================
# Gemini API 호출
# ============================================================

def call_gemini(prompt, system=SYSTEM_PROMPT):
    """Gemini 2.5 Flash API 호출"""
    import urllib.request
    import urllib.error

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})

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


def detect_search_intent(keyword):
    """키워드의 검색 의도 판별: informational / commercial"""
    commercial = ["견적", "비용", "단가", "가격", "업체", "수익", "투자", "보조금"]
    if any(w in keyword for w in commercial):
        return "commercial"
    return "informational"


def generate_content(topic):
    """AI로 블로그 글 생성"""
    intent = detect_search_intent(topic['keyword'])
    intent_guide = ""
    if intent == "commercial":
        intent_guide = """이 키워드는 상업성(구매 의도) 키워드입니다.
→ 비교표(<table>)를 반드시 포함하고, 강력한 CTA로 마무리하세요.
→ 구조: 시장 현실 폭로 → 비교표 → WOCS 원가 절감 → 실제 사례 → CTA"""
    else:
        intent_guide = """이 키워드는 정보성 키워드입니다.
→ 단계별 설명 또는 항목별 상세 비교로 구성하세요.
→ 구조: 도발적 오프닝 → 단계별/항목별 설명 → 전문가 팁 → 정리 → CTA"""

    prompt = f"""아래 주제로 WOCS 블로그 글을 작성해주세요.

주제: {topic['title_hint']}
SEO 타겟 키워드: {topic['keyword']}
검색 의도: {intent}

{intent_guide}

SEO 필수 규칙:
1. 제목(H1)에 "{topic['keyword']}" 키워드를 반드시 포함
2. 첫 문단 100자 이내에 "{topic['keyword']}" 자연스럽게 1회 포함
3. H2 소제목 중 최소 1개에 "{topic['keyword']}" 또는 변형 키워드 포함
4. 본문 중간에 [INTERNAL_LINK_1], 후반에 [INTERNAL_LINK_2] 플레이스홀더 삽입
5. 마지막 단락에 WOCS 상호/전화/웹사이트 정보 자연스럽게 포함
6. WOCS 차별점(공장 직영 30% 절감, 무용접 특허, 80평 황금비율, 화순 쇼룸) 녹일 것
7. 분량: 1,500~2,500자

출력 형식 (정확히 이 형식, 순서 지켜주세요):
---TITLE---
글 제목 (키워드 포함, 클릭 유도)
---META_DESC---
메타디스크립션 (120자 이내, 키워드 포함, 클릭 유도 문구)
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
    """AI 출력을 제목/메타디스크립션/요약/본문으로 파싱"""
    title = meta_desc = excerpt = content = ""

    # ---TITLE--- 파싱
    m = re.search(r'---TITLE---\s*\n(.+?)(?:\n---|\Z)', raw_text, re.DOTALL)
    if m:
        title = m.group(1).strip()

    # ---META_DESC--- 파싱
    m = re.search(r'---META_DESC---\s*\n(.+?)(?:\n---|\Z)', raw_text, re.DOTALL)
    if m:
        meta_desc = m.group(1).strip()[:120]

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

    # meta_desc가 없으면 excerpt에서 생성
    if not meta_desc and excerpt:
        meta_desc = excerpt[:120]

    return title, meta_desc, excerpt, content


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


def save_to_txt(post_id, title, meta_desc, excerpt, content, keyword, image, schema):
    """content/ 폴더에 txt 백업 저장 (schema markup 포함)"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"auto_post_{today}_{post_id}.txt"
    filepath = CONTENT_DIR / filename

    # schema의 post_id 플레이스홀더 치환
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    schema_str = schema_str.replace("{post_id}", str(post_id))

    txt = f"""{title}
{today}
{image}
---META_DESC---
{meta_desc}
---EXCERPT---
{excerpt}
---KEYWORD---
{keyword}
---CONTENT---
{content}
---SCHEMA---
<script type="application/ld+json">
{schema_str}
</script>
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
        title, meta_desc, excerpt, content = parse_ai_output(raw)
        if not title or not content:
            print("⚠ 파싱 실패. 원본을 txt로 저장합니다.")
            save_to_txt(post_id, topic['title_hint'], "", topic['keyword'], raw,
                        topic['keyword'], image, {})
            continue

        # 4. 내부링크 치환
        content = resolve_internal_links(content, topic['keyword'])

        # 5. Schema Markup 생성
        today = datetime.now().strftime('%Y-%m-%d')
        schema = generate_schema_markup(title, excerpt, topic['keyword'], image, today)
        schema_type = detect_schema_type(topic['keyword'], title)

        print(f"✍  제목: {title}")
        print(f"📝 메타: {meta_desc}")
        print(f"📄 본문: {len(content)}자")
        print(f"🔗 Schema: {schema_type}")

        # 6. 저장
        save_to_blog_data_js(post_id, title, excerpt, content, topic, image)
        save_to_txt(post_id, title, meta_desc, excerpt, content,
                    topic['keyword'], image, schema)

    print(f"\n{'='*50}")
    print("🎉 완료!")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
