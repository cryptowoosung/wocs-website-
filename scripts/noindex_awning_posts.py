#!/usr/bin/env python3
"""어닝·천막 주제 블로그 글을 noindex 처리하고 자매 브랜드 안내를 넣는다.

wocs.kr 은 글램핑 전용이므로 어닝·천막 글은 색인에서 빼되(noindex, follow),
링크 자산은 유지하고 독자를 자매 브랜드로 안내한다. 글 자체는 삭제하지 않는다.

여러 번 실행해도 결과가 같다(멱등).
실행: python scripts/noindex_awning_posts.py [--dry-run]
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = (
    "content/auto_post_2026-09-07.html",
    "content/auto_post_2026-08-03_2.html",
    "content/auto_post_2026-07-30.html",
    "content/auto_post_2026-07-27_2.html",
)

ROBOTS = '<meta name="robots" content="noindex, follow">'
NOTICE_MARK = 'class="notice"'
NOTICE = (
    '<p class="notice" style="padding:12px;border-left:3px solid var(--gold,#c9a227);'
    'margin:16px 0">이 글의 주제인 어닝·천막 시공은 자매 브랜드 '
    '<a href="https://glampingtentgo.com/">우성어닝</a>에서 전문으로 다룹니다.</p>'
)


def process(path, dry_run=False):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    text = io.open(full, encoding="utf-8", newline="").read()
    original = text
    did = []

    # 1) robots 메타: 있으면 교체, 없으면 </head> 앞에 삽입
    if re.search(r'<meta\s+name="robots"[^>]*>', text, re.I):
        new, n = re.subn(r'<meta\s+name="robots"[^>]*>', ROBOTS, text, flags=re.I)
        if n and new != text:
            text = new
            did.append("robots 교체")
    elif ROBOTS not in text:
        text = text.replace("</head>", "  " + ROBOTS + "\n</head>", 1)
        did.append("robots 삽입")

    # 2) 첫 </h1> 바로 뒤에 안내 박스
    if NOTICE_MARK not in text:
        m = re.search(r"</h1>", text)
        if m:
            text = text[: m.end()] + "\n  " + NOTICE + text[m.end():]
            did.append("안내 박스 삽입")

    if text != original and not dry_run:
        io.open(full, "w", encoding="utf-8", newline="").write(text)
    return did


def main():
    dry_run = "--dry-run" in sys.argv
    for path in TARGETS:
        did = process(path, dry_run)
        if did is None:
            print("  %-42s MISSING" % path)
        elif did:
            print("  %-42s %s" % (path, ", ".join(did)))
        else:
            print("  %-42s 변경 없음 (이미 적용)" % path)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
