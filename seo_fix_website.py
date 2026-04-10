"""Apply SEO fixes to wocs-website- for the 58 paths that exist in wocs-site-.

Rules:
- Only modify files whose relative path is in DESCRIPTIONS (58 common files).
- Add missing meta description (from DESCRIPTIONS).
- Add missing og:description (same as description).
- Add missing og:url (from canonical).
- Replace title if too short/long (from TITLE_OVERRIDES).
- index.html: fix h1 duplicates, add og:image if missing.
- Never touch files outside the 58 common paths (including nested OneDrive/Desktop/wocs-site/).
- Never modify body/CSS/JS — only <head> meta.
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
BACKUP_PATH = ROOT / "seo_backup.json"

# Load DESCRIPTIONS and TITLE_OVERRIDES from seo_fix.py
spec = importlib.util.spec_from_file_location("seo_fix", str(ROOT / "seo_fix.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DESCRIPTIONS = mod.DESCRIPTIONS
TITLE_OVERRIDES = dict(mod.TITLE_OVERRIDES)

# Additional overrides for wocs-website- only (titles that were short in this repo)
TITLE_OVERRIDES.update({
    "gallery/index.html": "WOCS 글램핑 시공 갤러리 — 실제 현장 사진",
    "occasions/index.html": "WOCS 활용 분야 — 글램핑·리조트·호텔 시공",
    "products/geodesic-domes.html": "WOCS D-시리즈 측지 돔 제품 라인업",
    "products/safari-basic.html": "WOCS S-Classic 사파리 텐트 — 베이직 라인",
})

# ──────────────────────────────────────────────────────────
# File I/O
# ──────────────────────────────────────────────────────────

def read(p):
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p, text):
    p.write_text(text, encoding="utf-8", newline="\n")

# ──────────────────────────────────────────────────────────
# Meta extraction
# ──────────────────────────────────────────────────────────

def get_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return m.group(1).strip() if m else None

def get_meta(html, key, value):
    pat = (
        r'<meta[^>]*\b' + key + r'\s*=\s*["\']' + re.escape(value) +
        r'["\'][^>]*\bcontent\s*=\s*["\']([^"\']*)["\'][^>]*>'
    )
    m = re.search(pat, html, re.I)
    if m:
        return m.group(1)
    pat2 = (
        r'<meta[^>]*\bcontent\s*=\s*["\']([^"\']*)["\'][^>]*\b' + key +
        r'\s*=\s*["\']' + re.escape(value) + r'["\'][^>]*>'
    )
    m = re.search(pat2, html, re.I)
    return m.group(1) if m else None

def get_canonical(html):
    m = re.search(
        r'<link[^>]*\brel\s*=\s*["\']canonical["\'][^>]*\bhref\s*=\s*["\']([^"\']*)["\']',
        html, re.I,
    )
    if m:
        return m.group(1)
    m = re.search(
        r'<link[^>]*\bhref\s*=\s*["\']([^"\']*)["\'][^>]*\brel\s*=\s*["\']canonical["\']',
        html, re.I,
    )
    return m.group(1) if m else None

def extract_head(html):
    m = re.search(r"<head[^>]*>(.*?)</head>", html, re.I | re.S)
    return m.group(0) if m else ""

# ──────────────────────────────────────────────────────────
# HTML patching
# ──────────────────────────────────────────────────────────

def insert_after_title(html, snippet):
    return re.sub(
        r'(</title>)',
        r'\1\n  ' + snippet.replace('\\', '\\\\'),
        html,
        count=1,
        flags=re.I,
    )

def insert_into_head_end(html, snippet):
    return re.sub(
        r'(</head>)',
        r'  ' + snippet.replace('\\', '\\\\') + r'\n\1',
        html,
        count=1,
        flags=re.I,
    )

def replace_title_text(html, new_title):
    return re.sub(
        r'<title[^>]*>.*?</title>',
        '<title>' + new_title + '</title>',
        html,
        count=1,
        flags=re.I | re.S,
    )

# ──────────────────────────────────────────────────────────
# Backup
# ──────────────────────────────────────────────────────────

def build_backup(target_files):
    data = {}
    for f in target_files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        html = read(f)
        data[rel] = {
            "head": extract_head(html),
            "title": get_title(html),
            "description": get_meta(html, "name", "description"),
            "canonical": get_canonical(html),
            "og:description": get_meta(html, "property", "og:description"),
            "og:url": get_meta(html, "property", "og:url"),
            "og:image": get_meta(html, "property", "og:image"),
        }
    BACKUP_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

# ──────────────────────────────────────────────────────────
# Fix engine
# ──────────────────────────────────────────────────────────

def fix_file(f, rel, log):
    html = read(f)
    mod = html

    current_title = get_title(mod)
    current_desc = get_meta(mod, "name", "description")
    current_og_desc = get_meta(mod, "property", "og:description")
    current_og_url = get_meta(mod, "property", "og:url")
    current_og_image = get_meta(mod, "property", "og:image")
    canonical = get_canonical(mod)

    # Title length fix (only if rel in TITLE_OVERRIDES AND current title out of range)
    if current_title:
        tl = len(current_title)
        if (tl < 15 or tl > 60) and rel in TITLE_OVERRIDES:
            new_title = TITLE_OVERRIDES[rel]
            mod = replace_title_text(mod, new_title)
            log.append(("title", current_title, new_title))

    # Description fix (only if missing AND rel in DESCRIPTIONS)
    description = DESCRIPTIONS.get(rel)
    if not current_desc and description:
        if len(description) < 70 or len(description) > 160:
            raise ValueError("description length OOR for " + rel)
        snippet = '<meta name="description" content="' + description + '">'
        mod = insert_after_title(mod, snippet)
        log.append(("meta description", "(none)", description))

    # og:description fix (only if missing AND we have a description)
    if not current_og_desc and description:
        snippet = '<meta property="og:description" content="' + description + '">'
        mod = insert_into_head_end(mod, snippet)
        log.append(("og:description", "(none)", description))

    # og:url fix (only if missing AND canonical exists)
    if not current_og_url and canonical:
        snippet = '<meta property="og:url" content="' + canonical + '">'
        mod = insert_into_head_end(mod, snippet)
        log.append(("og:url", "(none)", canonical))

    # index.html specific: og:image + h1 duplicates
    if rel == "index.html":
        if not current_og_image:
            snippet = '<meta property="og:image" content="https://wocs.kr/assets/images/og-default.jpg">'
            mod = insert_into_head_end(mod, snippet)
            log.append(("og:image", "(none)", "https://wocs.kr/assets/images/og-default.jpg"))
        # h1 duplicates → keep first, convert rest to h2
        h1_opens = list(re.finditer(r'<h1\b([^>]*)>', mod, re.I))
        if len(h1_opens) > 1:
            for i in range(len(h1_opens) - 1, 0, -1):
                start = h1_opens[i].start()
                end = h1_opens[i].end()
                new_open = re.sub(r'<h1\b', '<h2', h1_opens[i].group(0), flags=re.I)
                mod = mod[:start] + new_open + mod[end:]
            h1_closes = list(re.finditer(r'</h1>', mod, re.I))
            if len(h1_closes) > 1:
                for i in range(len(h1_closes) - 1, 0, -1):
                    start = h1_closes[i].start()
                    end = h1_closes[i].end()
                    mod = mod[:start] + "</h2>" + mod[end:]
            log.append(("h1 count", str(len(h1_opens)), "1 (others -> h2)"))

    if mod != html:
        write(f, mod)
        return True
    return False

# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def main():
    # Build list of target files — only the 58 paths in DESCRIPTIONS that exist in this repo
    target = []
    missing = []
    for rel in DESCRIPTIONS.keys():
        p = ROOT / rel
        if p.exists() and p.is_file():
            target.append(p)
        else:
            missing.append(rel)

    print("Target files (DESCRIPTIONS keys existing in repo): " + str(len(target)))
    if missing:
        print("Missing (not found in wocs-website-): " + str(len(missing)))
        for m in missing:
            print("  - " + m)

    print("Backing up heads -> seo_backup.json")
    build_backup(target)

    modified = 0
    log_all = {}
    for f in target:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        log = []
        try:
            if fix_file(f, rel, log):
                modified += 1
                log_all[rel] = log
        except Exception as e:
            print("ERROR " + rel + ": " + str(e))

    log_path = ROOT / "seo_fix_log.json"
    log_path.write_text(
        json.dumps(log_all, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Modified: " + str(modified))
    print("Log: " + str(log_path))

if __name__ == "__main__":
    main()
