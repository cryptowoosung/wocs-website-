#!/usr/bin/env python3
import os, json, random, re, time
from datetime import datetime, timedelta
# google-genai는 기존 Gemini 모드에서만 필요 → webhook 모드는 표준 라이브러리만 사용

# ─── 재시도 설정 (Gemini 503/UNAVAILABLE 대응) ───
RETRY_ATTEMPTS = 5
RETRY_BASE_DELAY = 15  # 초, 지수 백오프 시작값
RETRYABLE_STATUS = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL", "504", "DEADLINE_EXCEEDED")


def gemini_generate_with_retry(prompt, label="generate"):
    """Gemini API 호출을 지수 백오프로 재시도한다. 5회 모두 실패하면 None 반환."""
    last_err = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            if attempt > 1:
                print("[retry] " + label + " 성공 (attempt " + str(attempt) + ")")
            return response.text
        except Exception as e:
            last_err = e
            err_str = str(e)
            is_retryable = any(code in err_str for code in RETRYABLE_STATUS)
            if not is_retryable or attempt == RETRY_ATTEMPTS:
                print("오류(" + label + "): " + err_str)
                return None
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            print("[retry " + str(attempt) + "/" + str(RETRY_ATTEMPTS - 1) + "] " + label + " 일시 장애 — " + str(delay) + "초 후 재시도: " + err_str[:120])
            time.sleep(delay)
    print("오류(" + label + "): 재시도 모두 실패 — " + str(last_err))
    return None

API_KEY = os.environ.get("GEMINI_API_KEY") or ""
if not API_KEY:
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            API_KEY = json.load(f).get("gemini_api_key", "")
    except:
        pass

MODEL = "gemini-2.5-flash"

# webhook 모드: N8N_PAYLOAD 환경 변수가 있으면 외부 입력으로 발행 (Gemini 미사용)
_WEBHOOK_MODE = bool(os.environ.get("N8N_PAYLOAD"))
client = None

if not _WEBHOOK_MODE:
    if not API_KEY:
        print("GEMINI_API_KEY 없음")
        exit(1)
    from google import genai  # 기존 모드에서만 import (webhook 모드는 의존성 없음)
    client = genai.Client(api_key=API_KEY)
    print("Gemini 연결됨 (" + MODEL + ")")

