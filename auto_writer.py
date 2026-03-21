#!/usr/bin/env python3
import os, json, random, re
from datetime import datetime
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
print("Gemini 연결됨")

TOPICS = [
    {"keyword": "글램핑 창업", "title_hint": "글램핑 창업 완전 가이드"},
    {"keyword": "글램핑 시공 단가", "title_hint": "글램핑 시공 비용 현실 정리"},
    {"keyword": "사파리텐트 추천", "title_hint": "사파리텐트 고르는 법"},
    {"keyword": "돔텐트 글램핑", "title_hint": "돔텐트 글램핑 트렌드 분석"},
    {"keyword": "글램핑 수익률", "title_hint": "글램핑장 수익률 계산법"},
    {"keyword": "글램핑 구조물 허가", "title_hint": "글램핑 구조물 허가 절차"},
    {"keyword": "모듈러 글램핑", "title_hint": "모듈러 글램핑 시공 방식"},
    {"keyword": "글램핑 부지 선정", "title_hint": "글램핑 부지 고르는 기준"},
    {"keyword": "글램핑 인테리어", "title_hint": "글램핑 인테리어 트렌드"},
    {"keyword": "4계절 글램핑텐트", "title_hint": "4계절 운영 가능한 글램핑텐트"},
    {"keyword": "글램핑 정부지원", "title_hint": "글램핑 창업 정부지원금 총정리"},
    {"keyword": "글램핑 운영 노하우", "title_hint": "글램핑장 운영 실전 노하우"},
    {"keyword": "어닝 시공", "title_hint": "어닝 시공 완벽 가이드"},
    {"keyword": "천막 구조물", "title_hint": "천막 구조물 종류와 선택법"},
    {"keyword": "글램핑 OEM", "title_hint": "글램핑 구조물 OEM 구매 전략"},
    {"keyword": "캠핑장 창업비용", "title_hint": "캠핑장 창업비용 현실 분석"},
    {"keyword": "글램핑 시공업체", "title_hint": "글램핑 시공업체 선택 기준"},
    {"keyword": "유니버설 조인트", "title_hint": "무용접 유니버설 조인트란?"},
    {"keyword": "글램핑 내구성", "title_hint": "글램핑 구조물 내구성 비교"},
    {"keyword": "글램핑 트렌드 2026", "title_hint": "2026년 글램핑 트렌드 전망"},
]

BLOG_DATA_PATH = "assets/js/blog-data.js"
CONTENT_DIR = "content"

UNSPLASH_TAGS = {
    "글램핑": "glamping,tent",
    "사파리텐트": "safari,tent,camping",
    "돔텐트": "dome,tent,geodesic",
    "어닝": "awning,outdoor",
    "천막": "tent,canopy",
    "캠핑": "camping,nature",
    "인테리어": "interior,glamping",
    "모듈러": "modular,cabin",
    "부지": "land,nature,mountain",
}

def get_unsplash_image(keyword):
    tags = "glamping,tent"
    for k, v in UNSPLASH_TAGS.items():
        if k in keyword:
            tags = v
            break
    return "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800&h=500&fit=crop&q=85&" + tags

def get_used_topics():
    used = set()
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            data = f.read()
            # 새 포맷: title:'...' 에서 제목 추출
            titles = re.findall(r"title:'([^']+)'", data)
            used.update(titles)
    except:
        pass
    return used

def pick_topic():
    used_titles = get_used_topics()
    joined = " ".join(used_titles)
    available = [t for t in TOPICS if t["keyword"] not in joined]
    return random.choice(available if available else TOPICS)

def get_next_id():
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            ids = re.findall(r'id:(\d+)', f.read())
            return max([int(i) for i in ids], default=99) + 1
    except:
        return 100

def generate_content(topic):
    prompt = (
        "당신은 16년 경력의 글램핑 시공 전문가입니다. 아래 주제로 SEO 최적화된 블로그 글을 작성하세요.\n\n"
        "주제: " + topic["title_hint"] + "\n"
        "키워드: " + topic["keyword"] + "\n"
        "회사: WOCS (우성어닝천막공사캠프시스템) - 전남 화순 기반 글램핑 구조물 제조시공 전문\n\n"
        "=== 본문 작성 규칙 ===\n"
        "1. 반드시 1000~1500자 이상 작성 (짧으면 안 됨)\n"
        "2. 마크다운 형식으로 작성\n"
        "3. ## 소제목을 3~4개 포함 (각 섹션마다 2~3문단씩)\n"
        "4. 실용적이고 구체적인 정보 위주 (숫자, 비용, 절차 등)\n"
        "5. WOCS를 본문 중 자연스럽게 2~3회 언급\n"
        "6. 첫 문단에서 독자의 관심을 끄는 도입부 작성\n"
        "7. 마지막에 정리 또는 행동 유도 문단 포함\n"
        "8. 태풍/풍속/시공기간 보장 문구 금지\n"
        "9. 친근하지만 전문적인 블로그 문체\n\n"
        "=== 출력 형식 (반드시 준수) ===\n"
        "TITLE: (매력적인 제목, 30자 이내)\n"
        "EXCERPT: (2줄 요약, 핵심 가치 전달)\n"
        "CONTENT: (본문 1000~1500자, ## 소제목 3~4개 포함, 마크다운)\n"
        "SEO_TITLE: (SEO 제목, 60자 이내, 키워드 포함)\n"
        "META_DESCRIPTION: (메타 설명, 155자 이내, 핵심 내용 요약)\n"
        "FOCUS_KEYWORD: (핵심 키워드 1개)\n"
    )
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        print("오류: " + str(e))
        return None

