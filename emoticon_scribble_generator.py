#!/usr/bin/env python3
"""
WOCS 낙서풍(Scribble) 이모티콘 생성기.

기존 emoticon_generator.py와 분리된 별도 워크플로.
- 캐릭터 톤: 한국 인터넷 밈 풍 낙서 / 미니멀 / 단순 형태
- 시장: LINE 우선 (B급 친화), OGQ 보수적 (전략적 통과 시도)
- 카카오: 제외 (~3% 통과율)

기존 워크플로(emoticon.yml / emoticon_generator.py)는 절대 영향 없음.
재사용 함수(fill_alpha_holes / validate_alpha_holes / process_image_with_rembg)는
이 파일에 그대로 복제 — 모듈 의존성 없이 독립 실행.
"""
import os
import sys
import json
import re
import base64
import time
import random
import requests
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone, timedelta

from rembg import new_session, remove
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# === 환경 변수 ===
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
CLOUDINARY_CLOUD_NAME = os.environ['CLOUDINARY_CLOUD_NAME']
CLOUDINARY_API_KEY = os.environ['CLOUDINARY_API_KEY']
CLOUDINARY_API_SECRET = os.environ['CLOUDINARY_API_SECRET']

# === 상수 ===
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime('%Y-%m-%d')

IMAGE_MODEL = "gpt-image-1.5"
IMAGE_QUALITY = "low"
IMAGE_SIZE = "1024x1024"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

PREV_CHARACTERS_FILE = "prev_characters_scribble.json"  # 시리즈 분리
SERIES_PREFIX = "scribble"
KOREAN_FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumBrush.ttf"  # 손그림 폰트
KOREAN_FONT_FALLBACK = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"


# ============================================================
# 헬퍼
# ============================================================
def _is_dryrun() -> bool:
    """RUN_ONLY_FIRST 환경변수 truthy 판단 (boolean 'true' 호환).

    GitHub Actions의 workflow_dispatch boolean input은 'true'/'false' 문자열로
    전달되므로 '1'만 검사하던 기존 방식의 버그(쿠로 시리즈에서 발견)를 예방한다.
    """
    val = os.environ.get('RUN_ONLY_FIRST', '0').strip().lower()
    return val in ('1', 'true', 'yes', 'on')


def _ensure_unique_text_overlays(emotions: list) -> list:
    """text_overlay 중복 방지. 같은 한글이 두 번 이상 나오면 두 번째부터 None.

    쿠로 시리즈에서 Claude가 같은 한글을 중복 반환한 사례가 발견되어
    낙서풍에서는 처음부터 적용한다.
    """
    seen: set = set()
    duplicates: list = []
    for emo in emotions:
        text = (emo.get('text_overlay') or '').strip() if isinstance(emo, dict) else ''
        if text and text in seen:
            duplicates.append(text)
            emo['text_overlay'] = None
        elif text:
            seen.add(text)
    if duplicates:
        print(f"[중복 텍스트 제거] {len(duplicates)}개: {', '.join(duplicates)}")
    return emotions


# ============================================================
# 캐릭터 plan (Claude Haiku)
# ============================================================
SCRIBBLE_PLAN_SYSTEM = """너는 한국 인터넷 밈 풍의 '낙서풍' 이모티콘 캐릭터 기획자야.

영감: 한국 인터넷 커뮤니티에서 유행하는 낙서/밈 스타일.
초등학생이 5분 만에 그린 듯한 단순한 동그라미와 선만으로 구성된 캐릭터.
귀엽고 미니멀하지만 표정과 의도가 명확함.

캐릭터 조건:
- 동물 또는 사람 (단순한 형태)
- 단색 + 흰 배경 (그라디언트 X)
- 2D 평면, 음영 없음
- 표정/감정이 명확하게 드러남
- character_desc 필드에는 절대 실존 작가/유명인 이름 포함 금지
- character_desc는 캐릭터의 시각적 특징만 묘사 (예: "분홍색 둥근 곰", "노란 별 모양 친구")

이름은 짧고 어딘가 어색한 한글 (예: 멍충이, 짤짤이, 하찮이, 둘리, 쩌리)

emotions 24개 조건:
- 한글 텍스트 10개 (모두 unique, 중복 절대 없음)
- 이미지만 14개
- 직장/학교/일상 공감 밈 위주
- "월요병", "현타", "월급날", "퇴근", "ㅎㅎ", "존버", "미안", "화이팅" 같은 짧은 한국식 밈
- 한글은 5자 이내가 이상적

JSON 응답 형식 (반드시 이 구조 그대로):
{
  "character_name": "캐릭터 이름",
  "character_desc": "시각적 특징만 묘사 (인명 절대 금지)",
  "theme": "주제",
  "style": "scribble-meme",
  "emotions": [
    {"index": 1, "action": "...", "text_overlay": null},
    {"index": 2, "action": "...", "text_overlay": "월요병"},
    ...
  ]
}

다른 텍스트는 절대 포함하지 말고 JSON만 출력해."""


