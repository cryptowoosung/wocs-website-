#!/usr/bin/env python3
"""auto_writer.py가 생성한 linkedin_post.json을 읽어 LinkedIn에 포스팅한다."""
import os, json, requests

ACCESS_TOKEN = os.environ["LI_ACCESS_TOKEN"]
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

    urn = get_person_urn(headers)
    result = create_post(urn, text, headers)
    print("완료: " + str(result.get("id", "")))

    os.remove(POST_FILE)
    print("linkedin_post.json 삭제")


if __name__ == "__main__":
    main()
