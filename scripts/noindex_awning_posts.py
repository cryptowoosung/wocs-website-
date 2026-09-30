#!/usr/bin/env python3
"""어닝·천막·차양 주제 블로그 글을 자동 탐지해 noindex 처리한다.

wocs.kr 은 글램핑 전용이므로 어닝·천막 글은 색인에서 빼되(noindex, follow)
링크 자산은 유지하고 독자를 자매 브랜드로 안내한다. 글 자체는 삭제하지 않는다.

탐지: <title> 또는 <h1> 에 BRAND_RE 가 걸리고 "글램핑" 이 없는 글.
      "글램핑 어닝" 처럼 복합 주제인 글은 글램핑 사이트의 콘텐츠이므로 유지한다.

처리: robots 메타 -> noindex, follow
      본문 최상단(첫 </h1> 뒤) -> 자매 브랜드 안내 박스
      assets/js/blog-data.js 해당 항목 -> noindex:true  (목록 UI·llms.txt 가 읽음)

여러 번 실행해도 결과가 같다(멱등).
실행: python scripts/noindex_awning_posts.py [--list] [--dry-run]
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_blog_static as bbs  # noqa: E402

# 자매 브랜드(우성어닝) 소관 주제
BRAND_RE = re.compile(r"(어닝|천막|차양|캐노피|캠프시스템)")
# 글램핑이 같이 언급되면 wocs.kr 콘텐츠로 본다
KEEP_WORD = "글램핑"

# 오탐 수동 제외 목록 (파일명). "캠프시스템" 은 WOCS 자체 브랜드명이기도 해서
# 글램핑 구조물 글이 걸릴 수 있다.
EXCLUDE = frozenset()

ROBOTS = '<meta name="robots" content="noindex, follow">'
NOTICE_MARK = 'class="notice"'
NOTICE = (
    '<p class="notice" style="padding:12px;border-left:3px solid var(--gold,#c9a227);'
    'margin:16px 0">이 글의 주제인 어닝·천막 시공은 자매 브랜드 '
    '<a href="https://glampingtentgo.com/">우성어닝</a>에서 전문으로 다룹니다.</p>'
)

_TAG = re.compile(r"<[^>]+>")


def _text(html, pattern):
    m = re.search(pattern, html, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", _TAG.sub("", m.group(1))).strip()


def classify(path):
    """(title, matches, is_target) 반환. is_target 이면 noindex 대상."""
    html = io.open(path, encoding="utf-8", newline="").read()
    title = _text(html, r"<title[^>]*>(.*?)</title>")
    title = re.split(r"\s*\|\s*", title)[0].strip()
    h1 = _text(html, r"<h1[^>]*>(.*?)</h1>")
    hay = title + " " + h1
    matches = sorted(set(BRAND_RE.findall(hay)))
    is_target = (
        bool(matches)
        and KEEP_WORD not in hay
        and os.path.basename(path) not in EXCLUDE
    )
    return title, matches, is_target


def find_targets():
    """[(path, title, matches)] — noindex 대상, 파일명 순."""
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "auto_post_*.html"))):
        title, matches, is_target = classify(path)
        if is_target:
            out.append((path, title, matches))
    return out


# ── HTML 처리 ──────────────────────────────────────────────────────────────

def apply_html(path, dry_run=False):
    text = io.open(path, encoding="utf-8", newline="").read()
    original = text
    did = []

    if re.search(r'<meta\s+name="robots"[^>]*>', text, re.I):
        new = re.sub(r'<meta\s+name="robots"[^>]*>', ROBOTS, text, flags=re.I)
        if new != text:
            text = new
            did.append("robots 교체")
    elif ROBOTS not in text:
        text = text.replace("</head>", "  " + ROBOTS + "\n</head>", 1)
        did.append("robots 삽입")

    if NOTICE_MARK not in text:
        m = re.search(r"</h1>", text)
        if m:
            text = text[: m.end()] + "\n  " + NOTICE + text[m.end():]
            did.append("안내 박스")

    if text != original and not dry_run:
        io.open(path, "w", encoding="utf-8", newline="").write(text)
    return did


# ── blog-data.js 처리 ──────────────────────────────────────────────────────

def target_post_ids(target_files):
    """blog-data.js 항목 중 대상 파일에 해당하는 id 집합.

    제목 문자열 대신 resolve_links(date + id 순서) 로 매핑한다.
    오래된 글의 title 이 'bt12' 같은 번역 키여서 제목 매칭이 불가능하기 때문.
    """
    data = io.open(os.path.join(ROOT, "assets", "js", "blog-data.js"),
                   encoding="utf-8").read()
    posts = bbs.parse_blog_data(data)
    bbs.resolve_links(posts)
    want = {os.path.basename(p) for p in target_files}
    ids = set()
    for p in posts:
        href = p.get("href", "")
        if href.startswith("../content/") and os.path.basename(href) in want:
            ids.add(p["id"])
    return ids


def apply_blog_data(ids, dry_run=False):
    """해당 id 항목의 featured 필드 뒤에 noindex:true 를 넣는다."""
    path = os.path.join(ROOT, "assets", "js", "blog-data.js")
    text = io.open(path, encoding="utf-8", newline="").read()
    added = 0
    for pid in sorted(ids):
        m = re.search(r"\n\{\s*\n\s*id:%d\b" % pid, text)
        if not m:
            m = re.search(r"id:%d\b" % pid, text)
        if not m:
            print("    blog-data: id %d 못 찾음" % pid)
            continue
        chunk_end = text.find("\n}", m.end())
        chunk = text[m.start():chunk_end if chunk_end > 0 else len(text)]
        if "noindex:true" in chunk:
            continue
        fm = re.search(r"featured:(?:true|false),", chunk)
        if not fm:
            print("    blog-data: id %d featured 필드 없음" % pid)
            continue
        at = m.start() + fm.end()
        text = text[:at] + " noindex:true," + text[at:]
        added += 1
    if added and not dry_run:
        io.open(path, "w", encoding="utf-8", newline="").write(text)
    return added


# ── 출력 ───────────────────────────────────────────────────────────────────

def print_list(targets):
    rows = [(os.path.basename(p), t, "·".join(m)) for p, t, m in targets]
    fw = max([len(r[0]) for r in rows] + [4])
    tw = min(max([len(r[1]) for r in rows] + [2]), 52)
    print("| %-*s | %-*s | 매칭 |" % (fw, "파일", tw, "제목"))
    print("|%s|%s|------|" % ("-" * (fw + 2), "-" * (tw + 2)))
    for f, t, m in rows:
        print("| %-*s | %-*s | %s |" % (fw, f, tw, t[:tw], m))
    print()
    print("대상: %d편" % len(rows))

    # 1-4: "캠프시스템" 만으로 걸린 글 = 오탐 가능
    only_camp = [r for r in rows if r[2] == "캠프시스템"]
    print()
    if only_camp:
        print('*** "캠프시스템" 단독 매칭 (오탐 검토 필요) ***')
        for f, t, _ in only_camp:
            print("   -", f, "|", t)
    else:
        print('"캠프시스템" 단독 매칭: 0건 (오탐 없음)')


def main():
    targets = find_targets()
    if "--list" in sys.argv:
        print_list(targets)
        return 0

    dry_run = "--dry-run" in sys.argv
    for path, title, _ in targets:
        did = apply_html(path, dry_run)
        name = os.path.basename(path)
        print("  %-42s %s" % (name, ", ".join(did) if did else "변경 없음 (이미 적용)"))

    ids = target_post_ids([p for p, _, _ in targets])
    added = apply_blog_data(ids, dry_run)
    print()
    print(("[DRY-RUN] " if dry_run else "")
          + "HTML %d편 / blog-data.js 대상 id %d개 (신규 플래그 %d건)"
          % (len(targets), len(ids), added))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
