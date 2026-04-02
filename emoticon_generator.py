#!/usr/bin/env python3
"""
WOCS Emoticon Auto Generator
- n8n 워크플로우를 GitHub Actions용 Python으로 완전 대체
- 매일 자동 실행: 캐릭터 기획 → 32개 이미지 생성 → Google Drive 업로드 → 로그 → 알림
"""

import os
import sys
import json
import re
import base64
import time
import random
import requests
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
import struct
import zlib
import io
import math
import tempfile
from PIL import Image

# ============================================================
# 환경변수 로드
# ============================================================
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]

# Cloudinary 설정
CLOUDINARY_CLOUD_NAME = os.environ["CLOUDINARY_CLOUD_NAME"]
CLOUDINARY_API_KEY = os.environ["CLOUDINARY_API_KEY"]
CLOUDINARY_API_SECRET = os.environ["CLOUDINARY_API_SECRET"]

# Google Sheets 설정
SPREADSHEET_ID = "1OGZplXhNReH5M6rbNHH-ENjA_yJqIhorxSRSi3SYqmg"
SHEET_NAME = "이모티콘_캐릭터_로그"

# Google Drive 설정
DRIVE_PARENT_FOLDER = os.environ.get("DRIVE_PARENT_FOLDER_ID", "")  # WOCS_emoticons 폴더 ID

# 모델 설정
IMAGE_MODEL = "gpt-image-1.5"
IMAGE_QUALITY = "low"  # 메모리 절약 (GitHub Actions는 7GB라 medium도 가능하지만 비용 절약)
IMAGE_SIZE = "1024x1024"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# 한국 시간
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime("%Y-%m-%d")


# ============================================================
# Google API 인증
# ============================================================
def get_google_credentials():
    """서비스 계정 JSON으로 Google API 액세스 토큰 발급"""
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    creds.refresh(Request())
    return creds


def google_headers(creds):
    return {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}


# ============================================================
# Step 1: Google Sheets에서 이전 캐릭터 목록 읽기
# ============================================================
def read_previous_characters(creds):
    """이모티콘_캐릭터_로그 시트에서 최근 20개 캐릭터명 추출"""
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"
        f"/values/{SHEET_NAME}!A:B"
    )
    resp = requests.get(url, headers=google_headers(creds))
    resp.raise_for_status()
    rows = resp.json().get("values", [])

    # 헤더 제외, 캐릭터명(B열) 추출
    characters = []
    for row in rows[1:]:
        if len(row) >= 2 and row[1].strip():
            characters.append(row[1].strip())

    prev = ", ".join(characters[-20:]) if characters else "없음"
    print(f"[Step 1] 이전 캐릭터 {len(characters)}개 로드, 최근 20개: {prev[:100]}...")
    return prev