def plan_character_scribble(previous_characters: list) -> dict:
    """Claude Haiku에게 낙서풍 캐릭터 JSON 생성 요청"""
    prev_summary = ", ".join(
        c.get('name', '') for c in previous_characters[-20:]
    ) or "없음"

    user_prompt = f"""오늘의 낙서풍 이모티콘 캐릭터를 새로 기획해라.
이전 캐릭터: {prev_summary}

이전과 종류/이름/색상 모두 달라야 한다.
emotions는 정확히 24개, 그 중 정확히 10개에만 text_overlay에 한글을 넣고
나머지 14개는 text_overlay: null 로 설정해.
한글 텍스트는 모두 서로 달라야 한다 (중복 절대 금지).
"""

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
            "system": SCRIBBLE_PLAN_SYSTEM,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    raw_text = resp.json()["content"][0]["text"]

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        raise ValueError(f"Claude가 JSON을 반환하지 않음: {raw_text[:200]}")

    data = json.loads(match.group(0))

    # emotions 정규화
    normalized: list = []
    for e in data.get("emotions", []):
        if isinstance(e, str):
            normalized.append({"action": e, "text_overlay": None})
        elif isinstance(e, dict):
            action = str(e.get("action") or e.get("emotion") or "idle pose").strip()
            text = e.get("text_overlay")
            if isinstance(text, str):
                text = text.strip() or None
                if text and len(text) > 8:
                    text = text[:8]
            else:
                text = None
            normalized.append({"action": action, "text_overlay": text})

    # 24개 보정
    while len(normalized) < 24:
        normalized.append({"action": f"extra_pose_{len(normalized) + 1}", "text_overlay": None})
    normalized = normalized[:24]

    # 10:14 비율 강제
    FALLBACK_TEXTS = [
        "월요병", "현타옴", "퇴근각", "존버", "월급날",
        "ㅎㅎ", "ㅠㅠ", "화이팅", "미안", "고마워",
    ]
    text_idx = [i for i, e in enumerate(normalized) if e["text_overlay"]]

    # 한글이 10개 초과면 잘라내기
    if len(text_idx) > 10:
        for i in text_idx[10:]:
            normalized[i]["text_overlay"] = None

    # 한글이 10개 미만이면 fallback 채우기
    elif len(text_idx) < 10:
        used = {normalized[i]["text_overlay"] for i in text_idx}
        empty_idx = [i for i, e in enumerate(normalized) if not e["text_overlay"]]
        random.shuffle(empty_idx)
        fallback_pool = [t for t in FALLBACK_TEXTS if t not in used]
        random.shuffle(fallback_pool)
        need = 10 - len(text_idx)
        for i in empty_idx[:need]:
            if fallback_pool:
                normalized[i]["text_overlay"] = fallback_pool.pop()

    # 중복 제거 (Claude 응답 단계에서)
    normalized = _ensure_unique_text_overlays(normalized)

    # 중복 제거로 한글이 줄어들면 다시 fallback 채우기
    text_idx_after = [i for i, e in enumerate(normalized) if e["text_overlay"]]
    if len(text_idx_after) < 10:
        used = {normalized[i]["text_overlay"] for i in text_idx_after}
        empty_idx = [i for i, e in enumerate(normalized) if not e["text_overlay"]]
        random.shuffle(empty_idx)
        fallback_pool = [t for t in FALLBACK_TEXTS if t not in used]
        random.shuffle(fallback_pool)
        need = 10 - len(text_idx_after)
        for i in empty_idx[:need]:
            if fallback_pool:
                normalized[i]["text_overlay"] = fallback_pool.pop()

    # index 부여
    for i, emo in enumerate(normalized, start=1):
        emo["index"] = i

    data["emotions"] = normalized
    data.setdefault("character_desc",
                    "A simple naive doodle character with minimal flat-line illustration")
    data.setdefault("theme", "낙서풍 일상 밈")
    data.setdefault("style", "scribble-meme")
    return data


