#!/usr/bin/env python3
"""Generate sitemap.xml for wocs.kr.

Whitelist-based scan to prevent the earlier OneDrive contamination bug:
only known web-served directories are walked, and an explicit blacklist
drops any path that slipped through. index.html is normalised to the
directory URL (e.g. about/index.html -> https://wocs.kr/about/).
"""
import os
import re
import subprocess
from datetime import datetime

SITE_URL = "https://wocs.kr"
SITEMAP_PATH = "sitemap.xml"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Only these top-level dirs are scanned. Repo root is handled specially
# (top-level HTML only, no recursion).
ALLOWED_DIRS = (
    "about",
    "products",
    "occasions",
    "portfolio",
    "resources",
    "legal",
    "contact",
    "content",
    "gallery",
    "project",
)

# Any full path containing one of these substrings is rejected outright.
# Guards against future new dirs that should never appear in sitemap.
EXCLUDED_SUBSTRINGS = (
    "OneDrive",
    "node_modules",
    os.sep + "dist" + os.sep,
    "_original-backup",
    "venv",
    ".git" + os.sep,
    os.sep + "public" + os.sep,
    "vite-index.html",
    "draft-",
    "handoff_",
    ".bak",
    ".omc",
    ".bkit",
)

# Exact repo-relative paths that must never be indexed:
#  - *-template / *-detail / blog-post are unrendered boilerplate shells.
#  - privacy.html is a legacy duplicate of legal/privacy.html and is 301'd
#    to it in vercel.json, so only the canonical copy belongs in the sitemap.
EXCLUDED_FILES = frozenset((
    "products/product-template.html",
    "portfolio/case-detail.html",
    "resources/blog-post.html",
    "privacy.html",
))

MAIN_PAGES = {"index.html"}
MAX_DEPTH_FROM_BASE = 3


def should_skip(abs_path):
    # Test against the path RELATIVE to REPO_ROOT to avoid false positives
    # when the repo itself lives inside a parent named like one of the
    # blacklist entries (e.g. C:\Users\user\OneDrive\...).
    try:
        rel = os.path.relpath(abs_path, REPO_ROOT)
    except ValueError:
        rel = abs_path
    if rel.replace(os.sep, "/") in EXCLUDED_FILES:
        return True
    # Normalise separator to make cross-platform checks work
    rel_sep = os.sep + rel + os.sep
    return any(pat in rel_sep for pat in EXCLUDED_SUBSTRINGS)


def url_for(rel_posix):
    # Normalise <dir>/index.html to /<dir>/
    if rel_posix == "index.html":
        return SITE_URL + "/"
    if rel_posix.endswith("/index.html"):
        parent = rel_posix[: -len("/index.html")]
        return SITE_URL + "/" + parent + "/"
    return SITE_URL + "/" + rel_posix


NOINDEX_RE = re.compile(
    r'<meta\s+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.I
)


def is_noindex(full):
    """robots 메타에 noindex 가 있으면 sitemap 에서 뺀다.

    하드코딩 목록 대신 메타를 읽는 이유: 앞으로 어떤 글을 noindex 하더라도
    생성기를 고치지 않고 자동으로 반영된다 (색인 정책의 단일 출처).
    """
    try:
        with open(full, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(8192)  # robots 메타는 <head> 안에 있다
    except OSError:
        return False
    return bool(NOINDEX_RE.search(head))


def collect_html_files():
    seen = set()
    results = []

    # 1) Root-level HTML files only (no recursion)
    for f in sorted(os.listdir(REPO_ROOT)):
        full = os.path.join(REPO_ROOT, f)
        if not os.path.isfile(full) or not f.endswith(".html"):
            continue
        if should_skip(full):
            continue
        rel = f
        if rel in seen:
            continue
        seen.add(rel)
        results.append((rel, full))

    # 2) Whitelisted top dirs (recursive, depth-limited)
    for dirname in ALLOWED_DIRS:
        base = os.path.join(REPO_ROOT, dirname)
        if not os.path.isdir(base):
            continue
        base_depth = base.count(os.sep)
        for root, dirs, files in os.walk(base):
            # Depth limit (prevent runaway)
            if root.count(os.sep) - base_depth > MAX_DEPTH_FROM_BASE:
                dirs[:] = []
                continue
            # Prune excluded subdirs up-front
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
            for fname in files:
                if not fname.endswith(".html"):
                    continue
                full = os.path.join(root, fname)
                if should_skip(full):
                    continue
                rel = os.path.relpath(full, REPO_ROOT).replace(os.sep, "/")
                if rel in seen:
                    continue
                seen.add(rel)
                results.append((rel, full))

    results = [(rel, full) for rel, full in results if not is_noindex(full)]
    results.sort(key=lambda t: t[0])
    return results


def git_lastmod_map():
    """Map repo-relative posix path -> ISO commit date of its last commit.

    A single `git log --name-only` walk is used instead of one
    `git log -1 -- <file>` per URL: it is equivalent (the first commit a
    path appears in, walking newest-first, IS its last commit) but runs in
    one process instead of ~200.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--pretty=format:%cI", "--name-only"],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}

    dates = {}
    current = None
    for line in out.splitlines():
        if line.startswith(""):
            current = line[1:].strip()
        elif line.strip() and current:
            dates.setdefault(line.strip(), current)
    return dates


def git_dirty_paths():
    """Repo-relative posix paths with uncommitted changes.

    Their last *commit* date is stale, so they are dated today instead.
    """
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return frozenset()
    return frozenset(
        line[3:].strip().strip('"') for line in out.splitlines() if line[3:].strip()
    )


def lastmod_for(rel_posix, full, git_dates, fallback, dirty=frozenset()):
    """Real last-modified date: git history first, mtime only as a fallback."""
    if rel_posix in dirty:
        return fallback
    iso = git_dates.get(rel_posix)
    if iso:
        return iso
    # Untracked or newly added file - fall back to filesystem mtime.
    try:
        return datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d")
    except OSError:
        return fallback


def build_sitemap(entries):
    today = datetime.now().strftime("%Y-%m-%d")
    git_dates = git_lastmod_map()
    dirty = git_dirty_paths()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for rel, full in entries:
        loc = url_for(rel)
        basename = os.path.basename(rel)
        priority = "1.0" if basename in MAIN_PAGES else "0.6"
        mtime = lastmod_for(rel.replace(os.sep, "/"), full, git_dates, today, dirty)
        lines.append("  <url>")
        lines.append("    <loc>" + loc + "</loc>")
        lines.append("    <lastmod>" + mtime + "</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>" + priority + "</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    entries = collect_html_files()
    print("HTML 파일 " + str(len(entries)) + "개 발견")
    sitemap = build_sitemap(entries)
    out_path = os.path.join(REPO_ROOT, SITEMAP_PATH)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("sitemap.xml 갱신 완료 (" + str(len(entries)) + " URLs)")
    for rel, _ in entries[:5]:
        print("  " + url_for(rel))
    if len(entries) > 5:
        print("  ... (" + str(len(entries) - 5) + " more)")


if __name__ == "__main__":
    main()
