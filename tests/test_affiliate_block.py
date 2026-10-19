"""제휴 상품 블록 렌더러 테스트 (affiliate_block.py + shared/affiliate_block.json)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import affiliate_block as ab  # noqa: E402

DISCLOSURE = "#광고 #쿠팡파트너스 — 이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받습니다"
ENV = {"COUPANG_LINK_1": "https://link.coupang.com/a/one",
       "COUPANG_LINK_2": "https://link.coupang.com/a/two",
       "COUPANG_LINK_3": "https://link.coupang.com/a/three"}


def test_disclosure_is_first_text_in_block():
    html = ab.render("wocs", "3", env=ENV)
    assert html.startswith('<aside class="wocs-aff"')
    first_p = html.index("<p")
    assert DISCLOSURE in html[first_p:first_p + 300]
    assert html.index(DISCLOSURE) < html.index("관련 캠핑용품")


def test_coupang_only_when_naver_empty():
    html = ab.render("wocs", "1", env=ENV)
    assert "https://link.coupang.com/a/one" in html
    assert "네이버" not in html
    assert html.count("<a ") == 1
    assert 'rel="sponsored nofollow noopener"' in html


def test_naver_link_shown_when_set():
    env = dict(ENV, NAVER_CONNECT_LINK_2="https://naver.me/abc")
    html = ab.render("wocs", "2", env=env)
    assert html.count("<a ") == 2
    assert "#네이버쇼핑커넥트" in html


def test_empty_links_render_nothing():
    assert ab.render("wocs", "2", env={}) == ""
    assert ab.render("wocs", "2", env={"COUPANG_LINK_2": "javascript:alert(1)"}) == ""


def test_pick_slot_keywords_then_category():
    assert ab.pick_slot("wocs", "겨울 글램핑 난방은 어떻게 하나요?", "cat_startup") == "1"
    assert ab.pick_slot("wocs", "장마철 글램핑 데크 관리", "cat_startup") == "2"
    assert ab.pick_slot("wocs", "글램핑 창업 인허가 절차", "cat_construction") == "2"
    assert ab.pick_slot("wocs", "글램핑 창업 인허가 절차", "cat_unknown") == "3"


def test_glampingtentgo_heading_and_note():
    html = ab.render("glampingtentgo", "2", env=ENV)
    assert "관련 어닝·천막 보수용품" in html
    assert "천막 보수" in html


def test_url_is_escaped():
    html = ab.render("wocs", "1", env={"COUPANG_LINK_1": 'https://x.com/"><script>'})
    assert "<script>" not in html
