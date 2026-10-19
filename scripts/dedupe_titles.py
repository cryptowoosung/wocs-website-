#!/usr/bin/env python3
"""제목이 같은 블로그 글 묶음에서 1편만 남기고 나머지를 색인에서 뺀다.

남길 글: 내부링크(/products/·/content/)가 많은 글, 같으면 최근(파일명이 뒤인) 글.
나머지: robots -> noindex, follow / canonical -> 남긴 글 URL / blog-data.js noindex:true
        (sitemap·llms.txt·정적 목록은 update_sitemap.py 등이 noindex 를 읽어 제외)
여러 번 실행해도 결과가 같다(멱등).

실행: python scripts/dedupe_titles.py [--dry-run]
"""
import glob
import io
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import noindex_awning_posts as nap  # noqa: E402
import wocs_internal_links as wil  # noqa: E402

SITE_URL = "https://wocs.kr"
CANONICAL_RE = re.compile(r'<link\s+rel="canonical"[^>]*>', re.I)


def title_key(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return re.sub(r"\s+", "", m.group(1)) if m else ""


def find_groups():
    """{제목: [(파일명, 내부링크수)]} — 2편 이상인 묶음만"""
    groups = defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "auto_post_*.html"))):
        html = io.open(path, encoding="utf-8", newline="").read()
        groups[title_key(html)].append((os.path.basename(path), wil.count_internal_links(html)))
    return {t: fs for t, fs in groups.items() if t and len(fs) > 1}


def pick_keeper(files):
    # 내부링크 많은 순, 같으면 최근(파일명 큰) 순
    return max(files, key=lambda f: (f[1], f[0]))[0]


def apply_dup(fname, keeper, dry_run=False):
    path = os.path.join(ROOT, "content", fname)
    text = io.open(path, encoding="utf-8", newline="").read()
    original = text
    canonical = '<link rel="canonical" href="%s/content/%s">' % (SITE_URL, keeper)
    if CANONICAL_RE.search(text):
        text = CANONICAL_RE.sub(canonical, text, count=1)
    else:
        text = text.replace("</head>", "  " + canonical + "\n</head>", 1)
    if re.search(r'<meta\s+name="robots"[^>]*>', text, re.I):
        text = re.sub(r'<meta\s+name="robots"[^>]*>', nap.ROBOTS, text, count=1, flags=re.I)
    else:
        text = text.replace("</head>", "  " + nap.ROBOTS + "\n</head>", 1)
    if text != original and not dry_run:
        io.open(path, "w", encoding="utf-8", newline="").write(text)
    return text != original


def main():
    dry_run = "--dry-run" in sys.argv
    losers = []
    for title, files in find_groups().items():
        keeper = pick_keeper(files)
        print("남김 %s | 제목 %s" % (keeper, title[:40]))
        for fname, links in files:
            if fname == keeper:
                continue
            changed = apply_dup(fname, keeper, dry_run)
            losers.append(os.path.join(ROOT, "content", fname))
            print("  noindex+canonical %s (내부링크 %d) %s" % (fname, links, "수정" if changed else "이미 적용"))
    added = nap.apply_blog_data(nap.target_post_ids(losers), dry_run) if losers else 0
    print(("[DRY-RUN] " if dry_run else "") + "중복 %d편 처리, blog-data noindex 신규 %d건" % (len(losers), added))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
