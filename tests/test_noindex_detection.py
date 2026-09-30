"""noindex 자동 탐지 로직 테스트 (scripts/noindex_awning_posts.py)."""
import importlib.util
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def _load():
    path = os.path.join(ROOT, "scripts", "noindex_awning_posts.py")
    spec = importlib.util.spec_from_file_location("noindex_awning_posts", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def nap():
    return _load()


def _post(tmp_path, title, h1=None):
    """탐지에 필요한 최소 구조의 블로그 글 HTML 파일을 만든다."""
    body = (
        "<html><head><title>" + title + " | WOCS</title>"
        '<meta name="robots" content="index, follow">'
        "</head><body>"
        '<h1 class="post-title">' + (h1 or title) + "</h1>"
        "<p>본문</p></body></html>"
    )
    p = tmp_path / "auto_post_2026-01-01.html"
    io.open(str(p), "w", encoding="utf-8", newline="").write(body)
    return str(p)


# ─── 탐지 ──────────────────────────────────────────────────────────────────

def test_awning_title_is_detected(tmp_path, nap):
    """어닝 주제 글은 noindex 대상이다."""
    # Arrange
    path = _post(tmp_path, "광주 어닝 시공 비용 종류별 가격 2026")

    # Act
    title, matches, is_target = nap.classify(path)

    # Assert
    assert is_target is True
    assert matches == ["어닝"]
    assert title == "광주 어닝 시공 비용 종류별 가격 2026"


def test_glamping_composite_title_is_kept(tmp_path, nap):
    """제목에 '글램핑'이 함께 있으면 wocs.kr 콘텐츠이므로 대상에서 제외한다."""
    # Arrange
    path = _post(tmp_path, "광주 어닝 시공 비용 2026: 글램핑 최적화 전략")

    # Act
    _, matches, is_target = nap.classify(path)

    # Assert
    assert matches == ["어닝"]          # 단어는 걸리지만
    assert is_target is False           # 글램핑 예외로 유지


@pytest.mark.parametrize("word", ["어닝", "천막", "차양", "캐노피", "캠프시스템"])
def test_every_brand_word_is_detected(tmp_path, nap, word):
    path = _post(tmp_path, "나주 " + word + " 시공 가이드")
    _, matches, is_target = nap.classify(path)
    assert is_target is True
    assert word in matches


def test_pure_glamping_title_is_not_detected(tmp_path, nap):
    path = _post(tmp_path, "순천 글램핑 창업 비용과 절차")
    _, matches, is_target = nap.classify(path)
    assert matches == []
    assert is_target is False


def test_h1_is_also_scanned(tmp_path, nap):
    """<title>에 없고 <h1>에만 있어도 탐지된다."""
    path = _post(tmp_path, "나주 시설 시공 가이드", h1="나주 캐노피 설치 가이드")
    _, matches, is_target = nap.classify(path)
    assert matches == ["캐노피"]
    assert is_target is True


def test_exclude_list_is_honoured(tmp_path, nap, monkeypatch):
    """EXCLUDE 에 올린 파일은 단어가 걸려도 대상이 아니다."""
    path = _post(tmp_path, "전남 캠프시스템 구조물 시공")
    monkeypatch.setattr(nap, "EXCLUDE", frozenset({os.path.basename(path)}))
    _, _, is_target = nap.classify(path)
    assert is_target is False


# ─── 발행된 글 상태 (회귀 방지) ──────────────────────────────────────────────

def test_all_detected_posts_are_noindexed(nap):
    """탐지 대상 전부에 noindex 메타가 적용돼 있어야 한다."""
    missing = []
    for path, _, _ in nap.find_targets():
        html = io.open(path, encoding="utf-8").read()
        if 'content="noindex' not in html:
            missing.append(os.path.basename(path))
    assert missing == []


def test_detected_posts_are_absent_from_sitemap(nap):
    sitemap = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    leaked = [
        os.path.basename(p) for p, _, _ in nap.find_targets()
        if os.path.basename(p) in sitemap
    ]
    assert leaked == []