# ============================================================
# Step 2: Claude Haiku로 캐릭터 기획
# ============================================================
def plan_character(previous_characters):
    """Claude Haiku에게 새 캐릭터 JSON 생성 요청"""

    system_prompt = """너는 카카오/라인/OGQ 이모티콘 전문 캐릭터 기획자다.
매번 완전히 다른 신선한 캐릭터를 제안해야 한다.
이전에 만든 캐릭터와 절대 겹치면 안 된다.
반드시 JSON만 출력하고 다른 텍스트는 절대 포함하지 마라.
emotions 배열은 반드시 정확히 32개여야 한다."""

    user_prompt = f"""오늘의 이모티콘 캐릭터를 새로 기획해라.
이전 캐릭터: {previous_characters}

[캐릭터 조건]
- 동물 또는 귀여운 사물 캐릭터
- 성격과 콘셉트가 뚜렷해야 함
- 이전 캐릭터와 종류/색상/테마 모두 달라야 함

[스타일 선택 - 반드시 아래 비중 준수]
- meme-mz: 80% 확률 선택
- healing: 15% 확률 선택
- rough-sketch: 5% 확률 선택

[스타일별 동작 가이드]
meme-mz 스타일:
- 현실 공감형: 월요병, 야근, 현타, 피로, 번아웃, 지각, 시험기간
- 자조적 유머: 통장잔고 확인, 배달음식 기다리기, 카톡 읽씹, 인스타 눈팅
- 과장 리액션: 기절, 멘탈붕괴, 울면서 웃기, 억울함, 당황, 헛웃음
- MZ 감성 동작 예시: lying flat exhausted, existential crisis stare, pretending to be fine, checking empty wallet, forced smile, monday morning suffering, doom scrolling, rage quitting

healing 스타일:
- 따뜻한 위로, 응원, 소소한 행복, 귀여운 일상
- 동작 예시: giving a warm hug, cheering you on, cozy sleeping, drinking hot tea, happy dancing, sending love

rough-sketch 스타일:
- 거칠고 즉흥적인 선, B급 감성, 낙서체
- 과장되고 엉성한 표현, 의도적으로 삐뚤어진 느낌

[emotions 필수 규칙]
- 정확히 32개 (부족하면 심사 탈락)
- 영어로 작성
- 선택된 스타일에 맞는 동작 70% + 범용 감정 30%
- 범용 감정: happy, sad, angry, surprised, love, crying, laughing, waving, thinking, sleeping

[출력 형식 - JSON만, 다른 텍스트 절대 금지]
{{"character_name": "캐릭터명(한국어)", "character_desc": "A [구체적 색상] [동물/사물], flat 2D kawaii illustration, thick black outlines, white exterior stroke, fully colored with vibrant solid colors, transparent background", "theme": "테마명", "style": "meme-mz/healing/rough-sketch 중 하나", "emotions": ["동작1", ..., "동작32"]}}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": CLAUDE_MODEL,
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
    )
    resp.raise_for_status()
    raw_text = resp.json()["content"][0]["text"]

    # JSON 추출 (Claude가 텍스트를 앞뒤에 붙여도 처리)
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        raise ValueError(f"Claude가 JSON을 반환하지 않음: {raw_text[:200]}")

    data = json.loads(match.group(0))

    # emotions 32개 보정
    while len(data["emotions"]) < 32:
        data["emotions"].append(f"extra_action_{len(data['emotions']) + 1}")
    data["emotions"] = data["emotions"][:32]

    print(f"[Step 2] 캐릭터 기획 완료: {data['character_name']} / {data['theme']} / {data['style']}")
    print(f"         emotions {len(data['emotions'])}개")
    return data


# ============================================================
# Step 3: 프롬프트 생성
# ============================================================
def generate_prompts(data):
    """캐릭터 데이터에서 32개 이미지 프롬프트 생성"""

    style_guide = ""
    if data["style"] == "meme-mz":
        style_guide = "Exaggerated MZ/meme reactions - over-the-top expressions, dramatic poses, self-deprecating humor visible in posture"
    elif data["style"] == "healing":
        style_guide = "Soft, warm, comforting expressions and poses, pastel tones preferred"
    elif data["style"] == "rough-sketch":
        style_guide = "Slightly rough lines, spontaneous B-grade aesthetic, intentionally imperfect strokes"

    base_style = f"""{data['character_desc']}

VISUAL REQUIREMENTS (STRICT):
- Flat 2D kawaii illustration style
- Thick black outlines on all edges
- MANDATORY white stroke/border (3-5px thick) between the black outline and transparent background
- The layering must be: character body → thick black outline → white stroke → transparent background
- This white border is NOT optional - must be clearly visible around entire character silhouette
- FULL solid color fills throughout entire character body - absolutely NO hollow or empty areas
- Vibrant, saturated colors - NO grayscale, NO black-and-white only

COMPOSITION:
- Transparent background only
- Character centered with 10px margin on all sides
- NO text, NO speech bubbles, NO background elements

