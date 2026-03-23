#!/usr/bin/env python3
import os, json, random, re
from datetime import datetime, timedelta
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY") or ""
if not API_KEY:
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            API_KEY = json.load(f).get("gemini_api_key", "")
    except:
        pass

if not API_KEY:
    print("GEMINI_API_KEY 없음")
    exit(1)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"
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
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print("오류: " + str(e))
        return None


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
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        desc = response.text.strip().replace('"', "'").replace("\n", " ")
        return desc[:150]
    except:
        return content[:100].replace("\n", " ")


# ─── 저장: blog-data.js ───

def save_to_blog_data(post_id, title, content, topic, meta_desc):
    today = datetime.now().strftime("%Y-%m-%d")
    safe = lambda s: s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    image_url = get_unsplash_image(topic["keyword"])
    cat_key = CATEGORY_MAP.get(topic["category"], "cat_startup")
    excerpt = content[:100].replace("\n", " ")
    new_entry = (
        '{\n'
        "  id:" + str(post_id) + ", title:'" + safe(title) + "', excerpt:'" + safe(excerpt) + "',\n"
        "  date:'" + today + "', category:'" + cat_key + "', featured:false,\n"
        "  image:'" + image_url + "',\n"
        "  description:'" + safe(meta_desc) + "',\n"
        "  content:'" + safe(content[:3000]) + "'\n"
        '}'
    )
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            data = f.read()
        data = data.replace("var BLOG_POSTS = [", "var BLOG_POSTS = [\n" + new_entry + ",", 1)
        with open(BLOG_DATA_PATH, "w", encoding="utf-8") as f:
            f.write(data)
        print("blog-data.js 저장 완료 (id:" + str(post_id) + ")")
    except Exception as e:
        print("저장 실패: " + str(e))


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


def save_to_html(post_id, title, content, topic, meta_desc):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = CONTENT_DIR + "/auto_post_" + today + ".html"
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    body_html = markdown_to_html(content)
    url = "https://wocs.kr/content/auto_post_" + today + ".html"
    image_url = get_unsplash_image(topic["keyword"])
    html = (
        '<!DOCTYPE html>\n'
        '<html lang="ko">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + esc(title) + ' | WOCS</title>\n'
        '<meta name="description" content="' + esc(meta_desc) + '">\n'
        '<meta name="keywords" content="' + esc(topic["keyword"]) + ', ' + esc(topic["region"]) + ', WOCS, 글램핑">\n'
        '<link rel="canonical" href="' + url + '">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="' + esc(title) + '">\n'
        '<meta property="og:description" content="' + esc(meta_desc) + '">\n'
        '<meta property="og:url" content="' + url + '">\n'
        '<meta property="og:site_name" content="WOCS">\n'
        '<meta property="og:locale" content="ko_KR">\n'
        '<meta property="og:image" content="' + image_url + '">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="' + esc(title) + '">\n'
        '<meta name="twitter:description" content="' + esc(meta_desc) + '">\n'
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
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="post-wrap">\n'
        '  <h1 class="post-title">' + esc(title) + '</h1>\n'
        '  <div class="post-meta">\n'
        '    <span>' + today + '</span>\n'
        '    <span>' + esc(topic["keyword"]) + ' · ' + esc(topic["region"]) + '</span>\n'
        '  </div>\n'
        '  <img src="' + image_url + '" alt="' + esc(title) + '" style="width:100%;height:auto;margin-bottom:40px;border-radius:4px;filter:brightness(0.9)" loading="lazy">\n'
        '  <div class="post-body">\n'
        + body_html + '\n'
        '  </div>\n'
        '  <div class="post-cta">\n'
        '    <h4>WOCS 글램핑 구조물 전문 상담</h4>\n'
        '    <p>전남 화순 기반 글램핑 구조물 제조·시공 전문</p>\n'
        '    <a href="https://wocs.kr/contact/index.html">무료 상담 신청</a>\n'
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
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print("LinkedIn 포스트 생성 오류: " + str(e))
        return None


def save_linkedin_data(title, li_text):
    data = {"title": title, "text": li_text}
    with open("linkedin_post.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("linkedin_post.json 저장 완료")


# ─── 메인 ───

def main():
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
