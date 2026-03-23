#!/usr/bin/env python3
import os
import json
import random
import time
import requests
from datetime import datetime
import google.generativeai as genai

INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")
INSTAGRAM_TOKEN = os.environ.get("INSTAGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TOPICS = [
    {"text": "글램핑 창업 준비 핵심 체크리스트", "region": "광주·전남", "hashtags": "#글램핑창업 #글램핑시공 #WOCS #전남글램핑 #글램핑텐트"},
    {"text": "사파리 텐트 vs 돔 텐트 비교", "region": "전남", "hashtags": "#사파리텐트 #돔텐트 #글램핑구조물 #WOCS #글램핑창업"},
    {"text": "글램핑 구조물 내구성 선택 기준", "region": "전남·전북", "hashtags": "#글램핑구조물 #천막시공 #WOCS #글램핑 #어닝시공"},
    {"text": "여수 순천 담양 글램핑 입지 비교", "region": "전남", "hashtags": "#여수글램핑 #순천글램핑 #담양글램핑 #전남글램핑 #WOCS"},
    {"text": "글램핑 1동 설치 비용과 기간 현실", "region": "광주·전남", "hashtags": "#글램핑창업비용 #글램핑시공 #WOCS #글램핑텐트 #전남"},
    {"text": "겨울 글램핑 방한 구조물 선택법", "region": "전남", "hashtags": "#겨울글램핑 #글램핑구조물 #WOCS #전남글램핑 #글램핑창업"},
    {"text": "지자체 글램핑 공모사업 신청 팁", "region": "전남·전북", "hashtags": "#글램핑공모사업 #지자체글램핑 #WOCS #전남 #글램핑창업"},
    {"text": "WOCS 특허 무용접 유니버설 조인트", "region": "화순", "hashtags": "#WOCS #무용접조인트 #글램핑특허 #글램핑구조물 #화순"},
    {"text": "고흥 보성 장흥 글램핑 부지 분석", "region": "전남", "hashtags": "#고흥글램핑 #보성글램핑 #장흥글램핑 #전남글램핑 #WOCS"},
    {"text": "글램핑 수익 극대화 운영 전략", "region": "전남", "hashtags": "#글램핑수익 #글램핑창업 #WOCS #전남글램핑 #글램핑운영"},
]

IMAGE_URLS = {
    "사파리": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=1080&q=80",
    "돔": "https://images.unsplash.com/photo-1533575770077-052fa2c609fc?w=1080&q=80",
    "겨울": "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=1080&q=80",
    "여수": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&q=80",
    "담양": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1080&q=80",
    "default": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=1080&q=80",
}


def get_image_url(topic_text):
    for key in IMAGE_URLS:
        if key in topic_text:
            return IMAGE_URLS[key]
    return IMAGE_URLS["default"]


def generate_caption(topic):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
당신은 WOCS 대표 김우성입니다. 16년 경력 글램핑 구조물 전문가.
Instagram 캡션을 작성하세요.

주제: {topic['text']}
지역: {topic['region']}

규칙:
- 첫 줄: 강한 훅 문장 (이모지 1개 포함)
- 본문: 실용 정보 3~4줄
- {topic['region']} 자연스럽게 1~2회 포함
- 마지막 줄: "자세히 보기 -> wocs.kr"
- 줄바꿈 2번으로 단락 구분
- 해시태그는 포함하지 말 것 (별도 추가)
- 전체 1500자 이내

캡션만 출력.
"""
    response = model.generate_content(prompt)
    caption = response.text.strip()
    caption += "\n\n" + topic["hashtags"]
    return caption


def post_to_instagram(image_url, caption):
    # Step 1: 미디어 컨테이너 생성
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    container_res = requests.post(container_url, data={
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_TOKEN,
    })
    container_data = container_res.json()

    if "id" not in container_data:
        print("컨테이너 생성 실패: " + json.dumps(container_data, ensure_ascii=False))
        return False

    creation_id = container_data["id"]
    print("컨테이너 생성: " + creation_id)
    time.sleep(10)

    # Step 2: 게시
    publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": INSTAGRAM_TOKEN,
    })
    publish_data = publish_res.json()

    if "id" in publish_data:
        print("Instagram 포스팅 성공: " + publish_data["id"])
        return True
    else:
        print("게시 실패: " + json.dumps(publish_data, ensure_ascii=False))
        return False


def get_today_topic():
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


if __name__ == "__main__":
    print("=" * 50)
    print("WOCS Instagram 자동 포스터 시작")
    print("=" * 50)

    if not all([INSTAGRAM_USER_ID, INSTAGRAM_TOKEN, GEMINI_API_KEY]):
        print("환경변수 누락")
        exit(1)

    topic = get_today_topic()
    print("오늘 주제: " + topic["text"])

    image_url = get_image_url(topic["text"])
    print("이미지: " + image_url)

    caption = generate_caption(topic)
    print("캡션:\n" + caption + "\n")

    result = post_to_instagram(image_url, caption)
    if result:
        print("Instagram 자동 포스팅 완료!")
    else:
        print("포스팅 실패")
        exit(1)