def parse_output(raw):
    title = re.search(r'TITLE:\s*(.+)', raw)
    excerpt = re.search(r'EXCERPT:\s*(.+?)(?=CONTENT:|$)', raw, re.DOTALL)
    content = re.search(r'CONTENT:\s*(.+?)(?=SEO_TITLE:|$)', raw, re.DOTALL)
    seo_title = re.search(r'SEO_TITLE:\s*(.+)', raw)
    meta_desc = re.search(r'META_DESCRIPTION:\s*(.+)', raw)
    focus_kw = re.search(r'FOCUS_KEYWORD:\s*(.+)', raw)
    return (
        title.group(1).strip() if title else "",
        excerpt.group(1).strip().replace('\n', ' ') if excerpt else "",
        content.group(1).strip() if content else "",
        seo_title.group(1).strip() if seo_title else "",
        meta_desc.group(1).strip() if meta_desc else "",
        focus_kw.group(1).strip() if focus_kw else ""
    )

def save_to_blog_data(post_id, title, excerpt, content, topic, seo_title, meta_desc, focus_kw):
    today = datetime.now().strftime("%Y-%m-%d")
    safe = lambda s: s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    image_url = get_unsplash_image(topic['keyword'])
    new_entry = (
        '{\n'
        "  id:" + str(post_id) + ", title:'" + safe(title) + "', excerpt:'" + safe(excerpt[:100]) + "',\n"
        "  date:'" + today + "', category:'cat_startup', featured:false,\n"
        "  image:'" + image_url + "',\n"
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


def save_to_html(post_id, title, content, topic, seo_title, meta_desc, focus_kw):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = CONTENT_DIR + "/auto_post_" + today + ".html"
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    body_html = markdown_to_html(content)
    url = "https://wocs.kr/content/auto_post_" + today + ".html"
    image_url = get_unsplash_image(topic['keyword'])
    html = (
        '<!DOCTYPE html>\n'
        '<html lang="ko">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + esc(seo_title or title) + '</title>\n'
        '<meta name="description" content="' + esc(meta_desc) + '">\n'
        '<meta name="keywords" content="' + esc(focus_kw) + ', WOCS, 글램핑">\n'
        '<link rel="canonical" href="' + url + '">\n'
        '<!-- Open Graph -->\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="' + esc(seo_title or title) + '">\n'
        '<meta property="og:description" content="' + esc(meta_desc) + '">\n'
        '<meta property="og:url" content="' + url + '">\n'
        '<meta property="og:site_name" content="WOCS">\n'
        '<meta property="og:locale" content="ko_KR">\n'
        '<meta property="og:image" content="' + image_url + '">\n'
        '<!-- Twitter Card -->\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="' + esc(seo_title or title) + '">\n'
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
        '    <span>' + esc(topic["keyword"]) + '</span>\n'
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

def generate_linkedin_post(title, content, keyword):
    prompt = (
        "아래 블로그 글을 기반으로 LinkedIn 포스트를 작성하세요.\n\n"
        "제목: " + title + "\n"
        "키워드: " + keyword + "\n"
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
        "7. 해시태그 5~7개 (#WOCS #글램핑 필수, 주제 관련 태그 추가)\n"
        "8. LinkedIn 전문가 톤, 줄바꿈을 활용해 가독성 높게\n\n"
        "포스트 텍스트만 출력하세요."
    )
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print("LinkedIn 포스트 생성 오류: " + str(e))
        return None


def save_linkedin_data(title, li_text):
    data = {"title": title, "text": li_text}
    with open("linkedin_post.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("linkedin_post.json 저장 완료")


def main():
    topic = pick_topic()
    post_id = get_next_id()
    print("주제: " + topic['title_hint'])
    print("키워드: " + topic['keyword'])
    print("AI 글 생성 중...")

    raw = generate_content(topic)
    if not raw:
        print("생성 실패")
        exit(1)

    title, excerpt, content, seo_title, meta_desc, focus_kw = parse_output(raw)
    if not title or not content:
        print("파싱 실패")
        exit(1)

    print("제목: " + title)
    print("SEO: " + seo_title + " | " + focus_kw)
    save_to_blog_data(post_id, title, excerpt, content, topic, seo_title, meta_desc, focus_kw)
    save_to_html(post_id, title, content, topic, seo_title, meta_desc, focus_kw)

    print("LinkedIn 포스트 생성 중...")
    li_text = generate_linkedin_post(title, content, topic['keyword'])
    if li_text:
        save_linkedin_data(title, li_text)
        print("LinkedIn 포스트:\n" + li_text[:100] + "...")
    else:
        print("LinkedIn 포스트 생성 실패 (블로그 글은 정상 저장)")

    print("완료!")

if __name__ == "__main__":
    main()
