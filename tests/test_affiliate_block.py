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
    assert COMBINED in html


COMBINED = "#광고 — 이 포스팅은 쿠팡 파트너스 및 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다"
NAVER_ENV = dict(ENV, NAVER_CONNECT_LINK_1="https://naver.me/one",
                 NAVER_CONNECT_LINK_2="https://naver.me/two",
                 NAVER_CONNECT_LINK_3="https://naver.me/three")


def test_naver_button_next_to_coupang_with_combined_disclosure():
    html = ab.render("wocs", "1", env=NAVER_ENV)
    assert html.count(COMBINED) == 1
    assert "#쿠팡파트너스" not in html and "#네이버쇼핑커넥트" not in html  # 개별 고지문 대신 합친 1문장
    coupang, naver = html.index("https://link.coupang.com/a/one"), html.index("https://naver.me/one")
    assert coupang < naver
    assert html.count('rel="sponsored nofollow noopener"') == 2
    assert ">네이버에서 보기</a>" in html and ">쿠팡에서 보기</a>" in html
    assert "루메나 온풍기 · 휴대용 캠핑용 온풍기" in html


def test_naver_only_uses_naver_disclosure_and_product():
    html = ab.render("wocs", "3", env={"NAVER_CONNECT_LINK_3": "https://naver.me/three"})
    assert html.count("<a ") == 1
    assert "#광고 #네이버쇼핑커넥트" in html
    assert "발키다 캠핑용 랜턴" in html
    assert "쿠팡" not in html


def test_every_slot_has_naver_product():
    for slot, item in ab.load_spec()["slots"].items():
        assert item.get("naver_product"), slot


def test_top_notice_combined_sentence_when_both():
    html = ab.render_top_notice("3", env=NAVER_ENV)
    assert COMBINED in html
    assert html.startswith('<p class="wocs-aff-top"')


def test_top_notice_naver_only():
    html = ab.render_top_notice("2", env={"NAVER_CONNECT_LINK_2": "https://naver.me/two"})
    assert "#광고 — 이 글에는 네이버 쇼핑 커넥트 제휴 링크가 포함되어 있으며" in html


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


TOP = "#광고 — 이 글에는 쿠팡 파트너스 제휴 링크가 포함되어 있으며 일정액의 수수료를 제공받습니다"


def test_top_notice_exact_text_for_coupang():
    assert TOP in ab.render_top_notice("2", env=ENV)


def test_top_notice_names_both_programs():
    html = ab.render_top_notice("2", env=dict(ENV, NAVER_CONNECT_LINK_2="https://naver.me/abc"))
    assert COMBINED in html


def test_top_notice_empty_without_links():
    assert ab.render_top_notice("2", env={}) == ""


def test_url_is_escaped():
    html = ab.render("wocs", "1", env={"COUPANG_LINK_1": 'https://x.com/"><script>'})
    assert "<script>" not in html