# ─── TOPICS: 지역명 타겟팅 통합 ───
TOPICS = [
    # ── 창업가이드 + 지역 타겟 ──
    {"keyword": "글램핑 창업", "region": "광주", "long_tail": "광주 글램핑 창업 비용 절차 완전정복", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "화순", "long_tail": "화순 글램핑 창업 토지 선정부터 시공까지", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "나주", "long_tail": "나주 글램핑 창업 허가 절차 2026 최신판", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "담양", "long_tail": "담양 글램핑 창업 대나무숲 인근 부지 선정법", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "순천", "long_tail": "순천 글램핑 창업 생태관광 연계 수익 전략", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "여수", "long_tail": "여수 글램핑 창업 해변 인근 구조물 선택 기준", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "고흥", "long_tail": "고흥 글램핑 창업 우주센터 관광벨트 활용법", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "보성", "long_tail": "보성 글램핑 창업 차밭 뷰 프리미엄 입지 분석", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "광양", "long_tail": "광양 글램핑 창업 매화마을 인근 부지 수익성", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "구례", "long_tail": "구례 지리산 글램핑 창업 사계절 운영 전략", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "장흥", "long_tail": "장흥 글램핑 창업 편백숲 인근 입지 분석", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "강진", "long_tail": "강진 글램핑 창업 다산초당 관광 연계 전략", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "해남", "long_tail": "해남 땅끝 글램핑 창업 서울 원정객 유치 방법", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "완도", "long_tail": "완도 청산도 글램핑 창업 섬 여행 트렌드 공략", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "진도", "long_tail": "진도 울돌목 글램핑 창업 역사 관광 연계", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "무안", "long_tail": "무안 글램핑 창업 국제공항 접근성 입지 분석", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "함평", "long_tail": "함평 나비축제 글램핑 창업 계절 수익 전략", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "영광", "long_tail": "영광 굴비 특화 글램핑 창업 식도락 관광 연계", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "목포", "long_tail": "목포 글램핑 창업 다도해 뷰 구조물 선택 방법", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 창업", "region": "신안", "long_tail": "신안 퍼플섬 글램핑 창업 섬 관광 수요 분석", "category": "창업가이드", "cta_every": 4},
    # ── 제품정보 ──
    {"keyword": "사파리 글램핑 텐트", "region": "전남", "long_tail": "전남 사파리 글램핑 텐트 가격 스펙 비교", "category": "제품정보", "cta_every": 4},
    {"keyword": "돔 글램핑 텐트", "region": "광주", "long_tail": "광주 돔형 글램핑 텐트 설치비 포함 실제 비용", "category": "제품정보", "cta_every": 4},
    {"keyword": "글램핑 텐트 종류", "region": "전북", "long_tail": "전북 글램핑 텐트 종류별 장단점 완전 비교", "category": "제품정보", "cta_every": 4},
    {"keyword": "모듈러 글램핑 구조물", "region": "전남", "long_tail": "전남 모듈러 글램핑 조립식 구조물 시공 기간", "category": "제품정보", "cta_every": 4},
    # ── 시공정보 ──
    {"keyword": "글램핑 시공 업체", "region": "광주", "long_tail": "광주 글램핑 시공 업체 선택 기준 5가지", "category": "시공정보", "cta_every": 3},
    {"keyword": "글램핑 시공 업체", "region": "전남", "long_tail": "전남 글램핑 시공 전문 업체 비교 방법", "category": "시공정보", "cta_every": 3},
    {"keyword": "어닝 시공", "region": "광주", "long_tail": "광주 어닝 시공 비용 종류별 가격 2026", "category": "시공정보", "cta_every": 3},
    {"keyword": "천막 구조물", "region": "전남", "long_tail": "전남 천막 구조물 설계 KS 기준 허가 절차", "category": "시공정보", "cta_every": 3},
    {"keyword": "글램핑 단지 조성", "region": "전남북", "long_tail": "전남북 글램핑 단지 조성 토지 선정부터 완공", "category": "시공정보", "cta_every": 3},
    # ── 수익분석 ──
    {"keyword": "글램핑 수익", "region": "전남", "long_tail": "전남 글램핑 1동당 월 수익 현실 수치 공개", "category": "수익분석", "cta_every": 4},
    {"keyword": "글램핑 투자비 회수", "region": "광주", "long_tail": "광주 글램핑 투자비 회수 기간 손익분기점", "category": "수익분석", "cta_every": 4},
    # ── 정부/공모 ──
    {"keyword": "글램핑 공모사업", "region": "전남", "long_tail": "2026 전남 지자체 글램핑 공모사업 신청 방법", "category": "창업가이드", "cta_every": 4},
    {"keyword": "글램핑 공모사업", "region": "전북", "long_tail": "2026 전북 글램핑 관광단지 공모 지원 조건", "category": "창업가이드", "cta_every": 4},
    # ── WOCS 브랜드 ──
    {"keyword": "WOCS 글램핑", "region": "화순", "long_tail": "화순 WOCS 특허 무용접 유니버설 조인트 장점", "category": "브랜드", "cta_every": 2},
]

CATEGORY_MAP = {
    "창업가이드": "cat_startup",
    "제품정보": "cat_construction",
    "시공정보": "cat_construction",
    "수익분석": "cat_revenue",
    "브랜드": "cat_case",
}

INTRO_TYPES = [
    "질문형: 독자가 공감할 현실적 고민으로 시작",
    "수치형: 구체적 숫자나 통계로 시작",
    "상황형: 전남권 실제 현장 상황 묘사로 시작",
    "역설형: 상식을 뒤집는 주장으로 시작",
    "경험형: 16년 현장 경험에서 나온 관찰로 시작",
]

UNSPLASH_TAGS = {
    "글램핑": "glamping,tent",
    "사파리": "safari,tent,camping",
    "돔": "dome,tent,geodesic",
    "어닝": "awning,outdoor",
    "천막": "tent,canopy",
    "캠핑": "camping,nature",
    "모듈러": "modular,cabin",
    "수익": "business,profit",
    "공모": "government,document",
    "WOCS": "glamping,construction",
}

BLOG_DATA_PATH = "assets/js/blog-data.js"
CONTENT_DIR = "content"
USED_TOPICS_PATH = "used_topics.json"
CTA_COUNTER_PATH = "cta_counter.json"

CTA_TEXT = (
    "\n---\n"
    "글램핑 구조물 관련 문의는 전남 화순 기반의 WOCS(wocs.kr)에서\n"
    "현장 상담부터 시공까지 원스톱으로 진행합니다.\n"
)

# ─── SEO/AEO/GEO 상수 (Phase 5) ───
SITE_URL = "https://wocs.kr"
COMPANY_NAME = "우성어닝천막공사"
COMPANY_PHONE = "010-4337-0582"
COMPANY_ADDR = "전남 화순군 사평면 유마로 592"
COMPANY_LOGO = "https://wocs.kr/assets/images/logo_preview_dark.png"
AUTHOR_NAME = "김우성"
AUTHOR_TITLE = "WOCS 대표 · 16년 경력 어닝·천막·구조물 시공 전문가"
CATEGORY_LABELS = {
    "cat_startup": "창업가이드",
    "cat_construction": "시공정보",
    "cat_revenue": "수익분석",
    "cat_case": "시공사례",
}


# ─── 유틸리티 ───

def get_unsplash_image(keyword):
    tags = "glamping,tent"
    for k, v in UNSPLASH_TAGS.items():
        if k in keyword:
            tags = v
            break
    return "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800&h=500&fit=crop&q=85&" + tags


# ─── 중복 방지 (keyword+region, 60일) ───

def load_used_topics():
    try:
        with open(USED_TOPICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_used_topic(keyword, region):
    used = load_used_topics()
    key = keyword + "|" + region
    used[key] = datetime.now().strftime("%Y-%m-%d")
    with open(USED_TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def is_topic_available(topic):
    used = load_used_topics()
    key = topic["keyword"] + "|" + topic["region"]
    if key not in used:
        return True
    last_date = datetime.strptime(used[key], "%Y-%m-%d")
    return (datetime.now() - last_date) > timedelta(days=60)


def pick_topic():
    available = [t for t in TOPICS if is_topic_available(t)]
    if not available:
        available = TOPICS
    return random.choice(available)


# ─── CTA 순환 ───

def should_include_cta(topic):
    try:
        with open(CTA_COUNTER_PATH, "r", encoding="utf-8") as f:
            counter = json.load(f)
    except:
        counter = {"count": 0}
    counter["count"] = counter.get("count", 0) + 1
    with open(CTA_COUNTER_PATH, "w", encoding="utf-8") as f:
        json.dump(counter, f)
    return counter["count"] % topic.get("cta_every", 4) == 0


# ─── ID 생성 ───

def get_next_id():
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            ids = re.findall(r'id:(\d+)', f.read())
            return max([int(i) for i in ids], default=99) + 1
    except:
        return 100


# ─── AI 글 생성 ───

def generate_content(topic, cta_this_post):
    intro_style = random.choice(INTRO_TYPES)
    cta_instruction = (
        "6단락: wocs.kr 자연스럽게 언급 (CTA 아닌 정보 제공 형식으로)"
        if cta_this_post else
        "6단락: 독자에게 도움이 되는 추가 정보"
    )
    prompt = (
        "당신은 16년 경력의 글램핑 구조물 전문가 김우성입니다.\n"
        "전남 화순군에서 WOCS 브랜드로 사파리텐트·돔텐트·시그니처 구조물을 직접 제조·시공합니다.\n\n"
        "오늘 글 주제: " + topic["long_tail"] + "\n"
        "지역: " + topic["region"] + "\n"
        "타겟 독자: 글램핑 창업을 준비하거나 관심 있는 " + topic["region"] + " 지역 사람\n\n"
        "## 글쓰기 규칙 (반드시 준수)\n\n"
        "### 분량\n"
        "- 1600~2000자 (공백 제외)\n"
        "- 단락 5~6개\n\n"
        "### 저품질 방지 규칙 (이것을 어기면 안됨)\n"
        "- 제목과 내용이 반드시 일치할 것 (낚시성 제목 금지)\n"
        "- 광고·홍보 문구로 시작하지 말 것 (첫 문단은 반드시 정보성)\n"
        '- 키워드 남용 금지: "' + topic["keyword"] + '" 단어는 전체 글에서 최대 5회\n'
        '- 지역명 "' + topic["region"] + '"은 자연스럽게 3~5회 (억지로 반복 금지)\n'
        "- 매 단락 같은 패턴 반복 금지 (각 단락은 내용이 달라야 함)\n"
        "- 타 업체 비방 금지\n\n"
        "### 지역명 활용 방식 (핵심)\n"
        "다음 방식으로 지역을 자연스럽게 녹여라:\n"
        '- 부지 특성: "' + topic["region"] + ' 특유의 지형/기후/관광지 특성"과 연결\n'
        '- 실제 사례처럼: "전남 ' + topic["region"] + ' 지역에서 문의가 많은..."\n'
        '- 접근성: "광주·전남권에서 당일 방문 가능한..."\n'
        '- 주변 관광: "' + topic["region"] + ' 인근 주요 관광지와 연계한 글램핑 전략"\n'
        "전남/전북 주요 지역명을 자연스럽게 1~3개 추가 언급 가능\n\n"
        "### 구조 (단락별)\n"
        "1단락: 훅 — " + topic["region"] + " 또는 전남권 관련 구체적 상황/질문 (광고 아닌 현장 느낌)\n"
        "2단락: 핵심 정보 1 — 이 주제의 가장 중요한 실용 정보\n"
        "3단락: 핵심 정보 2 — 수치, 사례, 비교 중 하나 포함\n"
        "4단락: 전문가 시각 — 16년 경력에서 나온 현장 경험담\n"
        "5단락: 지역 특화 팁 — " + topic["region"] + " 또는 전남권 특성에 맞는 구체적 조언\n"
        + cta_instruction + "\n\n"
        "### 도입부 스타일: " + intro_style + "\n\n"
        "### 키워드 배치 (SEO)\n"
        "- 제목에 메인 키워드 포함\n"
        "- 첫 단락 100자 이내에 메인 키워드 1회\n"
        "- 중간 단락에 롱테일 키워드 1회\n"
        "- 지역명 자연스럽게 3~5회 분산\n\n"
        "### 절대 금지\n"
        '- "안녕하세요" "오늘은 ~에 대해 알아보겠습니다" 같은 판에 박힌 도입부\n'
        '- "무료 견적 받기" "지금 바로 문의" 같은 노골적 광고 문구\n'
        '- 같은 문장 구조 반복 ("~합니다. ~합니다. ~합니다.")\n'
        "- HTML 태그 없이 순수 텍스트만 출력\n\n"
        "제목(H1)과 본문만 출력. 설명이나 메타 정보는 출력하지 마시오.\n"
    )
    return gemini_generate_with_retry(prompt, label="blog-content")


def parse_content(raw):
    lines = raw.strip().split("\n")
    title = ""
    body_lines = []
    for line in lines:
        stripped = line.strip()
        if not title and stripped.startswith("# "):
            title = stripped.lstrip("# ").strip()
        elif not title and stripped and not stripped.startswith("#"):
            title = stripped
        else:
            body_lines.append(line)
    content = "\n".join(body_lines).strip()
    if not title and content:
        title = content.split("\n")[0][:50]
    return title, content


# ─── meta description 생성 ───

def generate_meta_description(topic, content):
    prompt = (
        "다음 글의 첫 두 문단을 읽고 '" + topic["keyword"] + "' 키워드와 '"
        + topic["region"] + "' 지역명이 포함된 80~120자 메타 디스크립션을 작성하세요. "
        "설명 없이 텍스트만 출력:\n\n" + content[:500]
    )
    raw = gemini_generate_with_retry(prompt, label="meta-desc")
    if not raw:
        return content[:100].replace("\n", " ")
    desc = raw.strip().replace('"', "'").replace("\n", " ")
    return desc[:150]


# ─── 저장: blog-data.js ───

def save_to_blog_data(post_id, title, content, topic, meta_desc, image_url=None,
                      is_html=False, extra=None):
    today = datetime.now().strftime("%Y-%m-%d")
    safe = lambda s: s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    if image_url is None:
        image_url = get_unsplash_image(topic["keyword"])
    cat_key = CATEGORY_MAP.get(topic["category"], "cat_startup")
    # is_html이면 excerpt/content 필드는 태그를 제거한 순수 텍스트로 저장 (목록 표시 일관성)
    if is_html:
        text_src = re.sub(r"<[^>]+>", " ", content)
        text_src = re.sub(r"\s+", " ", text_src).strip()
    else:
        text_src = content
    excerpt = text_src[:100].replace("\n", " ")
    # Phase 5: SEO/AEO/GEO 확장 필드 (extra 없으면 기존 동작)
    extra = extra or {}
    tldr = extra.get("tldr", "")
    faq = [q for q in (extra.get("faq") or []) if q.get("q") and q.get("a")]
    references = [r for r in (extra.get("references") or []) if r.get("name")]
    how_to = [str(s).strip() for s in (extra.get("how_to_steps") or [])
              if str(s).strip()]
    description = meta_desc or tldr
    # JS 안전 JSON 직렬화 (U+2028/2029는 JS에서 줄바꿈으로 취급되므로 이스케이프)
    jdump = lambda o: (json.dumps(o, ensure_ascii=False)
                       .replace(" ", "\\u2028").replace(" ", "\\u2029"))
    # 동적 페이지(blog-post.html)가 faq/references/how_to 전체 데이터를 렌더링하므로
    # count뿐 아니라 원본 배열도 저장. blog-data.js는 <script src>로 로드됨 → JSON 안전.
    new_entry = (
        '{\n'
        "  id:" + str(post_id) + ", title:'" + safe(title) + "', excerpt:'" + safe(excerpt) + "',\n"
        "  date:'" + today + "', category:'" + cat_key + "', featured:false,\n"
        "  image:'" + image_url + "',\n"
        "  description:'" + safe(description) + "',\n"
        "  tldr:'" + safe(tldr) + "', faq_count:" + str(len(faq))
        + ", has_how_to:" + ("true" if how_to else "false")
        + ", ref_count:" + str(len(references)) + ",\n"
        "  faq:" + jdump(faq) + ",\n"
        "  references:" + jdump(references) + ",\n"
        "  how_to:" + jdump(how_to) + ",\n"
        "  content:'" + safe(text_src[:3000]) + "'\n"
        '}'
    )
    with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
        data = f.read()
    # silent fail 방지: 앵커 존재 + 치환 적용 + 결과 검증을 모두 확인, 실패 시 예외 발생
    anchor = "var BLOG_POSTS = ["
    if anchor not in data:
        raise RuntimeError("blog-data.js 치환 실패: 앵커 '" + anchor + "'를 찾을 수 없음")
    new_data = data.replace(anchor, anchor + "\n" + new_entry + ",", 1)
    if new_data == data:
        raise RuntimeError("blog-data.js 치환 실패: 내용이 변경되지 않음 (silent fail 차단)")
    if ("id:" + str(post_id) + ",") not in new_data:
        raise RuntimeError("blog-data.js 치환 검증 실패: 새 항목(id:" + str(post_id) + ")이 결과에 없음")
    with open(BLOG_DATA_PATH, "w", encoding="utf-8") as f:
        f.write(new_data)
    print("blog-data.js 저장 완료 (id:" + str(post_id) + ")")


# ─── 저장: HTML ───

def markdown_to_html(text):
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            html_lines.append("<h3>" + stripped[4:] + "</h3>")
        elif stripped.startswith("## "):
            html_lines.append("<h2>" + stripped[3:] + "</h2>")
        elif stripped.startswith("# "):
            html_lines.append("<h2>" + stripped[2:] + "</h2>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_lines.append("<li>" + stripped[2:] + "</li>")
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_lines.append("<p><strong>" + stripped[2:-2] + "</strong></p>")
        else:
            bold = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            html_lines.append("<p>" + bold + "</p>")
    result = []
    in_list = False
    for line in html_lines:
        if line.startswith("<li>"):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(line)
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)
    if in_list:
        result.append("</ul>")
    return "\n".join(result)


# ─── SEO/AEO/GEO: JSON-LD 스키마 + 블록 렌더러 (Phase 5) ───

def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build_json_ld(title, url, image_url, meta_desc, cat_key, today,
                  focus_keyword, faq, references, how_to_steps):
    """schema.org @graph JSON-LD 생성 → <script> 블록 반환. faq/how_to는 있을 때만."""
    iso = today + "T09:00:00+09:00"
    cat_label = CATEGORY_LABELS.get(cat_key, "블로그")
    org_id = SITE_URL + "/#organization"
    author_id = SITE_URL + "/#author"
    address = {"@type": "PostalAddress", "addressCountry": "KR",
               "addressRegion": "전라남도", "streetAddress": COMPANY_ADDR}
    graph = [
        {
            "@type": "BlogPosting", "@id": url + "#article",
            "headline": title, "description": meta_desc, "image": image_url,
            "datePublished": iso, "dateModified": iso,
            "author": {"@id": author_id}, "publisher": {"@id": org_id},
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "keywords": focus_keyword, "articleSection": cat_label,
            "inLanguage": "ko-KR",
        },
        {
            "@type": "BreadcrumbList", "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "블로그",
                 "item": SITE_URL + "/blog"},
                {"@type": "ListItem", "position": 3, "name": cat_label},
                {"@type": "ListItem", "position": 4, "name": title},
            ],
        },
        {
            "@type": "Organization", "@id": org_id, "name": COMPANY_NAME,
            "url": SITE_URL, "telephone": COMPANY_PHONE, "address": address,
            "logo": {"@type": "ImageObject", "url": COMPANY_LOGO},
            "contactPoint": {"@type": "ContactPoint", "telephone": COMPANY_PHONE,
                             "contactType": "customer service", "areaServed": "KR"},
        },
        {
            "@type": "Person", "@id": author_id, "name": AUTHOR_NAME,
            "jobTitle": AUTHOR_TITLE, "worksFor": {"@id": org_id},
        },
        {
            "@type": "LocalBusiness", "@id": SITE_URL + "/#localbusiness",
            "name": COMPANY_NAME, "url": SITE_URL, "telephone": COMPANY_PHONE,
            "image": COMPANY_LOGO, "address": address, "priceRange": "₩₩",
        },
    ]
    valid_faq = [q for q in faq if q.get("q") and q.get("a")]
    if valid_faq:
        graph.append({
            "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
                for q in valid_faq
            ],
        })
    valid_steps = [s for s in how_to_steps if s]
    if valid_steps:
        graph.append({
            "@type": "HowTo", "@id": url + "#howto", "name": title,
            "step": [{"@type": "HowToStep", "position": i + 1, "text": s}
                     for i, s in enumerate(valid_steps)],
        })
    doc = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">\n'
            + json.dumps(doc, ensure_ascii=False, indent=2)
            + '\n</script>')


