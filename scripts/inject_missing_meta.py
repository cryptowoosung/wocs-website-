"""Backfill meta description / OpenGraph / Twitter Card on HTML pages that
lack them. Idempotent: re-runs are no-ops.

Scope: all HTML files under repo root, excluding vendor and junction dirs,
and excluding vite-index.html (Vite entry source — never served directly).

Description source:
  - First meaningful <p>/<h1>/<h2> inside <main> / <article> / <section>
  - Fallback: "<title> | WOCS 글램핑 시공 전문"
  - Cleaned (tags stripped, whitespace collapsed, HTML entities unescaped)
  - Truncated near word boundary, 155 chars target.

OG type:
  - 'article' for /content/* (blog posts)
  - 'website' otherwise
"""
import os
import re
import html as html_lib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE_URL = "https://wocs.kr"
DEFAULT_OG_IMAGE = "/assets/images/og-default.jpg"
SITE_TAGLINE = "WOCS 글램핑 시공 전문"
SKIP_DIRS = {'node_modules', 'dist', '.git', '_original-backup', 'venv', 'OneDrive', 'public', '.bkit', '.omc'}


def clean_text(s):
    s = re.sub(r'<script\b.*?</script>', ' ', s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r'<style\b.*?</style>', ' ', s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html_lib.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def truncate(s, max_len=155):
    if len(s) <= max_len:
        return s
    cut = s[:max_len]
    last_space = cut.rfind(' ')
    if last_space > 100:
        cut = cut[:last_space]
    return cut.rstrip('.,;:…') + '…'


def extract_description(content, fallback_title):
    body_m = re.search(r'<body\b[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    region = body_m.group(1) if body_m else content
    for container in (r'<main\b[^>]*>(.*?)</main>', r'<article\b[^>]*>(.*?)</article>',
                      r'<section\b[^>]*>(.*?)</section>'):
        cm = re.search(container, region, re.DOTALL | re.IGNORECASE)
        if not cm:
            continue
        inner = cm.group(1)
        for tag in (r'<p\b[^>]*>(.*?)</p>', r'<h1\b[^>]*>(.*?)</h1>',
                    r'<h2\b[^>]*>(.*?)</h2>', r'<h3\b[^>]*>(.*?)</h3>'):
            tm = re.search(tag, inner, re.DOTALL | re.IGNORECASE)
            if not tm:
                continue
            text = clean_text(tm.group(1))
            if len(text) >= 30:
                return truncate(text)
    return truncate(f"{fallback_title} | {SITE_TAGLINE}")


def get_title(content):
    m = re.search(r'<title\b[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    return m.group(1).strip() if m else SITE_TAGLINE


def page_url(rel_path):
    rel = rel_path.replace(os.sep, '/')
    if rel == 'index.html':
        return SITE_URL + '/'
    if rel.endswith('/index.html'):
        return SITE_URL + '/' + rel[:-len('index.html')]
    return SITE_URL + '/' + rel


def og_type(rel_path):
    rel = rel_path.replace(os.sep, '/')
    if rel.startswith('content/') or '/content/' in rel:
        return 'article'
    return 'website'


def escape_attr(s):
    return s.replace('"', '&quot;')


def build_missing_block(title, desc, url, type_, needs_desc, needs_og):
    t = escape_attr(title)
    d = escape_attr(desc)
    lines = ['<!-- SEO-META-AUTO -->']
    if needs_desc:
        lines.append(f'<meta name="description" content="{d}">')
    if needs_og:
        lines.extend([
            f'<meta property="og:type" content="{type_}">',
            f'<meta property="og:title" content="{t}">',
            f'<meta property="og:description" content="{d}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{SITE_URL}{DEFAULT_OG_IMAGE}">',
            f'<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{t}">',
            f'<meta name="twitter:description" content="{d}">',
            f'<meta name="twitter:image" content="{SITE_URL}{DEFAULT_OG_IMAGE}">',
        ])
    lines.append('<!-- /SEO-META-AUTO -->')
    return '\n'.join(lines) + '\n'


def process(fp):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False, 'read error'
    if 'SEO-META-AUTO' in content:
        return False, 'already has marker'
    needs_desc = 'name="description"' not in content
    needs_og = 'property="og:title"' not in content
    if not needs_desc and not needs_og:
        return False, 'already complete'
    if '</head>' not in content:
        return False, 'no </head>'
    title = get_title(content)
    rel = os.path.relpath(fp, ROOT)
    desc = extract_description(content, title)
    url = page_url(rel)
    type_ = og_type(rel)
    block = build_missing_block(title, desc, url, type_, needs_desc, needs_og)
    new_content = content.replace('</head>', block + '</head>', 1)
    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    return True, f'desc={needs_desc}, og={needs_og}'


def main():
    stats = {'processed': 0, 'skipped': 0}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith('.html') or f == 'vite-index.html':
                continue
            fp = os.path.join(root, f)
            changed, reason = process(fp)
            if changed:
                stats['processed'] += 1
                rel = os.path.relpath(fp, ROOT).replace(os.sep, '/')
                print(f'  + {rel}: {reason}')
            else:
                stats['skipped'] += 1
    print()
    print(f'processed: {stats["processed"]}')
    print(f'skipped:   {stats["skipped"]}')


if __name__ == '__main__':
    main()
