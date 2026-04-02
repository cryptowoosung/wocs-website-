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
def save_apng(frames, out_path, delay=15, loops=4):
    """APNG 저장 - 라인 공식 규격 준수
    - 5~20프레임
    - loop: 1~4회 (무한루프 금지)
    - 각 프레임 픽셀이 달라야 업로드 오류 방지
    """
    def png_chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    # 프레임 픽셀 고유성 보장: 각 프레임에 1픽셀 차이 강제 적용
    unique_frames = []
    for idx, frame in enumerate(frames):
        f = frame.copy()
        px = f.getpixel((0, 0))
        # alpha 채널에 미세한 차이 추가 (육안 식별 불가)
        new_alpha = max(0, min(255, (px[3] if len(px) > 3 else 255) - idx))
        f.putpixel((0, 0), (px[0], px[1], px[2], new_alpha))
        unique_frames.append(f)

    w, h = unique_frames[0].size
    n = len(unique_frames)

    out = io.BytesIO()
    out.write(b'\x89PNG\r\n\x1a\n')
    out.write(png_chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)))
    out.write(png_chunk(b'acTL', struct.pack('>II', n, loops)))  # loops=4 (무한루프 금지)
    seq = 0
    for i, frame in enumerate(unique_frames):
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

    data = out.getvalue()
    with open(out_path, 'wb') as f:
        f.write(data)

    # 파일 크기 검증 (라인 최대 1MB)
    size_kb = len(data) / 1024
    if size_kb > 1024:
        print(f"  ⚠️ APNG 크기 초과: {size_kb:.0f}KB > 1MB ({out_path})")
    return size_kb


def save_gif(frames, out_path, delay=15):
    """GIF 저장 - 투명 배경을 흰색으로 합성 (GIF는 완전 투명 미지원)"""
    gif_frames = []
    for frame in frames:
        bg = Image.new("RGBA", frame.size, (255, 255, 255, 255))
        bg.paste(frame, mask=frame.split()[3] if frame.mode == 'RGBA' else None)
        rgb = bg.convert("RGB")
        # 고품질 팔레트 변환
        p = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        gif_frames.append(p)
    gif_frames[0].save(
        out_path, save_all=True, append_images=gif_frames[1:],
        loop=0, duration=delay * 10, disposal=2, optimize=True
    )


def save_webp(frames, out_path, delay=120):
    frames[0].save(
        out_path, format="WEBP", save_all=True,
        append_images=frames[1:], loop=0, duration=delay,
        lossless=False, quality=85
    )
    size_kb = os.path.getsize(out_path) / 1024
    if size_kb > 150:
        # 품질 낮춰서 재시도
        frames[0].save(
            out_path, format="WEBP", save_all=True,
            append_images=frames[1:], loop=0, duration=delay,
            lossless=False, quality=60
        )
        size_kb = os.path.getsize(out_path) / 1024
        if size_kb > 150:
            print(f"  ⚠️ WEBP 150KB 초과: {size_kb:.0f}KB ({out_path})")
    return size_kb


