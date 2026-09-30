#!/usr/bin/env python3
"""3단계: 자매 브랜드(우성어닝) 안내 링크를 공용 푸터에 추가.

푸터는 두 곳에서 렌더된다:
  1) assets/js/wocs-footer.js  — 런타임에 #wocs-footer 를 innerHTML 로 덮어씀
  2) 각 HTML 의 <p class="biz-line"> — JS 미실행/크롤러용 서버 렌더 폴백
둘 다 넣어야 사용자와 크롤러 모두에게 보인다.

여러 번 실행해도 결과가 같다(멱등).
실행: python scripts/add_sister_site_link.py [--dry-run]
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKER = 'class="sister-site"'
ANCHOR = '<p class="biz-line"'

# 문구는 지시대로 고정. style 만 기존 푸터 톤(골드 #c9a96e)에 맞춤.
SISTER_LINE = (
    '<p class="sister-site" style="font-size:12px;margin:8px 0 0">'
    '<a href="https://glampingtentgo.com/" rel="noopener" target="_blank" '
    'style="color:#c9a96e;text-decoration:none">'
    '어닝·천막·전동어닝 시공은 자매 브랜드 우성어닝 →</a></p>'
)


def targets():
    """푸터가 하드코딩된 HTML + 푸터 생성 JS."""
    found = []
    for pattern in ("*.html", "*/*.html", "*/*/*.html"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            if rel.startswith("content/") or "OneDrive" in rel:
                continue
            found.append(path)
    found.append(os.path.join(ROOT, "assets", "js", "wocs-footer.js"))
    return found


def process(path, dry_run=False):
    """ANCHOR 앞에 SISTER_LINE 을 끼워 넣고 삽입 건수를 반환."""
    try:
        text = io.open(path, encoding="utf-8", newline="").read()
    except (OSError, UnicodeDecodeError):
        return 0
    if ANCHOR not in text or MARKER in text:
        return 0
    count = text.count(ANCHOR)
    out = text.replace(ANCHOR, SISTER_LINE + ANCHOR)
    if not dry_run:
        io.open(path, "w", encoding="utf-8", newline="").write(out)
    return count


def main():
    dry_run = "--dry-run" in sys.argv
    files, total = 0, 0
    for path in targets():
        n = process(path, dry_run)
        if n:
            files += 1
            total += n
    print(("[DRY-RUN] " if dry_run else "")
          + "삽입: %d개 파일 / %d곳" % (files, total))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
