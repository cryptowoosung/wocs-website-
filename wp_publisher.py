"""
WOCS WordPress Auto Publisher
- content/ 폴더의 오늘 날짜 auto_post_*.txt 파일을 찾아
  glampingtentgo.com 워드프레스에 자동 포스팅
"""

import os
import glob
import base64
import json
from datetime import datetime

import requests

# ── 설정 ──
WP_URL = "https://glampingtentgo.com"
WP_USER = "candlejs6"
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "5LxV PK7F SdZ4 nf1X r83l QB9d")

API_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/posts"
CATEGORY_NAME = "글램핑창업"


def get_auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def get_category_id(headers):
    """카테고리 이름으로 ID 조회, 없으면 생성"""
    res = requests.get(
        f"{WP_URL}/wp-json/wp/v2/categories",
        headers=headers,
        params={"search": CATEGORY_NAME},
        timeout=30,
    )
    if res.status_code == 200 and res.json():
        return res.json()[0]["id"]

    # 카테고리 생성
    res = requests.post(
        f"{WP_URL}/wp-json/wp/v2/categories",
        headers={**headers, "Content-Type": "application/json"},
        json={"name": CATEGORY_NAME},
        timeout=30,
    )
    if res.status_code == 201:
        return res.json()["id"]
    return None


def parse_post_file(filepath):
    """auto_post 파일 파싱: 1행=제목, 2행=날짜, 3행=키워드, 4행~=본문"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 5:
        return None

    title = lines[0].strip()
    # 4행(빈줄) 이후부터 본문
    body_lines = lines[4:] if len(lines) > 4 else lines[3:]
    body = "".join(body_lines).strip()

    # 마크다운 → HTML 간단 변환
    html = markdown_to_html(body)
    return {"title": title, "content": html}


def markdown_to_html(text):
    """간단한 마크다운 → HTML 변환"""
    import re

    lines = text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")
            continue

        # 헤딩
        if stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped == "---":
            html_lines.append("<hr>")
        else:
            # 볼드 처리
            converted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f"<p>{converted}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def publish_to_wordpress(post_data, headers, category_id):
    """워드프레스 REST API로 포스팅"""
    payload = {
        "title": post_data["title"],
        "content": post_data["content"],
        "status": "publish",
        "categories": [category_id] if category_id else [],
    }

    res = requests.post(
        API_ENDPOINT,
        headers={**headers, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    return res


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = os.path.join("content", f"auto_post_{today}_*.txt")
    files = glob.glob(pattern)

    if not files:
        print(f"⚠️ 오늘({today}) 생성된 포스트 파일이 없습니다.")
        return

    headers = get_auth_header()
    category_id = get_category_id(headers)
    print(f"📂 카테고리 '{CATEGORY_NAME}' ID: {category_id}")

    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\n📄 처리 중: {filename}")

        post_data = parse_post_file(filepath)
        if not post_data:
            print(f"  ⚠️ 파일 형식 오류, 건너뜀")
            continue

        print(f"  제목: {post_data['title']}")

        res = publish_to_wordpress(post_data, headers, category_id)
        if res.status_code == 201:
            post_url = res.json().get("link", "")
            print(f"  ✅ 워드프레스 포스팅 완료: {post_url}")
        else:
            print(f"  ❌ 포스팅 실패 (HTTP {res.status_code}): {res.text[:200]}")


if __name__ == "__main__":
    main()
