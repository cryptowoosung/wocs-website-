#!/usr/bin/env python3
import os
import json
import random
import time
import requests
import urllib.parse
from datetime import datetime
import google.generativeai as genai

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
THREADS_TOKEN = os.environ.get("THREADS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

TOPICS = [
    {"text": "글램핑 창업 준비할 때 가장 먼저 해야 할 것", "region": "광주·전남"},
    {"text": "사파리 텐트 vs 돔 텐트 수익 비교", "region": "전남"},
    {"text": "글램핑 구조물 내구성 선택 기준", "region": "전남·전북"},
    {"text": "2026 지자체 글램핑 공모사업 신청 핵심 팁", "region": "전남"},
    {"text": "글램핑 1동 설치 기간과 비용 현실", "region": "광주·전남"},
    {"text": "WOCS 특허 무용접 유니버설 조인트 장점", "region": "화순"},
    {"text": "겨울 글램핑 방한 구조물 선택법", "region": "전남·전북"},
    {"text": "글램핑 부지 선정 핵심 체크리스트", "region": "전남"},
    {"text": "여수 순천 담양 글램핑 입지 비교 분석", "region": "전남"},
    {"text": "글램핑 창업 투자비 회수 기간 현실", "region": "광주·전남"},
    {"text": "구례 보성 장흥 글램핑 수요 분석", "region": "전남"},
    {"text": "글램핑 단지 조성 절차 완전 정리", "region": "전남·전북"},
]

IMAGE_KEYWORDS = {
    "글램핑": "glamping tent nature",
    "사파리": "safari tent outdoor",
    "돔": "dome tent glamping",
    "창업": "glamping resort",
    "수익": "glamping business",
    "부지": "nature camping site",
    "구조물": "glamping structure",
    "겨울": "winter glamping snow",
    "여수": "korean nature coast",
    "담양": "bamboo forest korea",
    "default": "glamping korea nature",
}

FALLBACK_IMAGES = {
    "glamping tent nature": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=1080&q=80",
    "safari tent outdoor": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=1080&q=80",
    "dome tent glamping": "https://images.unsplash.com/photo-1533575770077-052fa2c609fc?w=1080&q=80",
    "glamping resort": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1080&q=80",
    "glamping business": "https://images.unsplash.com/photo-1496545672447-f699b503d270?w=1080&q=80",
    "nature camping site": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1080&q=80",
    "glamping structure": "https://images.unsplash.com/photo-1487730116645-74489c95b41b?w=1080&q=80",
    "winter glamping snow": "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=1080&q=80",
    "korean nature coast": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&q=80",
    "bamboo forest korea": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1080&q=80",
    "glamping korea nature": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=1080&q=80",
}


def get_image_url(topic_text):
    keyword = "default"
    for k in IMAGE_KEYWORDS:
        if k in topic_text:
            keyword = k
            break
    search_query = IMAGE_KEYWORDS[keyword]

    if UNSPLASH_ACCESS_KEY:
        try:
            encoded = urllib.parse.quote(search_query)
            url = "https://api.unsplash.com/photos/random?query=" + encoded + "&orientation=landscape&client_id=" + UNSPLASH_ACCESS_KEY
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                img = res.json()["urls"]["regular"]
                print("Unsplash API 이미지: " + img[:60] + "...")
                return img
        except Exception as e:
            print("Unsplash API 오류: " + str(e))

    return FALLBACK_IMAGES.get(search_query, FALLBACK_IMAGES["glamping korea nature"])


def generate_content(topic):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
당신은 WOCS 대표 김우성입니다. 16년 경력 글램핑 구조물 전문가.
전남 화순에서 제조·시공. Threads 계정 @woosung_tent 운영.

주제: {topic['text']}
지역: {topic['region']}

아래 규칙으로 Threads 포스팅 작성:

[규칙]
- 350~450자 이내 (공백 포함 절대 500자 초과 금지)
- 첫 줄: 강한 훅 (질문 또는 반전 사실) — "안녕하세요" 절대 금지
- 중간: 실용 정보 3~4줄 (수치 또는 현장 경험 포함)
- {topic['region']} 지역명 1~2회 자연스럽게 포함
- 마지막 줄: "더 궁금한 점은 wocs.kr 에서 확인하세요" 형식으로 자연스럽게
- 해시태그 5개: #글램핑창업 #글램핑시공 #WOCS #전남글램핑 + 주제관련 1개
- 이모지 2~3개만
- 광고 느낌 없이 정보성으로

포스팅 내용만 출력. 설명 없이.
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def post_to_threads(text, image_url=None):
    container_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"

    if image_url:
        data = {
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": text,
            "access_token": THREADS_TOKEN,
        }
    else:
        data = {
            "media_type": "TEXT",
            "text": text,
            "access_token": THREADS_TOKEN,
        }

    container_res = requests.post(container_url, data=data)
    container_data = container_res.json()

    if "id" not in container_data:
        print("컨테이너 생성 실패: " + json.dumps(container_data, ensure_ascii=False))
        if image_url:
            print("이미지 없이 텍스트만 재시도...")
            return post_to_threads(text, image_url=None)
        return False

    creation_id = container_data["id"]
    print("컨테이너 생성: " + creation_id)
    time.sleep(5)

    publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": THREADS_TOKEN,
    })
    publish_data = publish_res.json()

    if "id" in publish_data:
        print("Threads 포스팅 성공: " + publish_data["id"])
        return True
    else:
        print("게시 실패: " + json.dumps(publish_data, ensure_ascii=False))
        return False


def get_today_topic():
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


if __name__ == "__main__":
    print("=" * 50)
    print("WOCS Threads 자동 포스터 시작")
    print("=" * 50)

    if not all([THREADS_USER_ID, THREADS_TOKEN, GEMINI_API_KEY]):
        print("환경변수 누락")
        exit(1)

    topic = get_today_topic()
    print("오늘 주제: " + topic["text"])

    content = generate_content(topic)
    print("\n생성된 콘텐츠:\n" + content + "\n")

    if len(content) > 490:
        content = content[:490]
        print("글자수 초과 -> 490자로 자름")

    image_url = get_image_url(topic["text"])
    print("이미지 URL: " + image_url[:80] + "...")

    result = post_to_threads(content, image_url=image_url)
    if result:
        print("Threads 자동 포스팅 완료!")
    else:
        print("포스팅 실패")
        exit(1)