def render_tldr(tldr):
    if not tldr:
        return ""
    return ('  <div class="tldr">\n'
            '    <span class="tldr-label">핵심 요약 (TL;DR)</span>\n'
            '    <p>' + _esc(tldr) + '</p>\n  </div>\n')


def render_faq(faq):
    items = []
    for q in faq:
        qq, aa = q.get("q", ""), q.get("a", "")
        if qq and aa:
            items.append('    <details>\n      <summary>' + _esc(qq)
                         + '</summary>\n      <p>' + _esc(aa) + '</p>\n    </details>')
    if not items:
        return ""
    return ('  <section class="faq">\n    <h2>자주 묻는 질문</h2>\n'
            + "\n".join(items) + "\n  </section>\n")


def render_references(references):
    items = []
    for r in references:
        name = r.get("name", "")
        if not name:
            continue
        u = r.get("url", "")
        if u:
            items.append('      <li><a href="' + _esc(u)
                         + '" rel="nofollow noopener" target="_blank">'
                         + _esc(name) + '</a></li>')
        else:
            items.append('      <li>' + _esc(name) + '</li>')
    if not items:
        return ""
    return ('  <section class="references">\n    <h3>참고 자료</h3>\n    <ul>\n'
            + "\n".join(items) + '\n    </ul>\n  </section>\n')


