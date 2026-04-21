#!/usr/bin/env python3
"""Generate sitemap.xml for wocs.kr.

Whitelist-based scan to prevent the earlier OneDrive contamination bug:
only known web-served directories are walked, and an explicit blacklist
drops any path that slipped through. index.html is normalised to the
directory URL (e.g. about/index.html -> https://wocs.kr/about/).
"""
import os
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

    results.sort(key=lambda t: t[0])
    return results


def build_sitemap(entries):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for rel, full in entries:
        loc = url_for(rel)
        basename = os.path.basename(rel)
        priority = "1.0" if basename in MAIN_PAGES else "0.6"
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d")
        except OSError:
            mtime = today
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
