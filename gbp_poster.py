#!/usr/bin/env python3
import os, requests
from datetime import datetime

CLIENT_ID = os.environ["GBP_CLIENT_ID"]
CLIENT_SECRET = os.environ["GBP_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GBP_REFRESH_TOKEN"]

POSTS = [
    {
        "summary": (
            "글램핑 창업, WOCS와 함께 시작하세요!\n\n"
            "전남 화순 기반 글램핑 구조물 전문 제조·시공 업체 WOCS입니다.\n"
            "사파리텐트, 돔텐트, 모듈러 글램핑까지 맞춤 시공을 제공합니다.\n\n"
            "문의: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "글램핑 시공 단가가 궁금하신가요?\n\n"
            "WOCS는 합리적인 가격으로 고품질 글램핑 구조물을 시공합니다.\n"
            "텐트 종류별 견적을 무료로 상담해 드립니다.\n\n"
            "무료 견적 문의: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "사파리텐트로 감성 글램핑장을 만들어 보세요!\n\n"
            "WOCS의 사파리텐트는 내구성과 디자인을 모두 갖췄습니다.\n"
            "전국 어디서든 시공 가능합니다.\n\n"
            "상담: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "돔텐트 글램핑, 트렌드를 선도하는 WOCS!\n\n"
            "독특한 돔형 구조물로 차별화된 글램핑장을 완성하세요.\n"
            "설계부터 시공까지 원스톱으로 진행합니다.\n\n"
            "문의: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "어닝·천막 시공도 WOCS에 맡기세요!\n\n"
            "카페, 식당, 야외 공간에 딱 맞는 어닝과 천막 구조물을 시공합니다.\n"
            "30년 경력의 전문 시공팀이 함께합니다.\n\n"
            "문의: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "4계절 운영 가능한 글램핑텐트, WOCS가 만듭니다!\n\n"
            "단열과 방수를 고려한 설계로 사계절 내내 운영할 수 있습니다.\n"
            "글램핑 창업을 꿈꾸신다면 WOCS와 상담하세요.\n\n"
            "전화: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
    {
        "summary": (
            "글램핑 구조물 OEM 제작도 가능합니다!\n\n"
            "WOCS는 자체 공장에서 맞춤 제작하여 중간 마진 없이 공급합니다.\n"
            "대량 주문 및 특수 사양도 상담해 주세요.\n\n"
            "문의: 010-4337-0582\n"
            "홈페이지: wocs.kr"
        ),
    },
]


def get_access_token():
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    })
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print("Access Token 발급 완료")
    return token


def get_account(headers):
    resp = requests.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers,
    )
    resp.raise_for_status()
    accounts = resp.json().get("accounts", [])
    if not accounts:
        raise Exception("GBP 계정 없음")
    account = accounts[0]["name"]
    print("계정: " + account)
    return account


def get_location(account, headers):
    resp = requests.get(
        "https://mybusinessbusinessinformation.googleapis.com/v1/"
        + account + "/locations",
        headers=headers,
    )
    resp.raise_for_status()
    locations = resp.json().get("locations", [])
    if not locations:
        raise Exception("위치 없음")
    location = locations[0]["name"]
    print("위치: " + location)
    return location


def create_post(account, location, headers, post_data):
    url = (
        "https://mybusiness.googleapis.com/v4/"
        + account + "/" + location.split("/")[-1]
        + "/localPosts"
    )
    # v4 API uses {account}/locations/{locationId}/localPosts
    url = (
        "https://mybusiness.googleapis.com/v4/"
        + account + "/locations/" + location.split("/")[-1]
        + "/localPosts"
    )
    body = {
        "languageCode": "ko",
        "summary": post_data["summary"],
        "topicType": "STANDARD",
        "callToAction": {
            "actionType": "CALL",
            "url": "https://wocs.kr",
        },
    }
    resp = requests.post(url, headers=headers, json=body)
    resp.raise_for_status()
    print("포스트 업로드 완료")
    return resp.json()


def main():
    day_index = datetime.now().weekday()  # 0=월 ~ 6=일
    post_data = POSTS[day_index]
    print("오늘 요일 인덱스: " + str(day_index))

    token = get_access_token()
    headers = {"Authorization": "Bearer " + token}

    account = get_account(headers)
    location = get_location(account, headers)
    result = create_post(account, location, headers, post_data)
    print("완료: " + str(result.get("name", "")))


if __name__ == "__main__":
    main()