EMOTICON STYLE:
- Kakaotalk/LINE sticker style
- Exaggerated facial expressions matching the action
- Personality clearly visible in every pose
- {style_guide}"""

    prompts = []
    for i, emotion in enumerate(data["emotions"]):
        prompts.append(
            {
                "index": i + 1,
                "emotion": emotion,
                "prompt": f"{base_style}\nAction: {emotion}",
                "filename": f"{str(i + 1).zfill(2)}.png",
            }
        )

    folder_name = f"{TODAY}_{data['character_name']}"
    print(f"[Step 3] 프롬프트 {len(prompts)}개 생성 완료, 폴더: {folder_name}")
    return prompts, folder_name


# ============================================================
# 애니메이션 헬퍼 함수
# ============================================================
def save_apng(frames, out_path, delay=12):
    def png_chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    w, h = frames[0].size
    n = len(frames)
    out = io.BytesIO()
    out.write(b'\x89PNG\r\n\x1a\n')
    out.write(png_chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)))
    out.write(png_chunk(b'acTL', struct.pack('>II', n, 0)))
    seq = 0
    for i, frame in enumerate(frames):
        fctl = (struct.pack('>I', seq) + struct.pack('>II', w, h) +
                struct.pack('>II', 0, 0) + struct.pack('>HH', delay, 100) +
                struct.pack('>BB', 1, 0))
        out.write(png_chunk(b'fcTL', fctl))
        seq += 1
        fb = io.BytesIO()
        frame.save(fb, format='PNG')
        fd = fb.getvalue()
        pos = 8
        while pos < len(fd):
            l = struct.unpack('>I', fd[pos:pos+4])[0]
            ct = fd[pos+4:pos+8]
            cd = fd[pos+8:pos+8+l]
            pos += 12 + l
            if ct == b'IDAT':
                if i == 0:
                    out.write(png_chunk(b'IDAT', cd))
                else:
                    out.write(png_chunk(b'fdAT', struct.pack('>I', seq) + cd))
                    seq += 1
    out.write(png_chunk(b'IEND', b''))
    with open(out_path, 'wb') as f:
        f.write(out.getvalue())


def save_gif(frames, out_path, delay=12):
    gif_frames = []
    for frame in frames:
        bg = Image.new("RGB", frame.size, (255, 255, 255))
        bg.paste(frame, mask=frame.split()[3])
        gif_frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=256))
    gif_frames[0].save(
        out_path, save_all=True, append_images=gif_frames[1:],
        loop=0, duration=delay * 10, disposal=2
    )


def save_webp(frames, out_path, delay=120):
    frames[0].save(
        out_path, format="WEBP", save_all=True,
        append_images=frames[1:], loop=0, duration=delay,
        lossless=False, quality=85
    )


def make_frames_from_bytes(base_bytes, size, emotion=""):
    """감정별 다른 5프레임 애니메이션 생성"""
    base_img = Image.open(io.BytesIO(base_bytes)).convert("RGBA")
    w, h = size
    frames = []

    emotion_lower = emotion.lower()

    # 감정별 움직임 분류
    if any(k in emotion_lower for k in ["wave", "hello", "bye", "waving"]):
        # 좌우 흔들기
        offsets_x = [0, int(w*0.04), 0, int(-w*0.04), 0]
        offsets_y = [0, 0, 0, 0, 0]
    elif any(k in emotion_lower for k in ["cry", "sad", "tear", "sob"]):
        # 아래로 처짐 (슬픔)
        offsets_x = [0, 0, 0, 0, 0]
        offsets_y = [0, int(h*0.03), int(h*0.05), int(h*0.03), 0]
    elif any(k in emotion_lower for k in ["angry", "anger", "stomp", "mad"]):
        # 좌우 떨림 (화남)
        offsets_x = [0, int(w*0.03), int(-w*0.03), int(w*0.03), 0]
        offsets_y = [0, 0, 0, 0, 0]
    elif any(k in emotion_lower for k in ["jump", "cheer", "celebrat", "excit", "joy"]):
        # 크게 bounce (기쁨)
        offsets_x = [0, 0, 0, 0, 0]
        offsets_y = [0, int(-h*0.08), int(-h*0.12), int(-h*0.08), 0]
    elif any(k in emotion_lower for k in ["think", "wonder", "question"]):
        # 작게 좌우 (생각)
        offsets_x = [0, int(w*0.02), int(w*0.03), int(w*0.02), 0]
        offsets_y = [0, int(-h*0.01), int(-h*0.02), int(-h*0.01), 0]
    elif any(k in emotion_lower for k in ["sleep", "drowsy", "zzz"]):
        # 천천히 아래 (졸음)
        offsets_x = [0, 0, 0, 0, 0]
        offsets_y = [0, int(h*0.02), int(h*0.04), int(h*0.02), 0]
    elif any(k in emotion_lower for k in ["laugh", "haha", "lol"]):
        # 좌우+위아래 (웃음)
        offsets_x = [0, int(w*0.02), 0, int(-w*0.02), 0]
        offsets_y = [0, int(-h*0.02), int(-h*0.04), int(-h*0.02), 0]
    else:
        # 기본 bounce
        offsets_x = [0, 0, 0, 0, 0]
        offsets_y = [0, int(-h*0.03), int(-h*0.06), int(-h*0.03), 0]

    for ox, oy in zip(offsets_x, offsets_y):
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        resized = base_img.resize(size, Image.LANCZOS)
        canvas.paste(resized, (ox, oy), resized)
        frames.append(canvas)

    return frames


# ============================================================
# Step 4-5: 이미지 생성 + Cloudinary 업로드 (32개 순차)
# ============================================================
def generate_and_upload(prompts, folder_name):
    """gpt-image-1.5로 이미지 생성 후 Google Drive에 업로드"""
    success_count = 0
    fail_count = 0

    for item in prompts:
        idx = item["index"]
        filename = item["filename"]
        emotion = item["emotion"]

        print(f"  [{idx:02d}/32] {emotion}...", end=" ", flush=True)

        # --- 이미지 생성 ---
        try:
            img_resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": IMAGE_MODEL,
                    "prompt": item["prompt"],
                    "size": IMAGE_SIZE,
                    "quality": IMAGE_QUALITY,
                    "background": "transparent",
                    "output_format": "png",
                    "n": 1,
                },
                timeout=120,
            )
            img_resp.raise_for_status()
            b64_data = img_resp.json()["data"][0]["b64_json"]
        except Exception as e:
            print(f"❌ 생성 실패: {e}")
            fail_count += 1
            continue

        # --- Cloudinary 업로드 ---
        try:
            image_bytes = base64.b64decode(b64_data)
            del b64_data

            upload_resp = requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload",
                auth=(CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET),
                data={
                    "public_id": f"emoticons/{folder_name}/{filename.replace('.png','')}",
                    "folder": "",
                    "use_filename": "true",
                    "unique_filename": "false",
                    "overwrite": "true",
                },
                files={"file": (filename, image_bytes, "image/png")},
                timeout=60,
            )
            upload_resp.raise_for_status()
            del image_bytes

            print(f"✅ 업로드 완료")
            success_count += 1

        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            fail_count += 1
            continue

        # API 속도 제한 방지
        if idx < len(prompts):
            time.sleep(1)

    print(f"\n[Step 5] 이미지 생성 완료: 성공 {success_count}, 실패 {fail_count}")
    return success_count, fail_count


# ============================================================
# Step 6: Google Sheets 캐릭터 로그 기록
# ============================================================
def log_to_sheets(creds, data):
    """이모티콘_캐릭터_로그 시트에 오늘 기록 추가"""
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"
        f"/values/{SHEET_NAME}!A:G:append?valueInputOption=USER_ENTERED"
    )
    row = [
        TODAY,
        data["character_name"],
        data["theme"],
        data["style"],
        "pending",  # OGQ
        "pending",  # 라인
        "pending",  # 카카오
    ]
    resp = requests.post(
        url, headers=google_headers(creds), json={"values": [row]}
    )
    resp.raise_for_status()
    print(f"[Step 6] Sheets 로그 기록 완료")


# ============================================================
# Step 7: Telegram 알림
# ============================================================
def send_telegram(data, success_count, fail_count, folder_name):
    """Telegram으로 완료 알림 전송"""
    message = (
        f"🐾 이모티콘 생성 완료!\n"
        f"📅 {TODAY}\n"
        f"🎨 캐릭터: {data['character_name']}\n"
        f"🎭 테마: {data['theme']}\n"
        f"✨ 스타일: {data['style']}\n"
        f"✅ 성공: {success_count}개 / ❌ 실패: {fail_count}개\n"
        f"📁 Google Drive: WOCS_emoticons/{folder_name}\n"
        f"👉 다음: Claude Code 변환 → OGQ → 라인 제출"
    )

    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
    )
    if resp.ok:
        print(f"[Step 7] Telegram 알림 전송 완료")
    else:
        print(f"[Step 7] Telegram 알림 실패: {resp.text}")


# ============================================================
# 메인 실행
# ============================================================
def main():
    print("=" * 60)
    print(f"WOCS Emoticon Auto Generator - {TODAY}")
    print("=" * 60)

    # Google 인증
    creds = get_google_credentials()

    # Step 1: 이전 캐릭터 읽기
    prev_chars = read_previous_characters(creds)

    # Step 2: 캐릭터 기획
    data = plan_character(prev_chars)

    # Step 3: 프롬프트 생성
    prompts, folder_name = generate_prompts(data)

    # Step 4-5: 이미지 생성 + Cloudinary 업로드
    print(f"\n[Step 4-5] 32개 이미지 생성 시작...")
    success_count, fail_count = generate_and_upload(prompts, folder_name)

    # ============================================================
    # Step 5.4: 플랫폼별 정적 PNG 리사이즈 및 Cloudinary 업로드
    # ============================================================
    print("\n[Step 5.4] 정적 이모티콘 플랫폼별 리사이즈 중...")

    def resize_canvas(src_bytes, size, padding=10):
        img = Image.open(io.BytesIO(src_bytes)).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        cw, ch = img.size
        max_w = size[0] - padding * 2
        max_h = size[1] - padding * 2
        scale = min(max_w / cw, max_h / ch)
        resized = img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        px = (size[0] - resized.width) // 2
        py = (size[1] - resized.height) // 2
        canvas.paste(resized, (px, py), resized)
        return canvas

    static_tmp = tempfile.mkdtemp()
    kakao_static_dir = os.path.join(static_tmp, "kakao")
    line_static_dir = os.path.join(static_tmp, "line")
    ogq_static_dir = os.path.join(static_tmp, "ogq")
    for d in [kakao_static_dir, line_static_dir, ogq_static_dir]:
        os.makedirs(d, exist_ok=True)

    CLOUD = os.environ["CLOUDINARY_CLOUD_NAME"]
    API_KEY = os.environ["CLOUDINARY_API_KEY"]
    API_SECRET = os.environ["CLOUDINARY_API_SECRET"]

    for idx in range(len(data["emotions"])):
        filename = f"{str(idx+1).zfill(2)}.png"
        cloudinary_url = f"https://res.cloudinary.com/{CLOUD}/image/upload/emoticons/{folder_name}/{filename}"

        try:
            img_resp = requests.get(cloudinary_url, timeout=30)
            img_resp.raise_for_status()
            src_bytes = img_resp.content

            # 카카오: 360×360 (32개)
            kakao_img = resize_canvas(src_bytes, (360, 360))
            kakao_path = os.path.join(kakao_static_dir, filename)
            kakao_img.save(kakao_path, "PNG", optimize=True, compress_level=9)

            # 라인: 370×320 (24개만)
            if idx < 24:
                line_img = resize_canvas(src_bytes, (370, 320))
                line_path = os.path.join(line_static_dir, filename)
                line_img.save(line_path, "PNG", optimize=True, compress_level=9)

            # OGQ: 740×640 (24개만, O01 형식)
            if idx < 24:
                ogq_img = resize_canvas(src_bytes, (740, 640))
                ogq_path = os.path.join(ogq_static_dir, f"O{idx+1:02d}.png")
                ogq_img.save(ogq_path, "PNG", optimize=True, compress_level=9)

            print(f"  [{idx+1}] 리사이즈 완료")

        except Exception as e:
            print(f"  [{idx+1}] 리사이즈 실패: {e}")

    # 첫 번째 이미지로 main.png, tab.png, icon 생성
    try:
        first_url = f"https://res.cloudinary.com/{CLOUD}/image/upload/emoticons/{folder_name}/01.png"
        first_resp = requests.get(first_url, timeout=30)
        first_bytes = first_resp.content

        for d, name, size, pad in [
            (line_static_dir, "main.png", (240, 240), 8),
            (line_static_dir, "tab.png", (96, 74), 4),
            (ogq_static_dir, "main.png", (240, 240), 8),
            (ogq_static_dir, "tab.png", (96, 74), 4),
            (kakao_static_dir, "icon_78x78.png", (78, 78), 4),
        ]:
            resize_canvas(first_bytes, size, pad).save(os.path.join(d, name), "PNG")
    except Exception as e:
        print(f"  main/tab/icon 생성 실패: {e}")

    # Cloudinary 업로드
    print("  정적 PNG Cloudinary 업로드 중...")
    for platform, d in [("kakao", kakao_static_dir), ("line", line_static_dir), ("ogq", ogq_static_dir)]:
        for fname in sorted(os.listdir(d)):
            with open(os.path.join(d, fname), "rb") as f:
                requests.post(
                    f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                    auth=(API_KEY, API_SECRET),
                    data={"public_id": f"emoticons/{folder_name}/{platform}_static/{fname}"},
                    files={"file": f}
                )

    print("✅ 정적 리사이즈 완료!")

    # ============================================================
    # Step 5.5: 플랫폼별 애니메이션 이모티콘 생성 및 Cloudinary 업로드
    # ============================================================
    print("\n[Step 5.5] 움직이는 이모티콘 생성 중...")

    tmp_dir = tempfile.mkdtemp()

    line_dir = os.path.join(tmp_dir, "line_anim")
    ogq_dir = os.path.join(tmp_dir, "ogq_anim")
    kakao_dir = os.path.join(tmp_dir, "kakao_anim")
    for d in [line_dir, ogq_dir, kakao_dir]:
        os.makedirs(d, exist_ok=True)

    # 카카오 WEBP 대상: 0,1,2번 인덱스 (첫 3개)
    kakao_anim_indices = {0, 1, 2}

    anim_success = 0
    for idx in range(min(24, len(data["emotions"]))):
        emotion = data["emotions"][idx]
        filename = f"{str(idx+1).zfill(2)}.png"
        cloudinary_url = f"https://res.cloudinary.com/{os.environ['CLOUDINARY_CLOUD_NAME']}/image/upload/emoticons/{folder_name}/{filename}"

        try:
            # Cloudinary에서 원본 이미지 다운로드
            img_resp = requests.get(cloudinary_url, timeout=30)
            img_resp.raise_for_status()
            base_bytes = img_resp.content

            # 라인: APNG 320x270
            frames_line = make_frames_from_bytes(base_bytes, (320, 270), emotion)
            line_path = os.path.join(line_dir, f"{idx+1:02d}.png")
            save_apng(frames_line, line_path)

            # OGQ: GIF 740x640
            frames_ogq = make_frames_from_bytes(base_bytes, (740, 640), emotion)
            ogq_path = os.path.join(ogq_dir, f"O{idx+1:02d}.gif")
            save_gif(frames_ogq, ogq_path)

            # 카카오: WEBP 360x360 (첫 3개만)
            if idx in kakao_anim_indices:
                frames_kakao = make_frames_from_bytes(base_bytes, (360, 360), emotion)
                kakao_path = os.path.join(kakao_dir, f"{idx+1:02d}.webp")
                save_webp(frames_kakao, kakao_path)

            anim_success += 1
            print(f"  [{idx+1}/24] 애니메이션 완료: {emotion[:30]}")

        except Exception as e:
            print(f"  [{idx+1}/24] 애니메이션 실패: {e}")

    # Cloudinary 애니메이션 업로드
    print("  Cloudinary 애니메이션 업로드 중...")
    CLOUD = os.environ["CLOUDINARY_CLOUD_NAME"]
    API_KEY = os.environ["CLOUDINARY_API_KEY"]
    API_SECRET = os.environ["CLOUDINARY_API_SECRET"]

    for fname in sorted(os.listdir(line_dir)):
        with open(os.path.join(line_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/line_anim/{fname}"},
                files={"file": f}
            )

    for fname in sorted(os.listdir(ogq_dir)):
        with open(os.path.join(ogq_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/ogq_anim/{fname}"},
                files={"file": f}
            )

    for fname in sorted(os.listdir(kakao_dir)):
        with open(os.path.join(kakao_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/kakao_anim/{fname}"},
                files={"file": f}
            )

    print(f"✅ 애니메이션 완료: {anim_success}/24개")

    # Step 6: Sheets 로그
    log_to_sheets(creds, data)

    # Step 7: Telegram 알림
    send_telegram(data, success_count, fail_count, folder_name)

    print("\n" + "=" * 60)
    print(f"전체 완료! 성공: {success_count}/32")
    print("=" * 60)

    # 실패가 있으면 exit code 1
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
