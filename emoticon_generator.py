#!/usr/bin/env python3
"""
WOCS Emoticon Auto Generator
- n8n 워크플로우를 GitHub Actions용 Python으로 완전 대체
- 매일 자동 실행: 캐릭터 기획 → 24개 이미지 생성 → Google Drive 업로드 → 로그 → 알림
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

# rembg 배경 제거 (gpt-image-1.5 아티팩트 해결)
from rembg import new_session, remove
from PIL import ImageFilter
from io import BytesIO

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
emotions 배열은 반드시 정확히 24개여야 한다."""

    user_prompt = f"""오늘의 이모티콘 캐릭터를 새로 기획해라.
이전 캐릭터: {previous_characters}

[캐릭터 조건]
- 동물 또는 귀여운 사물 캐릭터
- 성격과 콘셉트가 뚜렷해야 함
- 이전 캐릭터와 종류/색상/테마 모두 달라야 함

[스타일 선택 - 아래 비중 준수 (OGQ 인기 6종)]
- sticker-pop: 25% (OGQ 표준 진한 외곽선 + 선명 컬러)
- meme-mz: 25% (MZ 밈 / 과장 리액션 / 자조적 유머)
- cute-round: 15% (통통 동글동글 / 아기 같은 귀여움)
- healing-pastel: 15% (파스텔톤 / 따뜻하고 포근한 분위기)
- minimal-line: 10% (미니멀 라인 드로잉 / 2-3색 제한 / 스칸디나비안)
- rough-doodle: 10% (손그림 낙서체 / 거친 펜선 / B급 감성)

[스타일별 한줄 가이드 - Claude 내부 참고용]
sticker-pop: 선명한 팝 컬러, 동적 포즈, OGQ 베스트셀러 표준
meme-mz: 월요병/현타/번아웃/통장잔고/야근/카톡읽씹 등 MZ 일상
cute-round: 공 형태에 가까운 비율, 짧은 팔다리, 큰 머리
healing-pastel: 민트/피치/라벤더 톤, 따뜻한 눈빛, 위로 제스처
minimal-line: 단순한 선, 파스텔 단색, 비어있는 여백 활용
rough-doodle: 공책 모서리 낙서 감성, 삐뚤빼뚤 일부러 엉성

[emotions 규칙 - 매우 중요]
- 반드시 정확히 24개
- 각 원소는 {{"action": "영어 구체 동작", "text_overlay": "한글 8자 이내" 또는 null}} 객체
- 24개 중 정확히 10개에만 text_overlay에 한글 텍스트 (나머지 14개는 null)
- 한글 텍스트 예시 (매우 짧게, 최대 8자): "퇴근하자", "월요병...", "현타옴", "존버중", "배고파", "사랑해", "화이팅!", "피곤해", "고마워", "미안해", "ㅠㅠ", "ㅎㅎ", "ㅇㅈ?", "ㄱㅊ?", "주말각", "칼퇴각", "출근싫어", "오늘도수고"
- action은 영어로, 한국 MZ 상황을 구체화 (예: "lying flat on bed completely exhausted after overtime")
- 한국 MZ 공감 action 예시 (최소 14개 포함):
  lying flat on bed after work / checking empty bank account shocked / doom scrolling at 3am /
  monday morning zombie walk / forced smile during meeting / existential stare out window /
  screaming into pillow / rage keyboard smashing / pay day excited dance / awkward silent eye rolling /
  waiting for delivery food impatiently / reading kakao message pretending to be away /
  scrolling instagram jealously / running late to work / crying while laughing /
  existential crisis over coffee / pretending to work busy / falling asleep at desk

[character_desc 필수 형식]
"A [구체적 색상] [동물/사물], flat 2D kawaii illustration, thick black outlines, white exterior stroke, fully colored with vibrant solid colors, transparent background"

[출력 형식 - JSON만, 다른 텍스트 절대 금지]
{{"character_name": "캐릭터명(한국어)", "character_desc": "...", "theme": "테마명", "style": "6종 중 하나", "emotions": [{{"action": "...", "text_overlay": "..."}}, {{"action": "...", "text_overlay": null}}, ...]}}"""

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

    # emotions 구조 정규화 (구형 string 포맷 호환)
    normalized: list[dict] = []
    for e in data.get("emotions", []):
        if isinstance(e, str):
            normalized.append({"action": e, "text_overlay": None})
        elif isinstance(e, dict):
            action = str(e.get("action") or e.get("emotion") or "idle pose").strip()
            text = e.get("text_overlay")
            if isinstance(text, str):
                text = text.strip() or None
                if text and len(text) > 10:
                    text = text[:10]
            else:
                text = None
            normalized.append({"action": action, "text_overlay": text})

    # 24개 보정
    while len(normalized) < 24:
        normalized.append({"action": f"extra_pose_{len(normalized) + 1}", "text_overlay": None})
    normalized = normalized[:24]

    # 10:14 비율 강제
    FALLBACK_TEXTS = [
        "퇴근하자", "월요병...", "현타옴", "존버중", "배고파",
        "사랑해", "화이팅!", "피곤해", "고마워", "ㅠㅠ",
    ]
    text_idx = [i for i, e in enumerate(normalized) if e["text_overlay"]]
    if len(text_idx) != 10:
        all_idx = list(range(24))
        random.shuffle(all_idx)
        target = set(all_idx[:10])
        fallback_iter = iter(FALLBACK_TEXTS)
        for i, e in enumerate(normalized):
            if i in target:
                if not e["text_overlay"]:
                    e["text_overlay"] = next(fallback_iter, "ㅎㅎ")
            else:
                e["text_overlay"] = None
        print(f"[Step 2] 10:14 비율 보정: Claude {len(text_idx)}개 → 10개로 재조정")

    data["emotions"] = normalized
    text_count = sum(1 for e in normalized if e["text_overlay"])

    # 스타일 6종 화이트리스트 검증
    VALID_STYLES = {"sticker-pop", "meme-mz", "cute-round", "healing-pastel", "minimal-line", "rough-doodle"}
    if data.get("style") not in VALID_STYLES:
        data["style"] = "sticker-pop"
        print(f"[Step 2] style 화이트리스트 이탈 → sticker-pop 대체")

    print(f"[Step 2] 캐릭터 기획 완료: {data['character_name']} / {data['theme']} / {data['style']}")
    print(f"         emotions 24개 (한글 {text_count} : 영문 {24 - text_count})")
    return data


