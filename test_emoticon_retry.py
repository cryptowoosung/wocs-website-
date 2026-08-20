#!/usr/bin/env python3
"""emoticon_generator._post_image_with_retry 재시도 로직 테스트.

pytest 미설치 환경을 고려해 stdlib unittest 로 작성.
모듈 최상단이 환경변수/rembg/PIL/google 을 요구하므로 import 전에 stub 한다.
실 네트워크 호출 없이 requests.post 를 mock 으로 대체해 500 응답을 주입한다.
"""
import io
import os
import sys
import types
import unittest
from unittest import mock

import requests  # 실제 패키지 (HTTPError 클래스 사용)

# --- 모듈 import 를 위한 사전 stub (실 의존성 없이 함수만 테스트) ---
_fake_rembg = types.ModuleType("rembg")
_fake_rembg.new_session = lambda *a, **k: None
_fake_rembg.remove = lambda *a, **k: None
sys.modules.setdefault("rembg", _fake_rembg)

_fake_pil = sys.modules.setdefault("PIL", types.ModuleType("PIL"))
_fake_imagefilter = types.ModuleType("PIL.ImageFilter")
sys.modules.setdefault("PIL.ImageFilter", _fake_imagefilter)
_fake_pil.ImageFilter = _fake_imagefilter

# google.auth.transport.requests.Request stub 체인
_g = sys.modules.setdefault("google", types.ModuleType("google"))
_ga = sys.modules.setdefault("google.auth", types.ModuleType("google.auth"))
_gat = sys.modules.setdefault("google.auth.transport", types.ModuleType("google.auth.transport"))
_gatr = sys.modules.setdefault(
    "google.auth.transport.requests", types.ModuleType("google.auth.transport.requests")
)
_gatr.Request = object

for _k in (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "GOOGLE_CREDENTIALS_JSON",
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
):
    os.environ.setdefault(_k, "test-dummy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emoticon_generator as gen  # noqa: E402


class FakeResp:
    """requests.Response 의 최소 대체물."""

    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{self.status_code} Server Error: for url: https://api.openai.com/v1/images/generations"
            )

    def json(self):
        return self._json


class PostImageRetryTest(unittest.TestCase):
    def setUp(self):
        # 백오프 sleep 을 제거해 테스트를 즉시 실행
        self._sleep_patch = mock.patch.object(gen.time, "sleep", lambda *a, **k: None)
        self._sleep_patch.start()

    def tearDown(self):
        self._sleep_patch.stop()

    def test_500_three_times_is_fatal(self):
        """500 이 IMAGE_MAX_ATTEMPTS(3)회 연속 반환되면 HTTPError 로 승격(FATAL)."""
        post = mock.Mock(return_value=FakeResp(500))
        with mock.patch.object(gen.requests, "post", post):
            with self.assertRaises(requests.exceptions.HTTPError):
                gen._post_image_with_retry("https://api.openai.com/v1/images/generations")
        self.assertEqual(
            post.call_count,
            gen.IMAGE_MAX_ATTEMPTS,
            f"500 은 정확히 {gen.IMAGE_MAX_ATTEMPTS}회 시도 후 FATAL 이어야 함",
        )

    def test_500_then_200_succeeds(self):
        """500 1회 후 200 이면 재시도하여 성공 응답을 반환."""
        ok = FakeResp(200, {"data": [{"b64_json": "QUJD"}]})
        post = mock.Mock(side_effect=[FakeResp(500), ok])
        with mock.patch.object(gen.requests, "post", post):
            resp = gen._post_image_with_retry("https://api.openai.com/v1/images/generations")
        self.assertIs(resp, ok)
        self.assertEqual(post.call_count, 2, "500 → 200 은 2회 호출이어야 함")

    def test_400_is_immediate_fatal_no_retry(self):
        """400(비일시적) 은 재시도 없이 즉시 FATAL."""
        post = mock.Mock(return_value=FakeResp(400))
        with mock.patch.object(gen.requests, "post", post):
            with self.assertRaises(requests.exceptions.HTTPError):
                gen._post_image_with_retry("https://api.openai.com/v1/images/generations")
        self.assertEqual(post.call_count, 1, "4xx 는 재시도하지 않아야 함")


class PlanRetryTest(unittest.TestCase):
    """_request_character_plan 재시도 / 원문 로깅 검증."""

    def setUp(self):
        self._sleep_patch = mock.patch.object(gen.time, "sleep", lambda *a, **k: None)
        self._sleep_patch.start()

    def tearDown(self):
        self._sleep_patch.stop()

    @staticmethod
    def _claude_resp(text, stop_reason="end_turn"):
        return FakeResp(200, {"content": [{"text": text}], "stop_reason": stop_reason})

    def test_broken_json_then_valid_succeeds(self):
        """1차 응답이 깨진 JSON 이면 재요청해 2차 응답으로 복구한다."""
        # Arrange
        good = '{"character_name": "복구", "emotions": []}'
        post = mock.Mock(side_effect=[self._claude_resp("{깨진,,,}"), self._claude_resp(good)])

        # Act
        with mock.patch.object(gen.requests, "post", post):
            data = gen._request_character_plan("sys", "user")

        # Assert
        self.assertEqual(data["character_name"], "복구")
        self.assertEqual(post.call_count, 2, "깨진 JSON 1회 → 정확히 1회 재요청")

    def test_all_attempts_broken_raises_runtime_error(self):
        """PLAN_MAX_ATTEMPTS 회 모두 실패하면 RuntimeError 로 승격한다."""
        # Arrange
        post = mock.Mock(return_value=self._claude_resp("{계속깨짐,,,}"))

        # Act / Assert
        with mock.patch.object(gen.requests, "post", post):
            with self.assertRaises(RuntimeError):
                gen._request_character_plan("sys", "user")
        self.assertEqual(post.call_count, gen.PLAN_MAX_ATTEMPTS)

    def test_raw_response_is_logged_on_failure(self):
        """진단 가능하도록 실패 응답 원문과 stop_reason 을 로그에 남긴다."""
        # Arrange
        raw = '{"character_name": "로그확인용" 깨짐,,,}'
        post = mock.Mock(return_value=self._claude_resp(raw, stop_reason="max_tokens"))

        # Act
        with mock.patch.object(gen.requests, "post", post):
            with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
                with self.assertRaises(RuntimeError):
                    gen._request_character_plan("sys", "user")
        printed = out.getvalue()

        # Assert
        self.assertIn(raw, printed, "실패한 응답 원문이 그대로 로그에 남아야 함")
        self.assertIn("max_tokens", printed, "stop_reason 이 로그에 남아야 함")

    def test_uses_plan_max_tokens(self):
        """max_tokens 는 PLAN_MAX_TOKENS(4000) 로 요청해야 한다."""
        # Arrange
        post = mock.Mock(return_value=self._claude_resp('{"character_name": "정상"}'))

        # Act
        with mock.patch.object(gen.requests, "post", post):
            gen._request_character_plan("sys", "user")

        # Assert
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], gen.PLAN_MAX_TOKENS)
        self.assertEqual(gen.PLAN_MAX_TOKENS, 4000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
