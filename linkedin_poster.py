#!/usr/bin/env python3
"""auto_writer.py가 생성한 linkedin_post.json을 읽어 LinkedIn에 포스팅한다.

토큰 만료(401/403) 시에는 워크플로 전체를 실패시키지 않고
graceful skip 한다 — 블로그 발행은 LinkedIn보다 우선이며,
LinkedIn 토큰은 60일 주기로 수동 재발급이 필요하다.
"""
import os, json, sys, requests

ACCESS_TOKEN = os.environ.get("LI_ACCESS_TOKEN", "")
POST_FILE = "linkedin_post.json"


def get_person_urn(headers):
    resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
    resp.raise_for_status()
    sub = resp.json()["sub"]
    print("LinkedIn 사용자: " + sub)
    return "urn:li:person:" + sub


def create_post(urn, text, headers):
    body = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=body,
    )
    resp.raise_for_status()
    print("포스트 업로드 완료")
    return resp.json()


def main():
    if not os.path.exists(POST_FILE):
        print("linkedin_post.json 없음 — 건너뜀")
        return

    if not ACCESS_TOKEN:
        print("[skip] LI_ACCESS_TOKEN 비어있음 — LinkedIn 포스팅 건너뜀")
        return

    with open(POST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = data.get("text", "")
    if not text:
        print("포스트 텍스트 비어있음 — 건너뜀")
        return

    print("포스트 제목: " + data.get("title", ""))
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        urn = get_person_urn(headers)
        result = create_post(urn, text, headers)
        print("완료: " + str(result.get("id", "")))
        os.remove(POST_FILE)
        print("linkedin_post.json 삭제")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status in (401, 403):
            print("[skip] LinkedIn 토큰 만료/권한 없음 (HTTP " + str(status) + ")")
            print("       Settings > Secrets > LI_ACCESS_TOKEN 재발급 필요 (60일 만료)")
            print("       https://www.linkedin.com/developers/apps → OAuth 2.0 token generator")
            # 워크플로 전체를 실패시키지 않음 — 블로그 발행은 이미 성공
            sys.exit(0)
        raise


if __name__ == "__main__":
    main()