# ============================================================
# Step 3: 프롬프트 생성 (OGQ 인기 6종 스타일)
# ============================================================
STYLE_GUIDES: dict[str, str] = {
    "sticker-pop": (
        "Classic OGQ sticker style — bold and punchy. Vibrant saturated solid colors, "
        "clear expressive faces, dynamic confident poses, high-contrast palette."
    ),
    "meme-mz": (
        "Exaggerated Korean MZ meme reactions — over-the-top expressions, dramatic poses, "
        "self-deprecating humor visible in posture, relatable everyday suffering, "
        "slightly messy but readable energy."
    ),
    "cute-round": (
        "Ultra round and chubby proportions, soft circular shapes, tiny stubby limbs, "
        "oversized head relative to body, baby-like adorable features, "
        "sparkly innocent eyes, blushed cheeks."
    ),
    "healing-pastel": (
        "Soft pastel palette (mint green, peach, lavender, cream yellow), gentle warm "
        "expressions, cozy comforting atmosphere, rounded gentle shapes, healing vibes."
    ),
    "minimal-line": (
        "Clean minimalist design, 2 to 3 flat colors maximum, simple geometric shapes, "
        "Scandinavian-inspired restraint, generous negative space, refined subtle lines "
        "(outlines remain but thinner than default)."
    ),
    "rough-doodle": (
        "Hand-drawn notebook-margin doodle feel, intentionally rough imperfect lines, "
        "slightly wobbly outlines, spontaneous B-grade aesthetic, pen-sketch texture, "
        "crooked on purpose."
    ),
}


def generate_prompts(data: dict) -> tuple[list[dict], str]:
    """캐릭터 데이터에서 24개 이미지 프롬프트 생성"""

    style_guide = STYLE_GUIDES.get(data["style"], STYLE_GUIDES["sticker-pop"])

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
- NO text, NO letters, NO Hangul, NO speech bubbles, NO background elements (text is added later in post-processing)