def make_frames_from_bytes(base_bytes, size, emotion="", api_key=None, character_desc=""):
    """
    GPT Image로 프레임2, 프레임3 실제 생성.
    실패시 위치이동 폴백.
    """
    import requests as req

    def resize_frame(img_bytes, size):
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        ratio = min(size[0]/img.width, size[1]/img.height)
        nw, nh = int(img.width*ratio), int(img.height*ratio)
        resized = img.resize((nw, nh), Image.LANCZOS)
        canvas.paste(resized, ((size[0]-nw)//2, (size[1]-nh)//2), resized)
        return canvas

    def fallback_frames(base_bytes, size, emotion):
        """위치이동 폴백"""
        base_img = Image.open(io.BytesIO(base_bytes)).convert("RGBA")
        w, h = size
        e = emotion.lower()
        def px(r): return int(w*r)
        def py(r): return int(h*r)
        if any(k in e for k in ["wave","hello","bye","farewell"]):
            ox=[0,px(0.05),0,px(-0.05),0]; oy=[0,0,0,0,0]
        elif any(k in e for k in ["jump","celebrat","excit","hooray","yay","cheer"]):
            ox=[0,0,0,0,0]; oy=[0,py(-0.08),py(-0.13),py(-0.08),0]
        elif any(k in e for k in ["cry","sad","tear","sob"]):
            ox=[0,0,0,0,0]; oy=[0,py(0.03),py(0.06),py(0.03),0]
        elif any(k in e for k in ["angry","mad","rage","stomp"]):
            ox=[0,px(0.04),px(-0.04),px(0.04),0]; oy=[0,0,0,0,0]
        elif any(k in e for k in ["love","heart","kiss"]):
            ox=[0,0,0,0,0]; oy=[0,py(-0.03),py(-0.06),py(-0.03),0]
        elif any(k in e for k in ["laugh","lol","haha"]):
            ox=[0,px(0.02),px(-0.02),px(0.02),0]; oy=[0,py(-0.02),py(-0.04),py(-0.02),0]
        else:
            ox=[0,0,0,0,0]; oy=[0,py(-0.03),py(-0.06),py(-0.03),0]
        frames=[]
        for i in range(5):
            canvas=Image.new("RGBA",size,(0,0,0,0))
            resized=base_img.resize(size,Image.LANCZOS)
            canvas.paste(resized,(ox[i],oy[i]),resized)
            frames.append(canvas)
        return frames

    if not api_key:
        return fallback_frames(base_bytes, size, emotion)

    # 감정별 프레임2,3 프롬프트
    e = emotion.lower()
    if any(k in e for k in ["wave","hello","bye"]):
        f2_action = "right arm/paw raised halfway up, mid-wave"
        f3_action = "right arm/paw fully raised high, peak wave"
    elif any(k in e for k in ["jump","celebrat","excit","cheer","hooray"]):
        f2_action = "body slightly lifted off ground, arms beginning to raise"
        f3_action = "fully jumping in air, both arms raised high, big smile"
    elif any(k in e for k in ["cry","sad","tear","sob"]):
        f2_action = "eyes beginning to well up with tears, mouth slightly open"
        f3_action = "big tears streaming down face, mouth wide open crying"
    elif any(k in e for k in ["angry","mad","rage","stomp","furious"]):
        f2_action = "eyebrows furrowed, fists clenched, body tensing"
        f3_action = "peak anger, fists raised, face very red, steam from head"
    elif any(k in e for k in ["laugh","lol","haha","giggle"]):
        f2_action = "mouth opening wider, eyes beginning to squint"
        f3_action = "holding belly laughing, eyes closed, mouth wide open"
    elif any(k in e for k in ["love","heart","kiss","adore"]):
        f2_action = "leaning forward slightly, eyes half closed, lips puckered"
        f3_action = "blowing kiss, heart floating from mouth, eyes closed happy"
    elif any(k in e for k in ["think","wonder","ponder","question"]):
        f2_action = "one finger raised to chin, looking upward thoughtfully"
        f3_action = "finger tapping chin, question mark appearing above head"
    elif any(k in e for k in ["sleep","drowsy","tired","zzz"]):
        f2_action = "eyes half closed, head drooping slightly"
        f3_action = "eyes fully closed, head tilted, ZZZ bubble above"
    elif any(k in e for k in ["surpris","shock","gasp"]):
        f2_action = "eyes beginning to widen, mouth starting to open"
        f3_action = "eyes fully wide, mouth wide open shocked, hands on cheeks"
    elif any(k in e for k in ["shy","embarrass","blush"]):
        f2_action = "cheeks turning pink, looking slightly away"
        f3_action = "face fully blushing red, both paws covering cheeks"
    elif any(k in e for k in ["eat","food","delicious","yummy"]):
        f2_action = "food approaching mouth, eyes lighting up"
        f3_action = "eating with big bite, eyes sparkling with delight"
    elif any(k in e for k in ["run","sprint","dash","rush"]):
        f2_action = "leaning forward, one leg lifted, arms pumping"
        f3_action = "full sprint, both arms pumping, speed lines behind"
    else:
        f2_action = f"mid-action {emotion}, halfway through the movement"
        f3_action = f"peak action {emotion}, maximum expression of the emotion"

    base_prompt = f"{character_desc}, kawaii emoticon sticker style, flat 2D illustration, thick black outlines, transparent background, centered composition, single character only"

    results = [resize_frame(base_bytes, size)]  # 프레임1: 원본

    for frame_num, action in [(2, f2_action), (3, f3_action)]:
        try:
            prompt = f"Keep EXACTLY the same character from the reference image. Same face, body, colors, style. Only change the action/pose to: {action}. Kawaii emoticon sticker, flat 2D illustration, thick black outlines, transparent background."
            # edit API - 원본 이미지 참조해서 캐릭터 일관성 유지
            import io as _io
            resp = req.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {api_key}"},
                files={
                    "image": ("frame1.png", _io.BytesIO(base_bytes), "image/png"),
                },
                data={
                    "model": "gpt-image-1",
                    "prompt": prompt,
                    "size": "1024x1024",
                    "quality": "low",
                    "n": "1",
                },
                timeout=120
            )
            resp.raise_for_status()
            img_bytes = base64.b64decode(resp.json()["data"][0]["b64_json"])
            results.append(resize_frame(img_bytes, size))
            print(f"      frame{frame_num} OK")
        except Exception as e:
            print(f"      frame{frame_num} fail({e}), fallback")
            fb = fallback_frames(base_bytes, size, emotion)
            results.append(fb[frame_num])

    # 5프레임으로 확장: 1->2->3->2->1 (자연스러운 루프)
    if len(results) >= 3:
        frames = [results[0], results[1], results[2], results[1].copy(), results[0].copy()]
    else:
        frames = fallback_frames(base_bytes, size, emotion)

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
def send_telegram(data, success_count, fail_count, folder_name, anim_success=0, anim_failed=None):
    """Telegram으로 완료 알림 전송"""
    anim_failed = anim_failed or []
    anim_status = f"✅ 애니메이션: {anim_success}/24개 성공"
    if anim_failed:
        anim_status += f"\n❌ 실패: {', '.join(anim_failed[:5])}"

    cloudinary_anim_url = f"https://console.cloudinary.com/console/media_library/folders/emoticons/{folder_name}"

    message = (
        f"🐾 이모티콘 생성 완료!\n"
        f"📅 {TODAY}\n"
        f"🎨 캐릭터: {data['character_name']}\n"
        f"🎭 테마: {data['theme']}\n"
        f"✨ 스타일: {data['style']}\n"
        f"✅ 성공: {success_count}개 / ❌ 실패: {fail_count}개\n"
        f"📁 Google Drive: WOCS_emoticons/{folder_name}\n"
        f"\n🎬 {anim_status}\n"
        f"📦 라인 ZIP / 카카오 ZIP Cloudinary에 저장됨\n"
        f"🔗 {cloudinary_anim_url}\n"
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
    kakao_gif_dir = os.path.join(tmp_dir, "kakao_gif")
    for d in [line_dir, ogq_dir, kakao_dir, kakao_gif_dir]:
        os.makedirs(d, exist_ok=True)

    # 감정 강도 강한 것 우선 선택 (카카오 WEBP 3개)
    priority_keywords = ["excited", "cry", "angry", "jump", "celebrat", "love", "surprise", "laugh", "cheer"]
    kakao_anim_indices = set()
    for idx_k, emotion_k in enumerate(data["emotions"][:24]):
        if any(k in emotion_k.lower() for k in priority_keywords):
            kakao_anim_indices.add(idx_k)
        if len(kakao_anim_indices) >= 3:
            break
    if len(kakao_anim_indices) < 3:
        for idx_k in range(24):
            kakao_anim_indices.add(idx_k)
            if len(kakao_anim_indices) >= 3:
                break

    anim_success = 0
    anim_failed = []
    for idx in range(min(24, len(data["emotions"]))):
        emotion = data["emotions"][idx]
        filename = f"{str(idx+1).zfill(2)}.png"
        cloudinary_url = f"https://res.cloudinary.com/{os.environ['CLOUDINARY_CLOUD_NAME']}/image/upload/emoticons/{folder_name}/{filename}"

        try:
            # Cloudinary에서 원본 이미지 다운로드
            img_resp = requests.get(cloudinary_url, timeout=30)
            img_resp.raise_for_status()
            base_bytes = img_resp.content

            # GPT Image로 프레임 생성 (1024x1024 기준으로 한번만 생성)
            print(f"    GPT Image 프레임 생성 중...")
            base_frames = make_frames_from_bytes(
                base_bytes, (1024, 1024), emotion,
                api_key=os.environ.get("OPENAI_API_KEY"),
                character_desc=data.get("character_desc", "cute kawaii animal character")
            )

            # 각 플랫폼 크기로 리사이즈
            def resize_frames(frames, size):
                result = []
                for f in frames:
                    canvas = Image.new("RGBA", size, (0,0,0,0))
                    ratio = min(size[0]/f.width, size[1]/f.height)
                    nw, nh = int(f.width*ratio), int(f.height*ratio)
                    resized = f.resize((nw,nh), Image.LANCZOS)
                    canvas.paste(resized, ((size[0]-nw)//2,(size[1]-nh)//2), resized)
                    result.append(canvas)
                return result

            # 라인: APNG 320x270
            frames_line = resize_frames(base_frames, (320, 270))
            line_path = os.path.join(line_dir, f"{idx+1:02d}.png")
            save_apng(frames_line, line_path)

            # OGQ: GIF 740x640
            frames_ogq = resize_frames(base_frames, (740, 640))
            ogq_path = os.path.join(ogq_dir, f"O{idx+1:02d}.gif")
            save_gif(frames_ogq, ogq_path)

            # 카카오: WEBP 360x360 (감정 강도 기반 3개) + 시안용 GIF
            if idx in kakao_anim_indices:
                frames_kakao = resize_frames(base_frames, (360, 360))
                kakao_path = os.path.join(kakao_dir, f"{idx+1:02d}.webp")
                save_webp(frames_kakao, kakao_path)
                # 시안 제출용 GIF도 생성
                kakao_gif_path = os.path.join(kakao_gif_dir, f"{idx+1:02d}.gif")
                save_gif(frames_kakao, kakao_gif_path)

            anim_success += 1
            print(f"  [{idx+1}/24] 애니메이션 완료: {emotion[:30]}")

        except Exception as e:
            print(f"  [{idx+1}/24] 애니메이션 실패: {e}")
            anim_failed.append(f"{idx+1}: {str(e)[:50]}")

    # 라인 ZIP 생성
    import zipfile as zf
    line_zip_path = os.path.join(tmp_dir, "line_anim.zip")
    with zf.ZipFile(line_zip_path, "w", zf.ZIP_DEFLATED) as zfile:
        for fname in sorted(os.listdir(line_dir)):
            zfile.write(os.path.join(line_dir, fname), fname)
    line_zip_kb = os.path.getsize(line_zip_path) / 1024
    print(f"  라인 ZIP: {line_zip_kb:.0f}KB {'✅' if line_zip_kb < 61440 else '❌ 60MB 초과'}")

    # 카카오 ZIP 생성 (WEBP + GIF 전부 포함)
    kakao_zip_path = os.path.join(tmp_dir, "kakao_anim.zip")
    with zf.ZipFile(kakao_zip_path, "w", zf.ZIP_DEFLATED) as zfile:
        for fname in sorted(os.listdir(kakao_dir)):
            zfile.write(os.path.join(kakao_dir, fname), f"webp/{fname}")
        for fname in sorted(os.listdir(kakao_gif_dir)):
            zfile.write(os.path.join(kakao_gif_dir, fname), f"gif_시안/{fname}")

    # Cloudinary 애니메이션 업로드
    print("  Cloudinary 애니메이션 업로드 중...")
    CLOUD = os.environ["CLOUDINARY_CLOUD_NAME"]
    API_KEY = os.environ["CLOUDINARY_API_KEY"]
    API_SECRET = os.environ["CLOUDINARY_API_SECRET"]

    # APNG 업로드 (라인) - raw 타입
    for fname in sorted(os.listdir(line_dir)):
        with open(os.path.join(line_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/raw/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/line_anim/{fname}", "resource_type": "raw"},
                files={"file": f}
            )

    # GIF 업로드 (OGQ) - image 타입
    for fname in sorted(os.listdir(ogq_dir)):
        with open(os.path.join(ogq_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/ogq_anim/{fname}", "resource_type": "image"},
                files={"file": f}
            )

    # WEBP 업로드 (카카오) - image 타입
    for fname in sorted(os.listdir(kakao_dir)):
        with open(os.path.join(kakao_dir, fname), "rb") as f:
            requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUD}/image/upload",
                auth=(API_KEY, API_SECRET),
                data={"public_id": f"emoticons/{folder_name}/kakao_anim/{fname}", "resource_type": "image"},
                files={"file": f}
            )

    # ZIP 업로드 (라인, 카카오)
    with open(line_zip_path, "rb") as f:
        requests.post(
            f"https://api.cloudinary.com/v1_1/{CLOUD}/raw/upload",
            auth=(API_KEY, API_SECRET),
            data={"public_id": f"emoticons/{folder_name}/line_anim.zip"},
            files={"file": f}
        )
    with open(kakao_zip_path, "rb") as f:
        requests.post(
            f"https://api.cloudinary.com/v1_1/{CLOUD}/raw/upload",
            auth=(API_KEY, API_SECRET),
            data={"public_id": f"emoticons/{folder_name}/kakao_anim.zip"},
            files={"file": f}
        )

    print(f"✅ 애니메이션 완료: {anim_success}/24개")

    # 임시 폴더 정리
    import shutil
    try:
        shutil.rmtree(tmp_dir)
        shutil.rmtree(static_tmp)
        print("✅ 임시 파일 정리 완료")
    except Exception as e:
        print(f"⚠️ 임시 파일 정리 실패: {e}")

    # Step 6: Sheets 로그
    log_to_sheets(creds, data)

    # Step 7: Telegram 알림
    send_telegram(data, success_count, fail_count, folder_name, anim_success, anim_failed)

    # 비용 출력
    anim_cost = min(24, len(data["emotions"])) * 2 * 0.011
    print(f"  애니메이션 추가 비용: ${anim_cost:.3f} (24개 × 2프레임 × $0.011)")

    print("\n" + "=" * 60)
    print(f"전체 완료! 성공: {success_count}/32")
    print("=" * 60)

    # 실패가 있으면 exit code 1
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
