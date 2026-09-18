"""build_blog_static 파서/링크 배정 단위 테스트: python -m pytest tests/test_build_blog_static.py -q"""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "bbs", Path(__file__).resolve().parent.parent / "scripts" / "build_blog_static.py")
bbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbs)

SAMPLE = r"""var BLOG_POSTS = [
{
  id:12, title:'둘째 글 \'따옴표\'', excerpt:'요약B',
  date:'2026-01-02', category:'cat_startup', featured:false,
  content:'본문'
},
{
  id:11, title:'첫 글', excerpt:'요약A',
  date:'2026-01-02', category:'cat_case', featured:false,
  content:'본문'
},
{
  id:1, title:'bt1', excerpt:'be1',
  date:'2025-12-01', category:'cat_trend', featured:true,
  content:'본문'
}
];
"""


def test_parse_extracts_fields_and_unescapes_quotes():
    posts = bbs.parse_blog_data(SAMPLE)
    assert [p["id"] for p in posts] == [12, 11, 1]
    assert posts[0]["title"] == "둘째 글 '따옴표'"
    assert posts[1]["category"] == "cat_case"


def test_same_day_posts_get_suffix_by_id_order(tmp_path, monkeypatch):
    monkeypatch.setattr(bbs, "CONTENT_DIR", tmp_path)
    (tmp_path / "auto_post_2026-01-02.html").write_text("x")
    (tmp_path / "auto_post_2026-01-02_2.html").write_text("x")
    posts = bbs.parse_blog_data(SAMPLE)
    bbs.resolve_links(posts)
    by_id = {p["id"]: p["href"] for p in posts}
    assert by_id[11] == "../content/auto_post_2026-01-02.html"   # 낮은 id = 먼저 생성 = 접미사 없음
    assert by_id[12] == "../content/auto_post_2026-01-02_2.html"
    assert by_id[1] == "blog-post.html?id=1"                     # 파일 없음 → 뷰어 링크


def test_render_resolves_translation_keys_and_escapes():
    posts = bbs.parse_blog_data(SAMPLE)
    bbs.resolve_links(posts)
    out = bbs.render_static_list(posts, {"bt1": "번역 제목 <b>", "be1": "번역 요약"})
    assert "번역 제목 &lt;b&gt;" in out and "번역 요약" in out
    assert out.count("<article") == 3 and bbs.START in out and bbs.END in out


def test_inject_is_idempotent():
    html = '<div class="blog-grid" id="blogGrid"></div>'
    once = bbs.inject(html, f"{bbs.START}\nA\n{bbs.END}")
    twice = bbs.inject(once, f"{bbs.START}\nB\n{bbs.END}")
    assert once.count(bbs.START) == 1 and "B" in twice and "A" not in twice
