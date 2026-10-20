"""webhook 모드에서 어닝·천막 주제가 들어오면 실패(exit 1)가 아니라 '건너뜀'으로 끝나는지 테스트."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def aw():
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    import auto_writer
    return auto_writer


def _payload(title):
    return json.dumps({"title": title, "content": "본문", "image_url": "https://example.com/a.webp"})


def test_offbrand_webhook_exits_zero(aw, tmp_path, monkeypatch):
    # 2026-10-20 실패 재현: n8n이 '작업장 차양' 주제를 보냄 → 차단은 정상 동작이므로 exit 0
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "out.txt"))
    with pytest.raises(SystemExit) as e:
        aw.run_webhook_mode(_payload("광주 작업장 차양 설치의 안전 기준과 정기 유지관리 체크리스트"))
    assert e.value.code == 0


def test_offbrand_webhook_writes_blocked_output(aw, tmp_path, monkeypatch):
    out = tmp_path / "out.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    with pytest.raises(SystemExit):
        aw.run_webhook_mode(_payload("공장 천막 설치 비용 총정리"))
    text = out.read_text(encoding="utf-8")
    assert "blocked=1" in text
    assert "blocked_title=공장 천막 설치 비용 총정리" in text


def test_offbrand_webhook_without_github_output(aw, monkeypatch):
    # 로컬 실행(GITHUB_OUTPUT 없음)에서도 예외 없이 exit 0
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    with pytest.raises(SystemExit) as e:
        aw.run_webhook_mode(_payload("작업장 어닝 시공 사례"))
    assert e.value.code == 0
