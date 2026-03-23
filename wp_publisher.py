"""
WOCS WordPress Auto Publisher
- content/ 폴더의 오늘 날짜 auto_post_*.txt 파일을 찾아
  glampingtentgo.com 워드프레스에 자동 포스팅
"""

import os
import sys
import glob
import re
from datetime import datetime

import requests

# ── 설정 ──
WP_URL = "https://glampingtentgo.com"
WP_USER = "candlejs6"
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "5LxV PK7F SdZ4 nf1X r83l QB9d")

CATEGORY_NAME = "글램핑창업"


def get_session():
    """Basic Auth가 설정된 requests.Session 반환"""
    s = requests.Session()
    s.auth = (WP_USER, WP_APP_PASSWORD)
    s.headers.update({"Content-Type": "application/json"})
    return s


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


def test_auth(session):
    """인증 테스트: GET /wp-json/wp/v2/users/me"""
    print("\n🔐 인증 테스트...")
    print(f"  URL: {WP_URL}")
    print(f"  사용자: {WP_USER}")
    print(f"  앱 비밀번호: {WP_APP_PASSWORD[:8]}{'*' * (len(WP_APP_PASSWORD) - 8)}")

    try:
        res = session.get(f"{WP_URL}/wp-json/wp/v2/users/me", timeout=30)
        print(f"  응답 코드: HTTP {res.status_code}")

        if res.status_code == 200:
            data = safe_json(res)
            if data:
                print(f"  ✅ 인증 성공! 사용자: {data.get('name', '?')} (ID: {data.get('id', '?')})")
                roles = data.get("roles", [])
                print(f"  역할: {', '.join(roles)}")
                return True
            else:
                print(f"  ⚠️ 인증 응답 파싱 불가")
                return False
        elif res.status_code == 401:
            print(f"  ❌ 인증 실패 (401 Unauthorized)")
            data = safe_json(res)
            if data:
                print(f"  에러 코드: {data.get('code', '?')}")
                print(f"  에러 메시지: {data.get('message', '?')}")
            print()
            print("  확인사항:")
            print("  1. 워드프레스 관리자 > 사용자 > 프로필 > 애플리케이션 비밀번호 확인")
            print("  2. WP_APP_PASSWORD 환경변수가 GitHub Secrets에 설정되었는지 확인")
            print("  3. 보안 플러그인이 REST API 인증을 차단하는지 확인")
            return False
        elif res.status_code == 403:
            print(f"  ❌ 권한 부족 (403 Forbidden)")
            print(f"  응답: {res.text[:300]}")
            return False
        else:
            print(f"  ❌ 예상치 못한 응답: HTTP {res.status_code}")
            print(f"  응답: {res.text[:300]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  ❌ 연결 실패: {e}")
        return False


def get_category_id(session):
    """카테고리 이름으로 ID 조회, 없으면 생성"""
    try:
        res = session.get(
            f"{WP_URL}/wp-json/wp/v2/categories",
            params={"search": CATEGORY_NAME},
            timeout=30,
        )
        data = safe_json(res)
        if res.status_code == 200 and data and isinstance(data, list) and len(data) > 0:
            cat_id = data[0]["id"]
            print(f"  카테고리 '{CATEGORY_NAME}' 찾음 (ID: {cat_id})")
            return cat_id
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ 카테고리 조회 실패: {e}")

    # 카테고리 생성 시도
    try:
        res = session.post(
            f"{WP_URL}/wp-json/wp/v2/categories",
            json={"name": CATEGORY_NAME},
            timeout=30,
        )
        data = safe_json(res)
        if res.status_code == 201 and data:
            cat_id = data.get("id")
            print(f"  카테고리 '{CATEGORY_NAME}' 생성 (ID: {cat_id})")
            return cat_id
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


def publish_to_wordpress(session, post_data, category_id):
    """워드프레스 REST API로 포스팅"""
    payload = {
        "title": post_data["title"],
        "content": post_data["content"],
        "status": "publish",
        "categories": [category_id] if category_id else [],
    }

    try:
        res = session.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
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

    print(f"📄 오늘({today}) 포스트 파일 {len(files)}개 발견")

    session = get_session()

    # 인증 테스트
    if not test_auth(session):
        print("\n❌ 인증 실패. 포스팅을 건너뜁니다.")
        sys.exit(0)

    # 카테고리 조회
    print("\n📂 카테고리 설정...")
    category_id = get_category_id(session)

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
        print(f"  본문 길이: {len(post_data['content'])}자")

        res = publish_to_wordpress(session, post_data, category_id)
        if res is None:
            fail_count += 1
            continue

        if res.status_code == 201:
            data = safe_json(res)
            post_url = data.get("link", "(URL 확인 불가)") if data else "(응답 파싱 불가)"
            post_id = data.get("id", "?") if data else "?"
            print(f"  ✅ 워드프레스 포스팅 완료 (ID: {post_id})")
            print(f"  URL: {post_url}")
            success_count += 1
        else:
            print(f"  ❌ 포스팅 실패 (HTTP {res.status_code})")
            data = safe_json(res)
            if data:
                print(f"  에러 코드: {data.get('code', '?')}")
                print(f"  에러 메시지: {data.get('message', '?')}")
            else:
                print(f"  응답: {res.text[:500]}")
            fail_count += 1

    print(f"\n📊 결과: 성공 {success_count}건, 실패 {fail_count}건")
    sys.exit(0)


if __name__ == "__main__":
    main()
