#!/usr/bin/env python3
"""낙서풍 시리즈의 특정 인덱스 1컷만 재생성 + Cloudinary 덮어쓰기.

사용 예:
    python tools/regenerate_single_scribble.py \
        --folder scribble_2026-05-08_쪼글이 \
        --idx 11 \
        --action "몸을 옆으로 기울이며 손을 머리 옆에 댄 생각하는 표정"

기존 emoticon_scribble_generator.py의 함수들을 재사용한다:
- _generate_image_from_reference (DALL-E edits)
- process_image_with_rembg (배경 제거 + fill + 외곽선 dilate)
- overlay_korean_text (한글 오버레이, bytes 기반)
- validate_alpha_holes (1컷 게이트와 동일한 검증)

검증 통과 후에만 Cloudinary에 overwrite + invalidate 업로드한다.
검증 실패 시 /tmp/regen_failed_<idx>.png에 디버그 저장 후 종료(exit 1).
"""
from __future__ import annotations

import argparse
import base64
import sys
from io import BytesIO
from pathlib import Path

# 프로젝트 루트 import 경로 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import emoticon_scribble_generator as eg  # noqa: E402
import requests  # noqa: E402
from PIL import Image  # noqa: E402


def download_reference(folder: str, ref_idx: int = 1) -> bytes:
    """Cloudinary에서 기준 이미지(보통 01번)를 다운로드한다."""
    url = (
        f"https://res.cloudinary.com/{eg.CLOUDINARY_CLOUD_NAME}"
        f"/image/upload/emoticons/{folder}/{ref_idx:02d}.png"
    )
    print(f"[ref 다운로드] {url}", flush=True)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content


def regenerate_one(
    folder: str,
    idx: int,
    action: str,
    text_overlay: str | None = None,
    character_description: str = "(see reference image)",
) -> bool:
    """1컷만 재생성하고 Cloudinary에 덮어쓰기한다.

    Returns:
        True  — 검증 통과 + 업로드 성공
        False — 검증 실패 (Cloudinary 업로드 미수행)
    """
    # 1. reference (01번) 다운로드
    ref_bytes = download_reference(folder, ref_idx=1)
    print(f"[ref] {len(ref_bytes) / 1024:.0f} KB 로드 완료", flush=True)

    # 2. DALL-E edits 호출 (기존 1컷-게이트 통과한 reference 사용)
    full_prompt = eg.SCRIBBLE_DALLE_PROMPT_TEMPLATE.format(
        character_description=character_description,
        action=action,
    )
    print(f"[DALL-E edits] action: {action}", flush=True)
    b64_data = eg._generate_image_from_reference(full_prompt, ref_bytes)
    image_bytes = base64.b64decode(b64_data)
    del b64_data
    print(f"[DALL-E] 생성 완료 ({len(image_bytes) / 1024:.0f} KB)", flush=True)

    # 3. rembg + fill_alpha_holes + 외곽선 dilate
    image_bytes = eg.process_image_with_rembg(image_bytes)
    print(f"[후처리] 완료 ({len(image_bytes) / 1024:.0f} KB)", flush=True)

    # 4. 검증 (1컷 게이트와 동일한 임계값 1.0%)
    vimg = Image.open(BytesIO(image_bytes))
    is_ok, hole_pct, hole_count, contour_pct = eg.validate_alpha_holes(vimg)
    print(
        f"[검증] hole={hole_pct:.2f}% ({hole_count:,}px) "
        f"contour={contour_pct:.1f}% ok={is_ok}",
        flush=True,
    )

    if not is_ok:
        debug_path = Path("/tmp") / f"regen_failed_{idx:02d}.png"
        try:
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            debug_path.write_bytes(image_bytes)
            print(f"   디버그 저장: {debug_path}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"   디버그 저장 실패: {e}", flush=True)
        print("⛔ 검증 실패. Cloudinary 업로드 중단.", flush=True)
        return False

    # 5. 한글 텍스트 오버레이 (있으면) — 검증 통과 후에 적용
    if text_overlay:
        try:
            image_bytes = eg.overlay_korean_text(image_bytes, text_overlay)
            print(f"[한글 오버레이] '{text_overlay}'", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[overlay 실패: {e}]", flush=True)

    # 6. Cloudinary 업로드 (overwrite + invalidate)
    public_id = f"emoticons/{folder}/{idx:02d}"
    print(f"[Cloudinary 덮어쓰기] {public_id}", flush=True)

    upload_url = (
        f"https://api.cloudinary.com/v1_1/{eg.CLOUDINARY_CLOUD_NAME}/image/upload"
    )
    resp = requests.post(
        upload_url,
        auth=(eg.CLOUDINARY_API_KEY, eg.CLOUDINARY_API_SECRET),
        data={
            "public_id": public_id,
            "use_filename": "true",
            "unique_filename": "false",
            "overwrite": "true",
            "invalidate": "true",
        },
        files={"file": (f"{idx:02d}.png", image_bytes, "image/png")},
        timeout=60,
    )
    resp.raise_for_status()
    result = resp.json()
    print("✅ 업로드 완료", flush=True)
    print(f"   secure_url: {result['secure_url']}", flush=True)
    print(f"   bytes: {result.get('bytes', 0):,}", flush=True)
    print(f"   version: {result.get('version', '-')}", flush=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, help="Cloudinary 폴더명")
    parser.add_argument("--idx", type=int, required=True, help="재생성 인덱스")
    parser.add_argument("--action", required=True, help="action 묘사 (한/영)")
    parser.add_argument("--text", default=None, help="한글 텍스트 오버레이 (선택)")
    parser.add_argument(
        "--character-description",
        default="(see reference image)",
        help="character_description 필드 (기본: 레퍼런스 이미지에 위임)",
    )
    args = parser.parse_args()

    success = regenerate_one(
        folder=args.folder,
        idx=args.idx,
        action=args.action,
        text_overlay=args.text,
        character_description=args.character_description,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