# ============================================================
# DALL-E 프롬프트 빌드
# ============================================================
SCRIBBLE_DALLE_PROMPT_TEMPLATE = """A naive folk-art style cartoon sticker, charmingly minimal Korean internet meme doodle aesthetic.

Subject: {character_description} {action}.

Visual style requirements (STRICT):
- Wobbly hand-drawn black outline, uneven thickness
- Flat solid color fill (max 3 colors), no gradient, no shading, no highlights
- Basic geometric shapes only: circles, ovals, simple lines, triangles
- Pure white background
- Character occupies center 70% of frame with 15% margin on all sides
- No text, no letters, no words anywhere in image
- Character internal areas must be fully filled (no transparent holes inside the body)
- Minimal detail, simple silhouette, recognizable but stylized

Aesthetic notes:
- Korean internet meme doodle culture
- Naive children's drawing style with adult humor
- Intentionally simplistic flat-line illustration
- Charm comes from minimalism, not from imitating any specific artist

Quality: simple, clean, expressive minimalism.
Image format: 1024x1024 transparent PNG."""


def generate_prompts_scribble(data: dict) -> tuple[list, str]:
    """24개 프롬프트 + Cloudinary 폴더명 생성"""
    char_desc = data.get("character_desc", "a simple doodle")
    folder_name = f"{SERIES_PREFIX}_{TODAY}_{data['character_name']}"

    prompts: list = []
    for emo in data["emotions"]:
        idx = emo["index"]
        action = emo["action"]
        text_overlay = emo.get("text_overlay")
        prompt = SCRIBBLE_DALLE_PROMPT_TEMPLATE.format(
            character_description=char_desc,
            action=action,
        )
        prompts.append({
            "index": idx,
            "filename": f"{idx:02d}.png",
            "emotion": action,
            "prompt": prompt,
            "text_overlay": text_overlay,
        })
    return prompts, folder_name


# ============================================================
# DALL-E 호출
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
    if resp.status_code >= 400:
        print(f"[DALL-E ERROR {resp.status_code}] response body: {resp.text[:500]}", flush=True)
    resp.raise_for_status()
    return resp.json()["data"][0]["b64_json"]


def _generate_image_from_reference(prompt: str, reference_png: bytes) -> str:
    """image-to-image (edits) — 2~24번, 1번 이미지를 레퍼런스로"""
    edit_preamble = (
        "Use the attached reference image as the exact character design template. "
        "Keep the exact same character, colors, proportions, and outline style. "
        "Change ONLY the pose, expression, and action as described below. "
        "Do not redesign the character. Maintain the naive folk-art doodle aesthetic with simple flat lines.\n\n"
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
    if resp.status_code >= 400:
        print(f"[DALL-E ERROR {resp.status_code}] response body: {resp.text[:500]}", flush=True)
    resp.raise_for_status()
    return resp.json()["data"][0]["b64_json"]


# ============================================================
# 한글 텍스트 오버레이 (NanumBrush)
# ============================================================
_korean_font_cache: dict = {}


def _load_korean_font(size: int):
    """NanumBrush(손그림) 우선, 실패 시 NanumGothicBold fallback."""
    if size in _korean_font_cache:
        return _korean_font_cache[size]

    for path in (KOREAN_FONT_PATH, KOREAN_FONT_FALLBACK):
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
    """낙서풍 시리즈 한글 오버레이.

    폰트: NanumBrush (손그림 느낌), fallback NanumGothicBold
    구조: 흰 외곽 → 검정 외곽 → 흰 글씨 (3중 레이어, 다크모드 대응)
    굵기: width*0.14 폰트, black_w=font_size//7 (쿠로/현행 강화판과 동일)
    위치: bottom = 하단 85%, top = 상단 4%

    PIL stroke_width 옵션 대신 픽셀별 그리기 — NanumBrush의 stroke 렌더링이
    PIL 내장 stroke와 시각적으로 어색해서 manual 방식 유지.
    """
    if not text:
        return image_bytes

    img = Image.open(BytesIO(image_bytes)).convert('RGBA')
    width, height = img.size
    font_size = max(80, int(width * 0.14))
    font = _load_korean_font(font_size)

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) // 2 - bbox[0]
    if position == "top":
        y = int(height * 0.04) - bbox[1]
    else:
        y = int(height * 0.85) - text_h // 2 - bbox[1]

    black_w = max(8, font_size // 7)
    white_outer_w = black_w + max(5, font_size // 12)

    # Layer 1: 흰 외곽 (halo) — 다크모드 대응
    for dx in range(-white_outer_w, white_outer_w + 1, 2):
        for dy in range(-white_outer_w, white_outer_w + 1, 2):
            if dx * dx + dy * dy <= white_outer_w * white_outer_w:
                draw.text((x + dx, y + dy), text, font=font, fill=(255, 255, 255, 255))

    # Layer 2: 검정 외곽
    for dx in range(-black_w, black_w + 1, 1):
        for dy in range(-black_w, black_w + 1, 1):
            if dx * dx + dy * dy <= black_w * black_w:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))

    # Layer 3: 흰 글씨
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    composed = Image.alpha_composite(img, overlay)
    out = BytesIO()
    composed.save(out, "PNG", optimize=True)
    return out.getvalue()


