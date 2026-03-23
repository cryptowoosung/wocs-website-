#!/usr/bin/env python3
"""사이트 전체 HTML 파일을 스캔하여 sitemap.xml을 재생성한다."""
import os, glob
from datetime import datetime

SITE_URL = "https://wocs.kr"
SITEMAP_PATH = "sitemap.xml"
EXCLUDE_DIRS = {".github", "node_modules", ".git", "assets", ".omc", ".bkit"}

# index.html이 있는 섹션 메인 페이지는 priority 1.0
MAIN_PAGES = {"index.html"}


def collect_html_files():
    files = []
    for path in glob.glob("**/*.html", recursive=True):
        path = path.replace("\\", "/")
        top_dir = path.split("/")[0] if "/" in path else ""
        if top_dir in EXCLUDE_DIRS:
            continue
        files.append(path)
    files.sort()
    return files


def build_sitemap(files):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for f in files:
        loc = SITE_URL + "/" + f
        basename = f.split("/")[-1]
        priority = "1.0" if basename in MAIN_PAGES else "0.6"
        lines.append("  <url>")
        lines.append("    <loc>" + loc + "</loc>")
        lines.append("    <lastmod>" + today + "</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>" + priority + "</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    files = collect_html_files()
    print("HTML 파일 " + str(len(files)) + "개 발견")
    sitemap = build_sitemap(files)
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("sitemap.xml 갱신 완료 (" + str(len(files)) + " URLs)")


if __name__ == "__main__":
    main()
