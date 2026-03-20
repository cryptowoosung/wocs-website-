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

def get_used_topics():
    used = set()
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            keywords = re.findall(r'"keyword"\s*:\s*"([^"]+)"', f.read())
            used.update(keywords)
    except:
        pass
    return used

def pick_topic():
    used = get_used_topics()
    available = [t for t in TOPICS if t["keyword"] not in used]
    return random.choice(available if available else TOPICS)

def get_next_id():
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            ids = re.findall(r'"id"\s*:\s*(\d+)', f.read())
            return max([int(i) for i in ids], default=99) + 1
    except:
        return 100

def generate_content(topic):
    prompt = (
        "당신은 글램핑 시공 전문가입니다. 아래 주제로 SEO 최적화된 블로그 글을 작성하세요.\n\n"
        "주제: " + topic["title_hint"] + "\n"
        "키워드: " + topic["keyword"] + "\n"
        "회사: WOCS (우성어닝천막공사캠프시스템) - 전남 화순 기반 글램핑 구조물 제조시공 전문\n\n"
        "형식:\nTITLE: (제목)\nEXCERPT: (2줄 요약)\nCONTENT: (본문 800~1200자, 소제목 포함)\n\n"
        "조건: 실용적이고 전문적, WOCS 1~2회 언급, 태풍/풍속/시공기간 보장 문구 금지, 블로그 문체"
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
    content = re.search(r'CONTENT:\s*(.+)', raw, re.DOTALL)
    return (
        title.group(1).strip() if title else "",
        excerpt.group(1).strip().replace('\n', ' ') if excerpt else "",
        content.group(1).strip() if content else ""
    )

def save_to_blog_data(post_id, title, excerpt, content, topic):
    today = datetime.now().strftime("%Y-%m-%d")
    safe = lambda s: s.replace('\\', '').replace('"', "'")
    new_entry = (
        '  {\n'
        '    "id": ' + str(post_id) + ',\n'
        '    "title": "' + safe(title) + '",\n'
        '    "excerpt": "' + safe(excerpt[:100]) + '",\n'
        '    "content": "' + safe(content[:2000]).replace('\n', ' ') + '",\n'
        '    "category": "글램핑창업",\n'
        '    "keyword": "' + topic['keyword'] + '",\n'
        '    "date": "' + today + '",\n'
        '    "image": "assets/images/blog/default.jpg"\n'
        '  }'
    )
    try:
        with open(BLOG_DATA_PATH, "r", encoding="utf-8") as f:
            data = f.read()
        data = data.replace("const blogPosts = [", "const blogPosts = [\n" + new_entry + ",", 1)
        with open(BLOG_DATA_PATH, "w", encoding="utf-8") as f:
            f.write(data)
        print("blog-data.js 저장 완료 (id:" + str(post_id) + ")")
    except Exception as e:
        print("저장 실패: " + str(e))

def save_to_txt(post_id, title, content, topic):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = CONTENT_DIR + "/auto_post_" + today + "_" + str(post_id) + ".txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(title + "\n" + today + "\n" + topic['keyword'] + "\n\n" + content)
    print(path + " 저장 완료")

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

    title, excerpt, content = parse_output(raw)
    if not title or not content:
        print("파싱 실패")
        exit(1)

    print("제목: " + title)
    save_to_blog_data(post_id, title, excerpt, content, topic)
    save_to_txt(post_id, title, content, topic)
    print("완료!")

if __name__ == "__main__":
    main()