# ============================================================
# 알파 hole 처리 (P0 패치 — 기존 emoticon_generator.py와 동일)
# ============================================================
def fill_alpha_holes(img):
    """캐릭터 외곽 컨투어 내부의 모든 알파 구멍을 채운다.
    외곽선 dilate 이전에 호출되어야 함.
    """
    import numpy as np
    import cv2

    arr = np.array(img)
    if arr.shape[2] != 4:
        return img

    alpha = arr[:, :, 3]
    binary = (alpha > 50).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img

    filled_mask = np.zeros_like(binary)
    cv2.drawContours(filled_mask, contours, -1, 255, thickness=cv2.FILLED)

    hole_mask = (filled_mask > 0) & (alpha < 50)
    if hole_mask.sum() == 0:
        return img

    rgb = arr[:, :, :3].copy()
    inpaint_mask = hole_mask.astype(np.uint8) * 255
    rgb_inpainted = cv2.inpaint(rgb, inpaint_mask, 3, cv2.INPAINT_TELEA)

    arr[:, :, :3] = rgb_inpainted
    arr[:, :, 3] = filled_mask

    return Image.fromarray(arr, mode='RGBA')


def validate_alpha_holes(img, threshold_pct=1.0):
    """외곽 컨투어 내부 알파 구멍 비율 측정.
    Returns: (is_ok, hole_pct, hole_count)
    """
    import numpy as np
    import cv2

    arr = np.array(img)
    if arr.shape[2] != 4:
        return (False, 100.0, 0)

    alpha = arr[:, :, 3]
    binary = (alpha > 50).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return (False, 100.0, 0)

    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)

    inner_holes = (filled > 0) & (alpha < 50)
    char_area = (filled > 0).sum()
    hole_pct = (inner_holes.sum() / char_area * 100) if char_area > 0 else 100.0

    return (hole_pct < threshold_pct, float(hole_pct), int(inner_holes.sum()))