EMOTICON STYLE:
- Kakaotalk/LINE/OGQ sticker style
- Exaggerated facial expressions matching the action
- Personality clearly visible in every pose
- {style_guide}"""

    prompts: list[dict] = []
    for i, emotion in enumerate(data["emotions"]):
        action = emotion["action"]
        text_overlay = emotion.get("text_overlay")
        prompts.append(
            {
                "index": i + 1,
                "emotion": action,
                "text_overlay": text_overlay,
                "prompt": f"{base_style}\nAction: {action}",
                "filename": f"{str(i + 1).zfill(2)}.png",
            }
        )

    folder_name = f"{TODAY}_{data['character_name']}"
    text_count = sum(1 for p in prompts if p["text_overlay"])
    print(
        f"[Step 3] 프롬프트 {len(prompts)}개 생성 완료 "
        f"(한글오버레이 {text_count}개 / 폴더: {folder_name})"
    )
    return prompts, folder_name


# ============================================================
# Step 4-5: 이미지 생성 + Cloudinary 업로드 (24개 순차)
# ============================================================
def _generate_image_from_text(prompt: str) -> str:
    """text-to-image (generations) — 1번 이미지 또는 fallback용"""
    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": IMAGE_MODEL,
            "prompt": prompt,
            "size": IMAGE_SIZE,
            "quality": IMAGE_QUALITY,
            "background": "transparent",
            "output_format": "png",
            "n": 1,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["b64_json"]


def _generate_image_from_reference(prompt: str, reference_png: bytes) -> str:
    """image-to-image (edits) — 2~24번, 1번 이미지를 레퍼런스로"""
    edit_preamble = (
        "Use the attached reference image as the exact character design template. "
        "Keep the exact same character, colors, proportions, outline style, and art style. "
        "Change ONLY the pose, expression, and action as described below. "
        "Do not redesign the character.\n\n"
    )
    resp = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        data={
            "model": IMAGE_MODEL,
            "prompt": edit_preamble + prompt,
            "size": IMAGE_SIZE,
            "quality": IMAGE_QUALITY,
            "background": "transparent",
            "output_format": "png",
            "n": 1,
        },
        files={"image": ("reference.png", reference_png, "image/png")},
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["b64_json"]


def generate_and_upload(prompts, folder_name):
    """gpt-image-1.5로 이미지 생성 후 Cloudinary 업로드.

    1번은 text-to-image로 생성하고, 2~24번은 1번을 레퍼런스로 사용해 edits
    엔드포인트로 생성 → 24개 캐릭터 일관성 확보.
    1번이 실패하면 레퍼런스가 없으므로 전체가 text-to-image로 fallback.
    """
    success_count = 0
    fail_count = 0
    reference_png: bytes | None = None  # rembg 처리 후, overlay 이전 상태

    for item in prompts:
        idx = item["index"]
        filename = item["filename"]
        emotion = item["emotion"]

        print(f"  [{idx:02d}/24] {emotion}...", end=" ", flush=True)

        # --- 이미지 생성 (1번=text / 2~24번=ref 기반 edits) ---
        try:
            if reference_png is None:
                b64_data = _generate_image_from_text(item["prompt"])
                print("[t2i]", end=" ", flush=True)
            else:
                try:
                    b64_data = _generate_image_from_reference(item["prompt"], reference_png)
                    print("[ref]", end=" ", flush=True)
                except Exception as ref_err:
                    # edits 실패 시 text-to-image로 fallback (1회만)
                    print(f"[ref 실패→t2i fallback: {ref_err}]", end=" ", flush=True)
                    b64_data = _generate_image_from_text(item["prompt"])
        except Exception as e:
            print(f"❌ 생성 실패: {e}")
            fail_count += 1
            continue

        # --- Cloudinary 업로드 ---
        try:
            image_bytes = base64.b64decode(b64_data)
            del b64_data

            # rembg 후처리 (배경 제거 + 흰 테두리)
            try:
                image_bytes = process_image_with_rembg(image_bytes)
            except Exception as e:
                print(f"[rembg] 후처리 실패, 원본 사용: {e}")

            # 1번 이미지가 성공하면 레퍼런스로 저장 (overlay 적용 이전 상태)
            if reference_png is None:
                reference_png = image_bytes
                print("[ref저장]", end=" ", flush=True)

            # 한글 텍스트 오버레이 (24개 중 10개만)
            overlay_text = item.get("text_overlay")
            if overlay_text:
                try:
                    image_bytes = overlay_korean_text(image_bytes, overlay_text)
                    print(f"[text '{overlay_text}']", end=" ", flush=True)
                except Exception as e:
                    print(f"[overlay 실패: {e}]", end=" ", flush=True)

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
    text_count = sum(1 for e in data.get("emotions", []) if isinstance(e, dict) and e.get("text_overlay"))
    message = (
        f"🐾 이모티콘 생성 완료!\n"
        f"📅 {TODAY}\n"
        f"🎨 캐릭터: {data['character_name']}\n"
        f"🎭 테마: {data['theme']}\n"
        f"✨ 스타일: {data['style']}\n"
        f"✅ 성공: {success_count}개 / ❌ 실패: {fail_count}개\n"
        f"💬 한글텍스트 {text_count}개 / 이미지만 {24 - text_count}개\n"
        f"📁 Cloudinary: emoticons/{folder_name}\n"
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
# 한글 텍스트 오버레이 (PIL)
# ============================================================
KOREAN_FONT_CANDIDATES: tuple[str, ...] = (
    # GitHub Actions Ubuntu (fonts-nanum-extra)
    "/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf",
    "/usr/share/fonts/truetype/nanum/NanumSquareRoundEB.ttf",
    "/usr/share/fonts/truetype/nanum/NanumSquareB.ttf",
    # GitHub Actions Ubuntu (fonts-nanum)
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunpenB.ttf",
    # Noto CJK fallback (fonts-noto-cjk)
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    # Windows 로컬 개발 fallback
    "C:/Windows/Fonts/malgunbd.ttf",
    "C:/Windows/Fonts/malgun.ttf",
    # macOS fallback
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
)

_korean_font_cache: dict[int, "object"] = {}


def _load_korean_font(size: int):
    """한글 폰트 로딩 (size별 캐시)"""
    from PIL import ImageFont

    if size in _korean_font_cache:
        return _korean_font_cache[size]

    for path in KOREAN_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _korean_font_cache[size] = font
                return font
            except Exception:
                continue

    print("    [overlay] ⚠ 한글 폰트 미발견 → default 폰트 (한글 깨짐 가능)")
    font = ImageFont.load_default()
    _korean_font_cache[size] = font
    return font


def overlay_korean_text(image_bytes: bytes, text: str, position: str = "bottom") -> bytes:
    """PNG 이미지에 한글 텍스트 오버레이

    - 흰 글씨 + 검은 외곽선 (이모티콘 전통 스타일, 어떤 배경에도 가독)
    - 폰트 크기: 이미지 폭의 9%
    - position: "bottom"(기본) / "top"
    """
    from PIL import Image, ImageDraw

    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    width, height = img.size

    font_size = max(60, int(width * 0.09))
    font = _load_korean_font(font_size)
    stroke_w = max(4, font_size // 10)

    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) // 2 - bbox[0]
    if position == "top":
        y = int(height * 0.04) - bbox[1]
    else:
        y = height - text_h - int(height * 0.06) - bbox[1]

    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke_w,
        stroke_fill=(0, 0, 0, 255),
    )

    out = BytesIO()
    img.save(out, "PNG", optimize=True)
    return out.getvalue()


# ============================================================
# rembg 배경 제거 + 흰 테두리 (gpt-image-1.5 아티팩트 해결)
# ============================================================

_rembg_session = None


def get_rembg_session():
    """rembg 세션 싱글톤 (24개 이미지 처리 중 1회만 로드)"""
    global _rembg_session
    if _rembg_session is None:
        print("    [rembg] 모델 로딩 중 (birefnet-general)...")
        _rembg_session = new_session("birefnet-general")
        print("    [rembg] 모델 로드 완료")
    return _rembg_session


def process_image_with_rembg(image_bytes, stroke_width=6):
    """gpt-image-1.5 후처리: 배경 제거 + 밝기 감지 + 자동 흰 테두리

    캐릭터 밝기에 따라 테두리 두께 자동 조정:
    - 밝기 < 100: 10px (어두운 캐릭터)
    - 밝기 100~140: 8px (중간)
    - 밝기 > 140: 6px (밝은 캐릭터, 기본)
    """
    from PIL import Image
    import numpy as np

    img = Image.open(BytesIO(image_bytes))
    session = get_rembg_session()
    cleaned = remove(img, session=session).convert('RGBA')

    arr = np.array(cleaned)
    opaque_mask = arr[:, :, 3] > 200
    if np.any(opaque_mask):
        avg_brightness = arr[opaque_mask][:, :3].mean()
        if avg_brightness < 100:
            stroke_width = 10
            print(f"    [rembg] 어두운 캐릭터 (밝기 {avg_brightness:.0f}) -> 테두리 {stroke_width}px")
        elif avg_brightness < 140:
            stroke_width = 8
            print(f"    [rembg] 중간 밝기 (밝기 {avg_brightness:.0f}) -> 테두리 {stroke_width}px")
        else:
            print(f"    [rembg] 밝은 캐릭터 (밝기 {avg_brightness:.0f}) -> 테두리 {stroke_width}px")

    alpha = cleaned.split()[3]
    dilated = alpha.filter(ImageFilter.MaxFilter(stroke_width * 2 + 1))
    white_bg = Image.new('RGBA', cleaned.size, (255, 255, 255, 0))
    white_bg.putalpha(dilated)
    result = Image.alpha_composite(white_bg, cleaned)

    output = BytesIO()
    result.save(output, 'PNG', optimize=True)
    return output.getvalue()


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
    print(f"\n[Step 4-5] 24개 이미지 생성 시작...")
    success_count, fail_count = generate_and_upload(prompts, folder_name)

    # Step 6: Sheets 로그
    log_to_sheets(creds, data)

    # Step 7: Telegram 알림
    send_telegram(data, success_count, fail_count, folder_name)

    print("\n" + "=" * 60)
    print(f"전체 완료! 성공: {success_count}/24")
    print("=" * 60)

    # 실패가 있으면 exit code 1
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
