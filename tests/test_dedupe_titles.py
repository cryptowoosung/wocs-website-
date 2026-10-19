"""제목 중복 글 처리 회귀 테스트 (scripts/dedupe_titles.py)."""
import glob
import io
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import dedupe_titles as dt  # noqa: E402

NOINDEX = re.compile(r'<meta\s+name="robots"[^>]*noindex', re.I)


def _posts():
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "auto_post_*.html"))):
        yield os.path.basename(path), io.open(path, encoding="utf-8").read()


def test_pick_keeper_prefers_links_then_recent():
    assert dt.pick_keeper([("a_2026-01-01.html", 5), ("a_2026-02-01.html", 3)]) == "a_2026-01-01.html"
    assert dt.pick_keeper([("a_2026-01-01.html", 3), ("a_2026-02-01.html", 3)]) == "a_2026-02-01.html"


def test_no_two_indexable_posts_share_a_title():
    groups = defaultdict(list)
    for name, html in _posts():
        if not NOINDEX.search(html):
            groups[dt.title_key(html)].append(name)
    assert {t: fs for t, fs in groups.items() if len(fs) > 1} == {}


def test_noindexed_duplicates_point_canonical_to_kept_post():
    for title, files in dt.find_groups().items():
        keeper = dt.pick_keeper(files)
        for name, _ in files:
            if name == keeper:
                continue
            html = io.open(os.path.join(ROOT, "content", name), encoding="utf-8").read()
            assert 'href="https://wocs.kr/content/%s"' % keeper in html
            assert NOINDEX.search(html)


def test_noindexed_duplicates_absent_from_sitemap():
    sitemap = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    for title, files in dt.find_groups().items():
        keeper = dt.pick_keeper(files)
        assert "/content/" + keeper in sitemap
        for name, _ in files:
            if name != keeper:
                assert "/content/" + name not in sitemap
