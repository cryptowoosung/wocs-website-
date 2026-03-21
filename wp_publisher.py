"""
WOCS WordPress Auto Publisher
- content/ 폴더의 오늘 날짜 auto_post_*.txt 파일을 찾아
  glampingtentgo.com 워드프레스에 자동 포스팅
"""

import os
import sys
import glob
import base64
import re
from datetime import datetime

import requests

# ── 설정 ──
WP_URLS = [
    "https://glampingtentgo.com",
    "https://candlejs6.mycafe24.com",
]
WP_USER = "candlejs6"
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "5LxV PK7F SdZ4 nf1X r83l QB9d")

CATEGORY_NAME = "글램핑창업"


def get_auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def safe_json(res):
    """응답이 빈 값이거나 JSON이 아닐 때 안전하게 파싱"""
    if not res.text or not res.text.strip():
        print(f"  ⚠️ 빈 응답 (HTTP {res.status_code})")
        return None
    try:
        return res.json()
    except Exception as e:
        print(f"  ⚠️ JSON 파싱 실패: {e}")
        print(f"  응답 내용: {res.text[:300]}")
        return None


def check_rest_api(base_url, headers):
    """REST API 활성화 여부 확인"""
    try:
        res = requests.get(
            f"{base_url}/wp-json/",
            headers=headers,
            timeout=15,
        )
        print(f"  REST API 체크 ({base_url}): HTTP {res.status_code}")
        if res.status_code == 200:
            data = safe_json(res)
            if data and "name" in data:
                print(f"  사이트 이름: {data['name']}")
                return True
            else:
                print(f"  ⚠️ REST API 응답이 비정상입니다")
                return False
        else:
            print(f"  ⚠️ REST API 비활성화 또는 접근 불가")
            print(f"  응답: {res.text[:300]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 연결 실패 ({base_url}): {e}")
        return False


def find_working_url(headers):
    """작동하는 WP URL 찾기"""
    for url in WP_URLS:
        print(f"\n🔍 URL 시도: {url}")
        if check_rest_api(url, headers):
            print(f"  ✅ 사용 가능: {url}")
            return url
    return None


def get_category_id(base_url, headers):
    """카테고리 이름으로 ID 조회, 없으면 생성"""
    try:
        res = requests.get(
            f"{base_url}/wp-json/wp/v2/categories",
            headers=headers,
            params={"search": CATEGORY_NAME},
            timeout=30,
        )
        print(f"  카테고리 조회: HTTP {res.status_code}")
        data = safe_json(res)
        if res.status_code == 200 and data and isinstance(data, list) and len(data) > 0:
            return data[0]["id"]
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ 카테고리 조회 실패: {e}")

    # 카테고리 생성 시도
    try:
        res = requests.post(
            f"{base_url}/wp-json/wp/v2/categories",
            headers={**headers, "Content-Type": "application/json"},
            json={"name": CATEGORY_NAME},
            timeout=30,
        )
        print(f"  카테고리 생성: HTTP {res.status_code}")
        data = safe_json(res)
        if res.status_code == 201 and data:
            return data.get("id")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ 카테고리 생성 실패: {e}")

    print(f"  ⚠️ 카테고리 설정 실패, 카테고리 없이 진행")
    return None


def parse_post_file(filepath):
    """auto_post 파일 파싱: 1행=제목, 2행=날짜, 3행=키워드, 4행~=본문"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 5:
        return None

    title = lines[0].strip()
    body_lines = lines[4:] if len(lines) > 4 else lines[3:]
    body = "".join(body_lines).strip()

    html = markdown_to_html(body)
    return {"title": title, "content": html}


def markdown_to_html(text):
    """간단한 마크다운 → HTML 변환"""
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
            converted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f"<p>{converted}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def publish_to_wordpress(base_url, post_data, headers, category_id):
    """워드프레스 REST API로 포스팅"""
    payload = {
        "title": post_data["title"],
        "content": post_data["content"],
        "status": "publish",
        "categories": [category_id] if category_id else [],
    }

    try:
        res = requests.post(
            f"{base_url}/wp-json/wp/v2/posts",
            headers={**headers, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        return res
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 포스팅 요청 실패: {e}")
        return None


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = os.path.join("content", f"auto_post_{today}_*.txt")
    files = glob.glob(pattern)

    if not files:
        print(f"⚠️ 오늘({today}) 생성된 포스트 파일이 없습니다.")
        sys.exit(0)

    headers = get_auth_header()

    # 작동하는 URL 찾기
    wp_url = find_working_url(headers)
    if not wp_url:
        print("\n❌ 모든 워드프레스 URL 접속 실패. 포스팅을 건너뜁니다.")
        print("  시도한 URL:")
        for url in WP_URLS:
            print(f"    - {url}")
        sys.exit(0)

    print(f"\n📡 사용 URL: {wp_url}")

    category_id = get_category_id(wp_url, headers)
    print(f"📂 카테고리 '{CATEGORY_NAME}' ID: {category_id}")

    success_count = 0
    fail_count = 0

    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\n📄 처리 중: {filename}")

        post_data = parse_post_file(filepath)
        if not post_data:
            print(f"  ⚠️ 파일 형식 오류, 건너뜀")
            fail_count += 1
            continue

        print(f"  제목: {post_data['title']}")

        res = publish_to_wordpress(wp_url, post_data, headers, category_id)
        if res is None:
            fail_count += 1
            continue

        if res.status_code == 201:
            data = safe_json(res)
            post_url = data.get("link", "(URL 확인 불가)") if data else "(응답 파싱 불가)"
            print(f"  ✅ 워드프레스 포스팅 완료: {post_url}")
            success_count += 1
        else:
            print(f"  ❌ 포스팅 실패 (HTTP {res.status_code})")
            print(f"  응답 헤더: {dict(res.headers)}")
            print(f"  응답 내용: {res.text[:500]}")
            fail_count += 1

    print(f"\n📊 결과: 성공 {success_count}건, 실패 {fail_count}건")
    sys.exit(0)


if __name__ == "__main__":
    main()
