#!/usr/bin/env python3
"""LLM 응답에서 JSON 객체를 견고하게 추출/정제하는 공용 유틸.

emoticon_generator.py / emoticon_scribble_generator.py 등 여러 생성기에서
Claude 응답의 비표준 JSON(코드펜스, 주석, 후행 쉼표)을 안전하게 파싱하기 위해
공유한다. 자세한 배경은 2026-06-03 Scribble Generator 실패(JSONDecodeError) 참고.
"""
import re
import json


def _strip_code_fence(text: str) -> str:
    """```json ... ``` 또는 ``` ... ``` 코드펜스를 벗겨 내부 본문만 반환."""
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    return fence.group(1) if fence else text


def _sanitize_json_text(text: str) -> str:
    """LLM JSON 의 흔한 비표준 요소(주석, 후행 쉼표)를 제거한다.

    - 블록 주석 /* ... */ 제거
    - 라인 주석 // ... 제거 (단, 'https://' 의 '://' 는 보호)
    - 후행 쉼표 ,] / ,} 제거
    """
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    text = re.sub(r"(?<!:)//[^\n\r]*", "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def parse_llm_json(raw_text: str) -> dict:
    """LLM 응답 텍스트에서 JSON 객체를 추출/정제하여 dict 로 반환.

    1) 코드펜스 제거 후 첫 '{' ~ 마지막 '}' 블록 추출
    2) 엄격 모드로 json.loads 시도
    3) 실패하면 주석/후행쉼표 정제 후 재시도
    JSON 객체를 찾지 못하면 ValueError, 정제 후에도 깨지면
    json.JSONDecodeError 를 그대로 전파한다.
    """
    text = _strip_code_fence(raw_text)
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"응답에서 JSON 객체를 찾지 못함: {raw_text[:200]!r}")

    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return json.loads(_sanitize_json_text(candidate))
