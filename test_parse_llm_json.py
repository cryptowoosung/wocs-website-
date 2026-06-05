#!/usr/bin/env python3
"""emoticon_scribble_generator.parse_llm_json 및 재요청 방어 로직 테스트.

pytest 미설치 환경을 고려해 stdlib unittest 로 작성.
모듈 최상단이 환경변수/rembg 를 요구하므로 import 전에 stub 한다.
"""
import os
import sys
import json
import types
import unittest

# --- 모듈 import 를 위한 사전 stub (실 의존성 없이 순수 파서만 테스트) ---
_fake_rembg = types.ModuleType("rembg")
_fake_rembg.new_session = lambda *a, **k: None
_fake_rembg.remove = lambda *a, **k: None
sys.modules.setdefault("rembg", _fake_rembg)

for _k in (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
):
    os.environ.setdefault(_k, "test-dummy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emoticon_scribble_generator as gen  # noqa: E402


class TestParseLlmJson(unittest.TestCase):
    def test_strict_json_passes_unchanged(self):
        # Arrange
        raw = '{"character_name": "멍충이", "emotions": []}'
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "멍충이")

    def test_trailing_comma_object_and_array(self):
        # Arrange — 6/3 실패 케이스: 후행 쉼표
        raw = (
            "{\n"
            '  "character_name": "짤짤이",\n'
            '  "emotions": [\n'
            '    {"index": 1, "action": "idle", "text_overlay": null},\n'
            "  ],\n"
            "}"
        )
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "짤짤이")
        self.assertEqual(len(data["emotions"]), 1)

    def test_code_fence_json_block(self):
        # Arrange
        raw = '```json\n{"character_name": "하찮이", "emotions": []}\n```'
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "하찮이")

    def test_line_comment_removed(self):
        # Arrange
        raw = (
            "{\n"
            '  "character_name": "둘리", // 캐릭터 이름\n'
            '  "emotions": []\n'
            "}"
        )
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "둘리")

    def test_block_comment_and_trailing_comma_combined(self):
        # Arrange
        raw = (
            "{\n"
            "  /* 오늘의 캐릭터 */\n"
            '  "character_name": "쩌리",\n'
            '  "emotions": [{"index": 1, "action": "a", "text_overlay": "ㅎㅎ"},],\n'
            "}"
        )
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "쩌리")
        self.assertEqual(data["emotions"][0]["text_overlay"], "ㅎㅎ")

    def test_surrounding_prose_is_stripped(self):
        # Arrange
        raw = (
            "여기 결과입니다:\n"
            '{"character_name": "멍뭉", "emotions": [{"index":1,"action":"x","text_overlay":"ㅠㅠ"},]}\n'
            "감사합니다."
        )
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_name"], "멍뭉")

    def test_url_in_string_not_broken_by_comment_strip(self):
        # Arrange — sanitize 단계가 '://' 를 주석으로 오인하면 안 됨 (trailing comma 로 sanitize 강제)
        raw = '{"character_desc": "https://ex.com 느낌", "emotions": [],}'
        # Act
        data = gen.parse_llm_json(raw)
        # Assert
        self.assertEqual(data["character_desc"], "https://ex.com 느낌")

    def test_no_json_raises_value_error(self):
        # Arrange
        raw = "죄송하지만 JSON 을 만들 수 없습니다."
        # Act / Assert
        with self.assertRaises(ValueError):
            gen.parse_llm_json(raw)


class TestPlanRetry(unittest.TestCase):
    """plan_character_scribble 의 1회 재요청 방어 로직 검증."""

    def _patch_requests(self, responses):
        """_request_scribble_plan 이 호출될 때마다 responses 를 순서대로 반환."""
        calls = {"n": 0}

        def fake_request(user_prompt):
            i = calls["n"]
            calls["n"] += 1
            return responses[i]

        return fake_request, calls

    def test_retry_succeeds_on_second_attempt(self):
        # Arrange — 1차 깨진 JSON, 2차 정상
        good = json.dumps({
            "character_name": "회복이",
            "emotions": [{"index": 1, "action": "idle", "text_overlay": "ㅎㅎ"}],
        }, ensure_ascii=False)
        bad = "응답: {이건 JSON 이 아님,,,}"
        fake_request, calls = self._patch_requests([bad, good])
        orig = gen._request_scribble_plan
        gen._request_scribble_plan = fake_request
        try:
            # Act
            data = gen.plan_character_scribble([])
        finally:
            gen._request_scribble_plan = orig
        # Assert
        self.assertEqual(calls["n"], 2)  # 정확히 1회 재요청
        self.assertEqual(data["character_name"], "회복이")

    def test_double_failure_raises_with_preview(self):
        # Arrange — 두 번 다 깨진 JSON
        bad1 = "첫 응답 {nope,,,}"
        bad2 = "두번째 응답 {still broken,,,}"
        fake_request, calls = self._patch_requests([bad1, bad2])
        orig = gen._request_scribble_plan
        gen._request_scribble_plan = fake_request
        try:
            # Act / Assert
            with self.assertRaises(ValueError):
                gen.plan_character_scribble([])
        finally:
            gen._request_scribble_plan = orig
        self.assertEqual(calls["n"], 2)  # 1차 + 재요청 1회 = 총 2회


if __name__ == "__main__":
    unittest.main(verbosity=2)