# ============================================================
# rembg 배경 제거 + 흰 외곽선 (외곽선 dilate 8px 구조 그대로)
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

    P0 패치: post_process_mask=True + fill_alpha_holes(dilate 이전)
    """
    import numpy as np

    img = Image.open(BytesIO(image_bytes))
    session = get_rembg_session()
    cleaned = remove(img, session=session, post_process_mask=True).convert('RGBA')
    cleaned = fill_alpha_holes(cleaned)  # 내부 hole 메움 (dilate 이전)

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
# 이미지 생성 + 업로드 (1컷 게이트 + dry-run + 24컷 hole 누적)
# ============================================================
def generate_and_upload_scribble(prompts: list, folder_name: str):
    """낙서풍 24컷 생성 + 업로드 + 1컷 게이트 + 24컷 hole% 누적."""
    if _is_dryrun():
        print("=" * 60)
        print("🧪 DRY-RUN MODE: RUN_ONLY_FIRST=true — 1번 이미지만 생성합니다")
        print("=" * 60)

    success_count = 0
    fail_count = 0
    reference_png: bytes | None = None
    hole_results: list = []

    for item in prompts:
        idx = item["index"]
        filename = item["filename"]
        emotion = item["emotion"]

        # Dry-run: 1번 이후 break
        if _is_dryrun() and idx > 1:
            print(f"\n🧪 RUN_ONLY_FIRST=true → idx={idx} 스킵 (1컷 dry-run 모드)")
            break

        print(f"  [{idx:02d}/24] {emotion[:50]}...", end=" ", flush=True)

        # 이미지 생성
        try:
            if reference_png is None:
                b64_data = _generate_image_from_text(item["prompt"])
                print("[t2i]", end=" ", flush=True)
            else:
                try:
                    b64_data = _generate_image_from_reference(item["prompt"], reference_png)
                    print("[ref]", end=" ", flush=True)
                except Exception as ref_err:
                    print(f"[ref 실패→t2i fallback: {ref_err}]", end=" ", flush=True)
                    b64_data = _generate_image_from_text(item["prompt"])
        except Exception as e:
            print(f"❌ 생성 실패: {e}")
            fail_count += 1
            continue

        try:
            image_bytes = base64.b64decode(b64_data)
            del b64_data

            # rembg 후처리 (배경 제거 + fill_alpha_holes + 흰 테두리)
            try:
                image_bytes = process_image_with_rembg(image_bytes)
            except Exception as e:
                print(f"[rembg] 후처리 실패, 원본 사용: {e}")

            # 알파 구멍 검증 (24컷 모두)
            try:
                _vimg = Image.open(BytesIO(image_bytes))
                _is_ok, _hole_pct, _hole_count = validate_alpha_holes(_vimg)
                hole_results.append({'idx': idx, 'hole_pct': round(_hole_pct, 2)})
            except Exception as _ve:
                print(f"[검증 오류: {_ve}]", end=" ", flush=True)
                _is_ok, _hole_pct, _hole_count = (True, 0.0, 0)
                hole_results.append({'idx': idx, 'hole_pct': -1.0})

            # 1컷 게이트
            if reference_png is None:
                if not _is_ok:
                    msg = (f"⛔ [낙서풍] 1컷 알파 검증 실패: hole={_hole_pct:.2f}% "
                           f"({_hole_count:,}px) — 임계값 1.0%\n"
                           f"23컷 생성 중단됨. fill_alpha_holes 또는 rembg 옵션 확인 필요.")
                    print(f"\n{msg}")
                    try:
                        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                            requests.post(
                                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                                timeout=10,
                            )
                    except Exception:
                        pass
                    sys.exit(1)
                print(f"    ✅ [낙서풍] 1컷 알파 검증 통과: hole={_hole_pct:.2f}%")
                reference_png = image_bytes
                print("[ref저장]", end=" ", flush=True)

            # 한글 텍스트 오버레이
            overlay_text = item.get("text_overlay")
            if overlay_text:
                try:
                    image_bytes = overlay_korean_text(image_bytes, overlay_text)
                    print(f"[text '{overlay_text}']", end=" ", flush=True)
                except Exception as e:
                    print(f"[overlay 실패: {e}]", end=" ", flush=True)

            # Cloudinary 업로드
            upload_resp = requests.post(
                f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload",
                auth=(CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET),
                data={
                    "public_id": f"emoticons/{folder_name}/{filename.replace('.png', '')}",
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

            print("✅ 업로드 완료")
            success_count += 1

        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            fail_count += 1
            continue

        if idx < len(prompts):
            time.sleep(1)

    print(f"\n[Step 5] 낙서풍 이미지 생성 완료: 성공 {success_count}, 실패 {fail_count}")
    return success_count, fail_count, hole_results


# ============================================================
# 텔레그램 알림 (낙서풍 prefix)
# ============================================================
def send_telegram_scribble(data: dict, success_count: int, fail_count: int,
                           folder_name: str, hole_results: list = None):
    """낙서풍 시리즈 완료 알림 (prefix 🎨 [낙서풍])"""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print("[Step 7] TELEGRAM_BOT_TOKEN/CHAT_ID 미설정 — 알림 스킵")
        return

    text_count = sum(
        1 for e in data.get("emotions", [])
        if isinstance(e, dict) and e.get("text_overlay")
    )

    hole_block = ""
    if hole_results:
        crit = [r for r in hole_results if r['hole_pct'] >= 5.0]
        fail = [r for r in hole_results if 2.0 <= r['hole_pct'] < 5.0]
        review = [r for r in hole_results if 0.5 <= r['hole_pct'] < 2.0]
        passed = [r for r in hole_results if 0 <= r['hole_pct'] < 0.5]
        errored = [r for r in hole_results if r['hole_pct'] < 0]
        hole_summary = "\n".join([f"  {r['idx']:02d}: {r['hole_pct']}%" for r in hole_results])
        hole_block = (
            f"\n\n🕳 알파 구멍 검증 ({len(hole_results)}컷)\n"
            f"🔴 CRITICAL(≥5%): {len(crit)}  🟠 FAIL(2~5%): {len(fail)}  "
            f"🟡 REVIEW(0.5~2%): {len(review)}  ✅ PASS(<0.5%): {len(passed)}  "
            f"⚠ 오류: {len(errored)}\n"
            f"{hole_summary}"
        )

    is_dryrun = _is_dryrun()
    title = "🎨 [낙서풍][DRY-RUN] 1컷 검증" if is_dryrun else "🎨 [낙서풍] 이모티콘 생성 완료!"

    message = (
        f"{title}\n"
        f"📅 {TODAY}\n"
        f"🎨 캐릭터: {data['character_name']}\n"
        f"🎭 테마: {data.get('theme', '-')}\n"
        f"✨ 스타일: {data.get('style', 'scribble-meme')}\n"
        f"✅ 성공: {success_count}개 / ❌ 실패: {fail_count}개\n"
        f"💬 한글텍스트 {text_count}개 / 이미지만 {24 - text_count}개\n"
        f"📁 Cloudinary: emoticons/{folder_name}\n"
        f"👉 다음: LINE 우선 제출 (B급 친화), OGQ 보수적"
        f"{hole_block}"
    )

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=15,
        )
        if resp.ok:
            print("[Step 7] Telegram 알림 전송 완료")
        else:
            print(f"[Step 7] Telegram 알림 실패: {resp.text}")
    except Exception as e:
        print(f"[Step 7] Telegram 알림 예외: {e}")


# ============================================================
# 메인
# ============================================================
def main():
    print("=" * 60)
    print(f"WOCS 낙서풍 이모티콘 생성기 - {TODAY}")
    print("=" * 60)

    # Step 1: 이전 캐릭터 누적 파일 (시리즈 분리)
    prev: list = []
    if Path(PREV_CHARACTERS_FILE).exists():
        try:
            prev = json.loads(Path(PREV_CHARACTERS_FILE).read_text(encoding='utf-8'))
        except Exception as e:
            print(f"[Step 1] {PREV_CHARACTERS_FILE} 파싱 실패, 빈 리스트로 시작: {e}")
            prev = []
    print(f"[Step 1] 낙서풍 이전 캐릭터 {len(prev)}개 로드")

    # Step 2: 캐릭터 plan
    data = plan_character_scribble(prev)
    print(f"[Step 2] 낙서풍 캐릭터 기획 완료: {data['character_name']} / {data.get('theme', '-')}")

    # Step 3: 프롬프트 24개 + Cloudinary 폴더
    prompts, folder_name = generate_prompts_scribble(data)

    # Step 4-5: 이미지 생성 + Cloudinary 업로드 (1컷 게이트 포함)
    print(f"\n[Step 4-5] 24개 이미지 생성 시작 (folder: {folder_name})...")
    success_count, fail_count, hole_results = generate_and_upload_scribble(prompts, folder_name)

    # Step 6: 누적 파일 업데이트 (dry-run에서도 캐릭터명만 기록)
    prev.append({
        'date': TODAY,
        'name': data['character_name'],
        'theme': data.get('theme', ''),
        'dryrun': _is_dryrun(),
    })
    try:
        Path(PREV_CHARACTERS_FILE).write_text(
            json.dumps(prev, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        print(f"[Step 6] {PREV_CHARACTERS_FILE} 업데이트 완료 (총 {len(prev)}개)")
    except Exception as e:
        print(f"[Step 6] {PREV_CHARACTERS_FILE} 쓰기 실패: {e}")

    # Step 7: 텔레그램 알림 (낙서풍 prefix)
    send_telegram_scribble(data, success_count, fail_count, folder_name, hole_results)

    print("\n" + "=" * 60)
    print(f"낙서풍 시리즈 완료! 성공: {success_count}/24")
    print("=" * 60)

    if fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