def render_eeat(today):
    return ('  <div class="eeat">\n'
            '    <p><strong>' + _esc(AUTHOR_NAME) + '</strong> · '
            + _esc(AUTHOR_TITLE) + '</p>\n'
            '    <p>' + _esc(COMPANY_NAME) + ' · ' + _esc(COMPANY_ADDR)
            + ' · ' + _esc(COMPANY_PHONE) + '</p>\n'
            '    <p>최종 수정: <time datetime="' + today + '" itemprop="dateModified">'
            + today + '</time></p>\n  </div>\n')


def save_to_html(post_id, title, content, topic, meta_desc, image_url=None,
                 is_html=False, extra=None):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    # 파일명 충돌 방지: 같은 날 2건 이상이면 _2, _3 ... 접미사 (덮어쓰기 차단)
    base = CONTENT_DIR + "/auto_post_" + today
    path = base + ".html"
    seq = 2
    while os.path.exists(path):
        path = base + "_" + str(seq) + ".html"
        seq += 1
    fname = os.path.basename(path)
    esc = _esc
    # is_html이면 본문이 이미 HTML이므로 markdown 변환을 건너뜀
    body_html = content if is_html else markdown_to_html(content)
    url = SITE_URL + "/content/" + fname
    if image_url is None:
        image_url = get_unsplash_image(topic["keyword"])
    # Phase 5: SEO/AEO/GEO 확장 데이터 (extra 없으면 기존 동작 유지)
    extra = extra or {}
    tldr = extra.get("tldr", "")
    faq = extra.get("faq", []) or []
    references = extra.get("references", []) or []
    how_to_steps = extra.get("how_to_steps", []) or []
    focus_keyword = extra.get("focus_keyword") or topic.get("keyword", "")
    region = topic.get("region", "")
    cat_key = CATEGORY_MAP.get(topic.get("category", ""), "cat_startup")
    cat_label = CATEGORY_LABELS.get(cat_key, "블로그")
    iso = today + "T09:00:00+09:00"
    schema_block = build_json_ld(title, url, image_url, meta_desc, cat_key,
                                 today, focus_keyword, faq, references, how_to_steps)
    tldr_html = render_tldr(tldr)
    faq_html = render_faq(faq)
    refs_html = render_references(references)
    eeat_html = render_eeat(today)
    html = (
        '<!DOCTYPE html>\n'
        '<html lang="ko">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + esc(title) + ' | WOCS</title>\n'
        '<meta name="description" content="' + esc(meta_desc) + '">\n'
        '<meta name="keywords" content="' + esc(focus_keyword) + ', ' + esc(region) + ', WOCS">\n'
        '<meta name="author" content="' + esc(AUTHOR_NAME) + '">\n'
        '<meta name="robots" content="index, follow, max-image-preview:large">\n'
        '<link rel="canonical" href="' + url + '">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="' + esc(title) + '">\n'
        '<meta property="og:description" content="' + esc(meta_desc) + '">\n'
        '<meta property="og:url" content="' + url + '">\n'
        '<meta property="og:site_name" content="WOCS">\n'
        '<meta property="og:locale" content="ko_KR">\n'
        '<meta property="og:image" content="' + image_url + '">\n'
        '<meta property="article:published_time" content="' + iso + '">\n'
        '<meta property="article:modified_time" content="' + iso + '">\n'
        '<meta property="article:author" content="' + esc(AUTHOR_NAME) + '">\n'
        '<meta property="article:section" content="' + esc(cat_label) + '">\n'
        '<meta property="article:tag" content="' + esc(focus_keyword) + '">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="' + esc(title) + '">\n'
        '<meta name="twitter:description" content="' + esc(meta_desc) + '">\n'
        '<meta name="twitter:image" content="' + image_url + '">\n'
        + schema_block + '\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Lexend:wght@200;300;400;500;600&family=Noto+Sans+KR:wght@300;400;500;600&family=Noto+Serif+KR:wght@300;400;500;600&display=swap" rel="stylesheet">\n'
        '<link rel="stylesheet" href="../assets/css/wocs-common.css">\n'
        '<style>\n'
        '.post-wrap{max-width:800px;margin:0 auto;padding:120px 24px 80px}\n'
        '.post-title{font-family:var(--font-serif);font-size:clamp(28px,4vw,42px);font-weight:400;color:var(--ivory);line-height:1.3;margin-bottom:16px}\n'
        '.post-meta{font-family:var(--font-body);font-size:12px;color:rgba(240,235,224,0.4);margin-bottom:40px;padding-bottom:20px;border-bottom:1px solid rgba(201,169,110,0.1)}\n'
        '.post-meta span{margin-right:16px}\n'
        '.post-body{font-family:var(--font-body);font-size:16px;color:rgba(240,235,224,0.85);line-height:2.2}\n'
        '.post-body h2{font-family:var(--font-serif);font-size:clamp(22px,2.5vw,30px);font-weight:400;color:var(--ivory);margin:48px 0 16px;padding-bottom:12px;border-bottom:1px solid rgba(201,169,110,0.12)}\n'
        '.post-body h3{font-size:clamp(18px,2vw,24px);font-weight:400;color:var(--gold);margin:36px 0 12px}\n'
        '.post-body p{margin-bottom:20px}\n'
        '.post-body strong{color:var(--gold);font-weight:600}\n'
        '.post-body ul{margin:16px 0 24px 20px}\n'
        '.post-body li{margin-bottom:8px}\n'
        '.post-cta{margin-top:60px;padding:32px;border:2px solid rgba(201,169,110,0.25);background:rgba(201,169,110,0.03);text-align:center}\n'
        '.post-cta h4{font-size:17px;font-weight:400;color:var(--ivory);margin-bottom:12px}\n'
        '.post-cta p{font-family:var(--font-body);font-size:13px;color:rgba(240,235,224,0.55)}\n'
        '.post-cta a{display:inline-block;margin-top:16px;padding:12px 40px;background:var(--gold);color:var(--bg);font-family:var(--font-body);font-size:12px;letter-spacing:1px;text-decoration:none;transition:background .3s}\n'
        '.post-cta a:hover{background:var(--ivory)}\n'
        '.tldr{margin:0 0 36px;padding:20px 24px;border-left:3px solid var(--gold);background:rgba(201,169,110,0.06)}\n'
        '.tldr-label{display:block;font-size:11px;letter-spacing:1px;color:var(--gold);margin-bottom:8px}\n'
        '.tldr p{font-family:var(--font-body);font-size:15px;color:rgba(240,235,224,0.82);line-height:1.9;margin:0}\n'
        '.post-body table{width:100%;border-collapse:collapse;margin:24px 0;font-size:14px}\n'
        '.post-body th,.post-body td{border:1px solid rgba(201,169,110,0.2);padding:10px 12px;text-align:left}\n'
        '.post-body th{background:rgba(201,169,110,0.08);color:var(--gold);font-weight:500}\n'
        '.faq{margin:48px 0}\n'
        '.faq h2{font-family:var(--font-serif);font-size:clamp(22px,2.5vw,30px);font-weight:400;color:var(--ivory);margin-bottom:16px}\n'
        '.faq details{border-bottom:1px solid rgba(201,169,110,0.12);padding:14px 0}\n'
        '.faq summary{font-size:15px;color:var(--ivory);cursor:pointer}\n'
        '.faq details p{margin:12px 0 0;font-size:14px;color:rgba(240,235,224,0.75);line-height:1.9}\n'
        '.references{margin:40px 0}\n'
        '.references h3{font-size:16px;color:var(--gold);margin-bottom:12px}\n'
        '.references ul{margin:0 0 0 20px}\n'
        '.references li{font-size:13px;color:rgba(240,235,224,0.7);margin-bottom:6px}\n'
        '.references a{color:rgba(240,235,224,0.7)}\n'
        '.eeat{margin:40px 0;padding:20px 24px;border:1px solid rgba(201,169,110,0.15);background:rgba(201,169,110,0.03)}\n'
        '.eeat p{font-family:var(--font-body);font-size:12px;color:rgba(240,235,224,0.5);margin:4px 0}\n'
        '.eeat strong{color:var(--gold)}\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="post-wrap">\n'
        '  <h1 class="post-title">' + esc(title) + '</h1>\n'
        '  <div class="post-meta">\n'
        '    <span>' + today + '</span>\n'
        '    <span>' + esc(focus_keyword) + ' · ' + esc(region) + '</span>\n'
        '    <span>' + esc(cat_label) + '</span>\n'
        '  </div>\n'
        '  <img src="' + image_url + '" alt="' + esc(title) + '" style="width:100%;height:auto;margin-bottom:40px;border-radius:4px;filter:brightness(0.9)" loading="lazy">\n'
        + tldr_html +
        '  <div class="post-body">\n'
        + body_html + '\n'
        '  </div>\n'
        + refs_html
        + faq_html
        + eeat_html +
        '  <div class="post-cta">\n'
        '    <h4>' + esc(COMPANY_NAME) + ' 시공 전문 상담</h4>\n'
        '    <p>전남 화순 기반 어닝·천막·구조물 제조·시공 전문</p>\n'
        '    <a href="' + SITE_URL + '/contact/index.html">무료 상담 신청</a>\n'
        '  </div>\n'
        '</div>\n'
        '</body>\n'
        '</html>'
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(path + " 저장 완료")


# ─── LinkedIn ───

def generate_linkedin_post(title, content, topic):
    prompt = (
        "아래 블로그 글을 기반으로 LinkedIn 포스트를 작성하세요.\n\n"
        "제목: " + title + "\n"
        "키워드: " + topic["keyword"] + "\n"
        "지역: " + topic["region"] + "\n"
        "본문: " + content[:2000] + "\n\n"
        "=== LinkedIn 포스트 작성 규칙 ===\n"
        "1. 반드시 500~700자 이상 작성 (짧으면 안 됨)\n"
        "2. 소제목 없이 자연스러운 글 형식으로 작성\n"
        "3. 첫 줄: 독자의 관심을 끄는 질문이나 강렬한 문장\n"
        "4. 본문: 블로그 핵심 내용을 구체적으로 풀어서 설명 (숫자, 사례 포함)\n"
        "5. WOCS 소개를 자연스럽게 포함 (전남 화순, 16년 경력, 글램핑 구조물 전문)\n"
        "6. 마지막에 행동 유도:\n"
        "   - 자세히 보기: https://wocs.kr\n"
        "   - 무료 상담: 010-4337-0582\n"
        "7. 해시태그 5~7개 (#WOCS #글램핑 필수, #" + topic["region"] + " 포함)\n"
        "8. LinkedIn 전문가 톤, 줄바꿈을 활용해 가독성 높게\n\n"
        "포스트 텍스트만 출력하세요."
    )
    raw = gemini_generate_with_retry(prompt, label="linkedin-post")
    return raw.strip() if raw else None


def save_linkedin_data(title, li_text):
    data = {"title": title, "text": li_text}
    with open("linkedin_post.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("linkedin_post.json 저장 완료")


# ─── Webhook 모드 (n8n 외부 입력) ───

def run_webhook_mode(payload_raw):
    print("Webhook 모드 (n8n 외부 입력)")
    try:
        payload = json.loads(payload_raw)
    except Exception as e:
        print("페이로드 JSON 파싱 실패: " + str(e))
        exit(1)
    if not isinstance(payload, dict):
        print("페이로드 형식 오류: JSON 객체가 아님")
        exit(1)

    # 필수 필드 검증 (누락 시 즉시 종료)
    required = ["title", "content", "image_url"]
    missing = [k for k in required if not str(payload.get(k) or "").strip()]
    if missing:
        print("필수 필드 누락: " + ", ".join(missing))
        exit(1)

    title = str(payload["title"]).strip()
    content = str(payload["content"])
    image_url = str(payload["image_url"]).strip()
    keyword = str(payload.get("keyword") or "").strip()
    region = str(payload.get("region") or "전남").strip()
    excerpt = str(payload.get("excerpt") or "").strip()
    meta_desc = str(payload.get("meta_desc") or excerpt or "").strip()
    tags = payload.get("tags") or []
    # Phase 5 핫픽스: GitHub repository_dispatch는 client_payload top-level 속성
    # 10개 제한 → tldr/faq/references/how_to_steps를 seo_extras 객체로 래핑.
    # seo_extras 우선, 없으면 top-level fallback (구 페이로드 회귀 안전)
    seo_extras = payload.get("seo_extras")
    if not isinstance(seo_extras, dict):
        seo_extras = {}
    tldr = str(seo_extras.get("tldr") or payload.get("tldr") or "").strip()
    faq_raw = seo_extras.get("faq") or payload.get("faq") or []
    faq = [x for x in faq_raw if isinstance(x, dict)]
    refs_raw = seo_extras.get("references") or payload.get("references") or []
    references = [x for x in refs_raw if isinstance(x, dict)]
    steps_raw = seo_extras.get("how_to_steps") or payload.get("how_to_steps") or []
    how_to_steps = [str(x).strip() for x in steps_raw if str(x).strip()]

    # 카테고리 정규화: payload는 wocs.kr 키(cat_*) 또는 한글 카테고리명을 허용
    reverse_cat = {v: k for k, v in CATEGORY_MAP.items()}
    cat_in = str(payload.get("category") or "").strip()
    if cat_in in CATEGORY_MAP:
        topic_category = cat_in
    elif cat_in in reverse_cat:
        topic_category = reverse_cat[cat_in]
    else:
        topic_category = "창업가이드"

    topic = {"keyword": keyword or "글램핑", "region": region, "category": topic_category}

    # meta description 보강: excerpt → tldr → 본문 순 (외부 API 미사용)
    if not meta_desc:
        if tldr:
            meta_desc = tldr[:150]
        else:
            plain = re.sub(r"<[^>]+>", " ", content)
            plain = re.sub(r"\s+", " ", plain).strip()
            meta_desc = plain[:150]

    extra = {"tldr": tldr, "faq": faq, "references": references,
             "how_to_steps": how_to_steps, "focus_keyword": keyword}

    post_id = get_next_id()
    print("제목: " + title)
    print("ID: " + str(post_id))
    print("카테고리: " + topic_category + " (" + CATEGORY_MAP.get(topic_category, "cat_startup") + ")")
    print("이미지: " + image_url)
    print("AEO/GEO: TL;DR=" + ("있음" if tldr else "없음")
          + ", FAQ=" + str(len(faq)) + "개, 출처=" + str(len(references))
          + "개, HowTo=" + str(len(how_to_steps)) + "단계")

    save_to_blog_data(post_id, title, content, topic, meta_desc,
                      image_url=image_url, is_html=True, extra=extra)
    save_to_html(post_id, title, content, topic, meta_desc,
                 image_url=image_url, is_html=True, extra=extra)

    if tags:
        print("tags " + str(len(tags)) + "개 수신 - 현 정적 구조에 저장 슬롯 없음(미반영)")

    print("Webhook 발행 완료")


# ─── 메인 ───

def main():
    if _WEBHOOK_MODE:
        run_webhook_mode(os.environ.get("N8N_PAYLOAD", ""))
        return
    topic = pick_topic()
    post_id = get_next_id()
    cta_this_post = should_include_cta(topic)

    print("주제: " + topic["long_tail"])
    print("지역: " + topic["region"])
    print("카테고리: " + topic["category"])
    print("CTA 포함: " + str(cta_this_post))
    print("AI 글 생성 중...")

    raw = generate_content(topic, cta_this_post)
    if not raw:
        print("생성 실패")
        exit(1)

    title, content = parse_content(raw)
    if not title or not content:
        print("파싱 실패")
        exit(1)

    if cta_this_post:
        content += CTA_TEXT

    print("제목: " + title)
    print("글자 수: " + str(len(content.replace(" ", ""))))

    # meta description 생성
    print("메타 설명 생성 중...")
    meta_desc = generate_meta_description(topic, content)
    print("메타: " + meta_desc[:60] + "...")

    # 저장
    save_to_blog_data(post_id, title, content, topic, meta_desc)
    save_to_html(post_id, title, content, topic, meta_desc)

    # 중복 방지 기록
    save_used_topic(topic["keyword"], topic["region"])

    # LinkedIn
    print("LinkedIn 포스트 생성 중...")
    li_text = generate_linkedin_post(title, content, topic)
    if li_text:
        save_linkedin_data(title, li_text)
        print("LinkedIn 포스트:\n" + li_text[:100] + "...")
    else:
        print("LinkedIn 포스트 생성 실패 (블로그 글은 정상 저장)")

    print("완료!")


if __name__ == "__main__":
    main()
