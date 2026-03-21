#!/usr/bin/env python3
import os, requests
from datetime import datetime

ACCESS_TOKEN = os.environ["LI_ACCESS_TOKEN"]

POSTS = [
    (
        "글램핑 창업, WOCS와 함께 시작하세요!\n\n"
        "전남 화순 기반 글램핑 구조물 전문 제조·시공 업체 WOCS입니다.\n"
        "사파리텐트, 돔텐트, 모듈러 글램핑까지 맞춤 시공을 제공합니다.\n\n"
        "문의: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#글램핑창업 #글램핑시공 #WOCS #사파리텐트 #돔텐트"
    ),
    (
        "글램핑 시공 단가가 궁금하신가요?\n\n"
        "WOCS는 합리적인 가격으로 고품질 글램핑 구조물을 시공합니다.\n"
        "텐트 종류별 견적을 무료로 상담해 드립니다.\n\n"
        "무료 견적 문의: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#글램핑시공단가 #글램핑견적 #WOCS #글램핑구조물"
    ),
    (
        "사파리텐트로 감성 글램핑장을 만들어 보세요!\n\n"
        "WOCS의 사파리텐트는 내구성과 디자인을 모두 갖췄습니다.\n"
        "전국 어디서든 시공 가능합니다.\n\n"
        "상담: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#사파리텐트 #감성글램핑 #WOCS #글램핑장만들기"
    ),
    (
        "돔텐트 글램핑, 트렌드를 선도하는 WOCS!\n\n"
        "독특한 돔형 구조물로 차별화된 글램핑장을 완성하세요.\n"
        "설계부터 시공까지 원스톱으로 진행합니다.\n\n"
        "문의: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#돔텐트 #글램핑트렌드 #WOCS #돔글램핑"
    ),
    (
        "어닝·천막 시공도 WOCS에 맡기세요!\n\n"
        "카페, 식당, 야외 공간에 딱 맞는 어닝과 천막 구조물을 시공합니다.\n"
        "30년 경력의 전문 시공팀이 함께합니다.\n\n"
        "문의: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#어닝시공 #천막구조물 #WOCS #야외인테리어"
    ),
    (
        "4계절 운영 가능한 글램핑텐트, WOCS가 만듭니다!\n\n"
        "단열과 방수를 고려한 설계로 사계절 내내 운영할 수 있습니다.\n"
        "글램핑 창업을 꿈꾸신다면 WOCS와 상담하세요.\n\n"
        "전화: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#4계절글램핑 #글램핑텐트 #WOCS #사계절운영"
    ),
    (
        "글램핑 구조물 OEM 제작도 가능합니다!\n\n"
        "WOCS는 자체 공장에서 맞춤 제작하여 중간 마진 없이 공급합니다.\n"
        "대량 주문 및 특수 사양도 상담해 주세요.\n\n"
        "문의: 010-4337-0582\n"
        "홈페이지: https://wocs.kr\n\n"
        "#글램핑OEM #맞춤제작 #WOCS #글램핑구조물"
    ),
]


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
    day_index = datetime.now().weekday()  # 0=월 ~ 6=일
    text = POSTS[day_index]
    print("오늘 요일 인덱스: " + str(day_index))

    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    urn = get_person_urn(headers)
    result = create_post(urn, text, headers)
    print("완료: " + str(result.get("id", "")))


if __name__ == "__main__":
    main()
