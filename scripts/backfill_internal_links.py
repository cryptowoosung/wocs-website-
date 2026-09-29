#!/usr/bin/env python3
"""기존 content/auto_post_*.html 일회성 후처리.

1. 금칙어 "글람핑" -> "글램핑" 강제 치환
2. 내부링크(href="/products/ · href="/content/)가 3개 미만인 글에
   본문 끝 '관련 제품' 섹션으로 products/ 링크 3개 추가

상품은 글 제목 키워드와 매칭하고, 매칭이 없으면
dome-tent / safari-tents / universal-joint 를 기본값으로 쓴다.
여러 번 실행해도 결과가 같다(멱등).

실행: python scripts/backfill_internal_links.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wocs_internal_links as wil  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BANNED_WORDS = (("글람핑", "글램핑"),)

# 이 앵커 바로 앞에 '관련 제품' 섹션을 넣는다 (FAQ·E-E-A-T 뒤, 상담 CTA 앞).
CTA_ANCHOR = '<div class="post-cta">'
SECTION_MARKER = 'class="related-products"'


def post_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if not m:
        return ""
    return re.split(r"\s*\|\s*", re.sub(r"<[^>]+>", "", m.group(1)))[0].strip()


def article_text(html):
    """상품 매칭의 보조 신호로 쓸 본문 텍스트 (스크립트·스타일 제외)."""
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))


def related_section(products):
    items = "\n".join(
        '      <li><a href="' + p["url"] + '">' + p["name"] + "</a></li>"
        for p in products
    )
    return (
        '  <section class="related-products">\n'
        "    <h2>관련 제품</h2>\n"
        "    <ul>\n" + items + "\n"
        "    </ul>\n"
        "  </section>\n"
    )


def process(path, products, dry_run=False):
    """한 파일을 처리하고 (금칙어치환수, 링크추가수, 처리전링크수)를 돌려준다."""
    html = io.open(path, encoding="utf-8", newline="").read()
    original = html

    banned = 0
    for bad, good in BANNED_WORDS:
        banned += html.count(bad)
        html = html.replace(bad, good)

    before_links = wil.count_internal_links(html)
    added = 0

    if before_links < wil.MIN_INTERNAL_LINKS and SECTION_MARKER not in html:
        picks = wil.match_products(post_title(html), products, limit=3,
                                   body=article_text(html))
        if picks and CTA_ANCHOR in html:
            section = related_section(picks)
            idx = html.rindex(CTA_ANCHOR)
            # 앵커가 들여쓰기된 줄의 시작으로 되돌아가 그 앞에 끼워 넣는다.
            line_start = html.rfind("\n", 0, idx) + 1
            html = html[:line_start] + section + html[line_start:]
            added = len(picks)

    if html != original and not dry_run:
        io.open(path, "w", encoding="utf-8", newline="").write(html)
    return banned, added, before_links


def main():
    dry_run = "--dry-run" in sys.argv
    products = wil.load_products(ROOT)
    paths = sorted(glob.glob(os.path.join(ROOT, "content", "auto_post_*.html")))

    files, tot_banned, tot_added = 0, 0, 0
    for path in paths:
        banned, added, before = process(path, products, dry_run)
        if banned or added:
            files += 1
            tot_banned += banned
            tot_added += added

    print(("[DRY-RUN] " if dry_run else "")
          + "대상 %d편 / 수정 %d편" % (len(paths), files))
    print("  금칙어 치환: %d건" % tot_banned)
    print("  내부링크 추가: %d개" % tot_added)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
