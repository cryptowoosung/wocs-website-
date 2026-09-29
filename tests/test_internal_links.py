"""wocs_internal_links + auto_writer 내부링크/금칙어 로직 테스트."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import wocs_internal_links as wil  # noqa: E402


@pytest.fixture(scope="module")
def products():
    return wil.load_products(ROOT)


# ─── 카탈로그 ───────────────────────────────────────────────────────────────

def test_catalog_is_built_from_products_directory(products):
    # Arrange / Act
    slugs = {p["slug"] for p in products}

    # Assert
    assert len(products) >= 20
    assert "dome-tent" in slugs
    assert "safari-tents" in slugs


def test_catalog_excludes_index_and_template(products):
    slugs = {p["slug"] for p in products}
    assert "index" not in slugs
    assert "product-template" not in slugs


def test_catalog_urls_are_root_relative(products):
    assert all(p["url"].startswith("/products/") for p in products)


def test_display_name_stops_at_br_subtitle(products):
    """<h1> 안의 <br> 뒤 부제가 상품명에 붙지 않아야 한다."""
    joint = next(p for p in products if p["slug"] == "universal-joint")
    assert joint["name"] == "무용접 유니버설 조인트"


def test_display_name_has_no_markup(products):
    assert all("<" not in p["name"] and ">" not in p["name"] for p in products)


# ─── 매칭 ──────────────────────────────────────────────────────────────────

def test_match_uses_title_keywords(products):
    picks = wil.match_products("글램핑장 화장실 샤워 설치", products, limit=3)
    assert picks[0]["slug"] == "modular-bath"


def test_match_falls_back_to_defaults_when_nothing_matches(products):
    picks = wil.match_products("zzz nothing relevant zzz", products, limit=3)
    assert [p["slug"] for p in picks] == list(wil.DEFAULT_SLUGS)


def test_match_always_returns_requested_count(products):
    for seed in ("돔텐트", "", "태양광", "존재하지않는키워드"):
        assert len(wil.match_products(seed, products, limit=3)) == 3


def test_title_outweighs_body(products):
    """제목에 있는 키워드가 본문에만 있는 키워드보다 우선한다."""
    picks = wil.match_products("태양광 발전", products, limit=1,
                               body="욕실 욕실 욕실 샤워 화장실")
    assert picks[0]["slug"] == "solar-system"


def test_body_is_used_as_secondary_signal(products):
    """제목이 비어 있어도 본문 신호로 매칭된다 (기본값으로 떨어지지 않음)."""
    picks = wil.match_products("", products, limit=3, body="모듈러 욕실 설치 사례")
    assert "modular-bath" in [p["slug"] for p in picks]


# ─── 링크 카운트 ────────────────────────────────────────────────────────────

def test_count_internal_links_counts_both_products_and_content():
    html = ('<a href="/products/dome-tent.html">a</a>'
            '<a href="/content/auto_post_2026-01-01.html">b</a>')
    assert wil.count_internal_links(html) == 2


def test_count_internal_links_ignores_external_and_empty():
    assert wil.count_internal_links('<a href="https://example.com">x</a>') == 0
    assert wil.count_internal_links("") == 0


# ─── 발행된 글 상태 (회귀 방지) ──────────────────────────────────────────────

def test_every_published_post_has_minimum_internal_links():
    import glob
    paths = glob.glob(os.path.join(ROOT, "content", "auto_post_*.html"))
    assert paths, "content/auto_post_*.html 이 없음"
    short = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            if wil.count_internal_links(fh.read()) < wil.MIN_INTERNAL_LINKS:
                short.append(os.path.basename(path))
    assert short == []


def test_no_banned_word_in_published_posts():
    import glob
    offenders = []
    for path in glob.glob(os.path.join(ROOT, "content", "auto_post_*.html")):
        with open(path, encoding="utf-8") as fh:
            if "글람핑" in fh.read():
                offenders.append(os.path.basename(path))
    assert offenders == []


# ─── auto_writer 후처리 ─────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def aw():
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    import auto_writer
    return auto_writer


def test_apply_banned_words_replaces_all(aw):
    assert aw.apply_banned_words("글람핑과 글람핑") == "글램핑과 글램핑"


def test_apply_banned_words_handles_empty(aw):
    assert aw.apply_banned_words("") == ""
    assert aw.apply_banned_words(None) is None


def test_md_links_to_html(aw):
    out = aw.md_links_to_html("사양은 [D-시리즈 돔](/products/dome-tent.html)입니다.")
    assert out == '사양은 <a href="/products/dome-tent.html">D-시리즈 돔</a>입니다.'


def test_md_links_to_html_leaves_plain_text_alone(aw):
    assert aw.md_links_to_html("대괄호 [강조] 만 있는 문장") == "대괄호 [강조] 만 있는 문장"


def test_enforce_internal_links_adds_section_when_missing(aw):
    topic = {"long_tail": "광주 돔텐트 비용", "keyword": "돔텐트"}
    out = aw.enforce_internal_links("## 질문?\n본문", "돔텐트 창업", topic)
    assert "## 관련 제품" in out
    assert out.count("](/products/") >= aw.MIN_PRODUCT_LINKS


def test_enforce_internal_links_is_noop_when_already_linked(aw):
    topic = {"long_tail": "x", "keyword": "y"}
    content = ("본문 [돔](/products/dome-tent.html) 과 "
               "[사파리](/products/safari-tents.html)")
    assert aw.enforce_internal_links(content, "제목", topic) == content


def test_internal_link_rules_mentions_real_paths(aw):
    rules = aw.internal_link_rules({"long_tail": "돔텐트 비용", "keyword": "돔텐트"})
    assert "### 내부링크 (필수)" in rules
    assert "/products/" in rules
