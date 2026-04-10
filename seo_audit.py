"""WOCS SEO Audit — generates seo_audit_report.md"""
import os, re, json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = "https://wocs.kr"

def find_html_files():
    files = []
    for p in ROOT.rglob("*.html"):
        parts = p.relative_to(ROOT).parts
        if any(x in parts for x in ("node_modules", ".git", "__pycache__", "dist")):
            continue
        files.append(p)
    return sorted(files)

def read_file(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extract_tag(html, tag, attr=None, val=None):
    """Extract tag content or attribute value."""
    if attr and val:
        pat = r'<' + tag + r'[^>]*\b' + attr + r'\s*=\s*["\']' + re.escape(val) + r'["\'][^>]*>'
        m = re.search(pat, html, re.I)
        if not m:
            return None
        fragment = m.group(0)
        cm = re.search(r'content\s*=\s*["\']([^"\']*)["\']', fragment, re.I)
        return cm.group(1) if cm else None
    pat = r'<' + tag + r'[^>]*>(.*?)</' + tag + r'>'
    m = re.search(pat, html, re.I | re.S)
    return m.group(1).strip() if m else None

def extract_link(html, rel):
    pat = r'<link[^>]*\brel\s*=\s*["\']' + re.escape(rel) + r'["\'][^>]*>'
    m = re.search(pat, html, re.I)
    if not m:
        return None
    fragment = m.group(0)
    hm = re.search(r'href\s*=\s*["\']([^"\']*)["\']', fragment, re.I)
    return hm.group(1) if hm else None

def extract_html_lang(html):
    m = re.search(r'<html[^>]*\blang\s*=\s*["\']([^"\']*)["\']', html, re.I)
    return m.group(1) if m else None

def extract_viewport(html):
    return bool(re.search(r'<meta[^>]*\bname\s*=\s*["\']viewport["\']', html, re.I))

def count_h1(html):
    return len(re.findall(r'<h1\b[^>]*>', html, re.I))

def count_hreflang(html):
    return len(re.findall(r'<link[^>]*\bhreflang\s*=', html, re.I))

def count_img_missing_alt(html):
    imgs = re.findall(r'<img\b[^>]*>', html, re.I)
    missing = 0
    for img in imgs:
        if not re.search(r'\balt\s*=', img, re.I):
            missing += 1
    return missing, len(imgs)

def extract_internal_links(html):
    hrefs = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', html, re.I)
    internal = []
    for h in hrefs:
        if h.startswith("#") or h.startswith("mailto:") or h.startswith("tel:") or h.startswith("javascript:"):
            continue
        if h.startswith("http://") or h.startswith("https://") or h.startswith("//"):
            continue
        # anchor/query 제거 후 빈 문자열이면 스킵
        bare = h.split("#")[0].split("?")[0]
        if not bare:
            continue
        # 루트 경로 "/" 만 있으면 index.html 로 리졸브
        if bare == "/":
            continue
        internal.append(h)
    return internal

def resolve_link(src_file, href):
    """Resolve a relative href to an absolute path."""
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    try:
        if href.startswith("/"):
            resolved = (ROOT / href.lstrip("/")).resolve()
        else:
            resolved = (src_file.parent / href).resolve()
        return resolved
    except Exception:
        return None

def audit():
    files = find_html_files()
    all_files_set = set(f.resolve() for f in files)
    records = []
    title_map = defaultdict(list)
    desc_map = defaultdict(list)

    for f in files:
        html = read_file(f)
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        rec = {
            "file": rel,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "title": extract_tag(html, "title"),
            "desc": extract_tag(html, "meta", "name", "description"),
            "canonical": extract_link(html, "canonical"),
            "viewport": extract_viewport(html),
            "og_title": extract_tag(html, "meta", "property", "og:title"),
            "og_desc": extract_tag(html, "meta", "property", "og:description"),
            "og_image": extract_tag(html, "meta", "property", "og:image"),
            "og_url": extract_tag(html, "meta", "property", "og:url"),
            "h1_count": count_h1(html),
            "html_lang": extract_html_lang(html),
            "hreflang_count": count_hreflang(html),
            "img_total": 0,
            "img_no_alt": 0,
            "broken_links": [],
        }
        no_alt, total_img = count_img_missing_alt(html)
        rec["img_no_alt"] = no_alt
        rec["img_total"] = total_img

        # Broken link check
        for href in extract_internal_links(html):
            resolved = resolve_link(f, href)
            if resolved is None:
                continue
            if resolved.is_dir():
                candidate = resolved / "index.html"
                if not candidate.exists():
                    rec["broken_links"].append(href)
                continue
            # If it's an HTML link, must exist
            if str(resolved).lower().endswith(".html"):
                if not resolved.exists():
                    rec["broken_links"].append(href)
                continue
            # Non-html assets: skip broken check (css/js/img false positives)

        if rec["title"]:
            title_map[rec["title"].strip()].append(rel)
        if rec["desc"]:
            desc_map[rec["desc"].strip()].append(rel)

        records.append(rec)

    # Severity analysis
    for r in records:
        issues = []
        warnings = []

        # 필수 메타
        t = r["title"]
        if not t:
            issues.append(("title 누락", "", "title 추가"))
        else:
            tl = len(t)
            if tl < 15:
                warnings.append(("title 너무 짧음", f"{tl}자: {t}", "15~60자"))
            elif tl > 60:
                warnings.append(("title 너무 김", f"{tl}자", "60자 이내"))

        d = r["desc"]
        if not d:
            issues.append(("meta description 누락", "", "description 추가"))
        else:
            dl = len(d)
            if dl < 70:
                warnings.append(("description 너무 짧음", f"{dl}자", "70~160자"))
            elif dl > 160:
                warnings.append(("description 너무 김", f"{dl}자", "160자 이내"))

        c = r["canonical"]
        if not c:
            issues.append(("canonical 누락", "", "canonical 추가"))
        elif not c.startswith(SITE_URL):
            warnings.append(("canonical URL 잘못됨", c, "https://wocs.kr/... 사용"))

        if not r["viewport"]:
            issues.append(("viewport 누락", "", "viewport meta 추가"))

        # OG
        if not r["og_title"]:
            warnings.append(("og:title 누락", "", "og:title 추가"))
        if not r["og_desc"]:
            warnings.append(("og:description 누락", "", "og:description 추가"))
        if not r["og_image"]:
            warnings.append(("og:image 누락", "", "og:image 추가"))
        if not r["og_url"]:
            warnings.append(("og:url 누락", "", "og:url 추가"))
        elif c and r["og_url"] != c:
            warnings.append(("og:url/canonical 불일치", f"og={r['og_url']}", "canonical과 일치"))

        # 구조
        if r["h1_count"] == 0:
            issues.append(("h1 없음", "0개", "h1 1개 추가"))
        elif r["h1_count"] > 1:
            warnings.append(("h1 중복", f"{r['h1_count']}개", "h1 1개로"))

        if not r["html_lang"]:
            issues.append(("html lang 없음", "", "<html lang='ko'>"))

        # 이미지
        if r["img_no_alt"] > 0:
            warnings.append(("img alt 누락", f"{r['img_no_alt']}/{r['img_total']}개", "모든 img에 alt"))

        # 깨진 링크
        if r["broken_links"]:
            issues.append(("깨진 내부링크", f"{len(r['broken_links'])}개: " + ", ".join(r["broken_links"][:3]), "링크 수정/제거"))

        r["issues"] = issues
        r["warnings"] = warnings

    # 중복 title/desc
    dup_titles = {k: v for k, v in title_map.items() if len(v) > 1}
    dup_descs = {k: v for k, v in desc_map.items() if len(v) > 1}

    # 중복을 문제로 추가
    for r in records:
        t = (r["title"] or "").strip()
        if t and t in dup_titles:
            r["warnings"].append(("title 중복", f"{len(dup_titles[t])}개 파일이 공유", "title 개별화"))
        d = (r["desc"] or "").strip()
        if d and d in dup_descs:
            r["warnings"].append(("description 중복", f"{len(dup_descs[d])}개 파일이 공유", "description 개별화"))

    return records, dup_titles, dup_descs

def render_report(records, dup_titles, dup_descs):
    total = len(records)
    lines = []
    lines.append("# WOCS SEO 감사 보고서")
    lines.append("")
    lines.append("**감사 대상**: `C:/Users/user/OneDrive/Desktop/wocs-site` 전체 HTML 파일")
    lines.append("**총 파일 수**: " + str(total) + "개  ")
    lines.append("**감사일**: 2026-04-11  ")
    lines.append("**레포**: cryptowoosung/wocs-site-  ")
    lines.append("")
    lines.append("> 모든 HTML은 한국어 단일 언어 (다국어 파일 없음). hreflang 검사는 해당 없음.")
    lines.append("")

    # 1. 요약표
    def count_ok(key_check):
        return sum(1 for r in records if key_check(r))

    items = [
        ("title 존재", lambda r: bool(r["title"])),
        ("title 길이 적정 (15~60)", lambda r: r["title"] and 15 <= len(r["title"]) <= 60),
        ("meta description 존재", lambda r: bool(r["desc"])),
        ("description 길이 적정 (70~160)", lambda r: r["desc"] and 70 <= len(r["desc"]) <= 160),
        ("canonical 존재", lambda r: bool(r["canonical"])),
        ("canonical URL 올바름", lambda r: r["canonical"] and r["canonical"].startswith(SITE_URL)),
        ("viewport 존재", lambda r: r["viewport"]),
        ("og:title 존재", lambda r: bool(r["og_title"])),
        ("og:description 존재", lambda r: bool(r["og_desc"])),
        ("og:image 존재", lambda r: bool(r["og_image"])),
        ("og:url 존재", lambda r: bool(r["og_url"])),
        ("h1 정확히 1개", lambda r: r["h1_count"] == 1),
        ("html lang 속성 존재", lambda r: bool(r["html_lang"])),
        ("img alt 누락 없음", lambda r: r["img_no_alt"] == 0),
        ("깨진 내부링크 없음", lambda r: len(r["broken_links"]) == 0),
    ]

    lines.append("## 1. 요약표")
    lines.append("")
    lines.append("| 검사 항목 | 정상 | 문제 | 비율 |")
    lines.append("|---|---|---|---|")
    for name, check in items:
        ok = count_ok(check)
        bad = total - ok
        pct = round(ok / total * 100, 1) if total else 0
        lines.append("| " + name + " | " + str(ok) + " | " + str(bad) + " | " + str(pct) + "% |")
    lines.append("")

    # 심각도 집계
    red_files = [r for r in records if r["issues"]]
    yellow_files = [r for r in records if not r["issues"] and r["warnings"]]
    green_files = [r for r in records if not r["issues"] and not r["warnings"]]
    lines.append("**심각도 분포**: 🔴 심각 " + str(len(red_files)) + "개 · 🟡 개선필요 " + str(len(yellow_files)) + "개 · 🟢 정상 " + str(len(green_files)) + "개")
    lines.append("")

    # 2. 문제 파일 상세
    lines.append("## 2. 문제 파일 상세")
    lines.append("")
    lines.append("| 파일 | 심각도 | 문제 항목 | 현재값 | 권장 조치 |")
    lines.append("|---|---|---|---|---|")
    def esc(s):
        return str(s).replace("|", "\\|").replace("\n", " ")[:120]
    for r in records:
        sev = "🔴" if r["issues"] else ("🟡" if r["warnings"] else None)
        if not sev:
            continue
        all_items = [("🔴", it) for it in r["issues"]] + [("🟡", it) for it in r["warnings"]]
        for badge, (issue, cur, fix) in all_items:
            lines.append("| " + esc(r["file"]) + " | " + badge + " | " + esc(issue) + " | " + esc(cur) + " | " + esc(fix) + " |")
    lines.append("")

    # 3. 중복 title/description 그룹
    lines.append("## 3. 중복 title/description 그룹")
    lines.append("")
    if dup_titles:
        lines.append("### title 중복")
        lines.append("")
        for title, fs in dup_titles.items():
            lines.append("**\"" + esc(title) + "\"** (" + str(len(fs)) + "개)")
            for fn in fs:
                lines.append("- `" + fn + "`")
            lines.append("")
    else:
        lines.append("### title 중복")
        lines.append("")
        lines.append("_중복 없음_")
        lines.append("")
    if dup_descs:
        lines.append("### description 중복")
        lines.append("")
        for d, fs in dup_descs.items():
            lines.append("**\"" + esc(d) + "\"** (" + str(len(fs)) + "개)")
            for fn in fs:
                lines.append("- `" + fn + "`")
            lines.append("")
    else:
        lines.append("### description 중복")
        lines.append("")
        lines.append("_중복 없음_")
        lines.append("")

    # 4. 파일별 메타 원본 (참고)
    lines.append("## 4. 전체 파일 메타 원본 (참고)")
    lines.append("")
    lines.append("| 파일 | KB | title 길이 | desc 길이 | canonical | h1 | img alt 누락 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in records:
        t_len = len(r["title"]) if r["title"] else 0
        d_len = len(r["desc"]) if r["desc"] else 0
        canon = "✅" if r["canonical"] and r["canonical"].startswith(SITE_URL) else ("⚠️" if r["canonical"] else "❌")
        lines.append("| " + r["file"] + " | " + str(r["size_kb"]) + " | " + str(t_len) + " | " + str(d_len) + " | " + canon + " | " + str(r["h1_count"]) + " | " + str(r["img_no_alt"]) + "/" + str(r["img_total"]) + " |")

    return "\n".join(lines)

if __name__ == "__main__":
    records, dup_titles, dup_descs = audit()
    report = render_report(records, dup_titles, dup_descs)
    out_path = ROOT / "seo_audit_report.md"
    out_path.write_text(report, encoding="utf-8")
    print("OK")
    print("Total files:", len(records))
    print("Red:", sum(1 for r in records if r["issues"]))
    print("Yellow:", sum(1 for r in records if not r["issues"] and r["warnings"]))
    print("Green:", sum(1 for r in records if not r["issues"] and not r["warnings"]))
    print("Report:", out_path)
