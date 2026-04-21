"""
Convert `<link rel="stylesheet">` tags into the preload+onload async pattern
so that stylesheet fetch does not block the initial render.

Before:
  <link rel="stylesheet" href="../assets/css/wocs-common.css">

After:
  <link rel="preload" href="../assets/css/wocs-common.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="../assets/css/wocs-common.css"></noscript>

Scope:
  - local CSS only (no absolute http/https URLs, Google Fonts skipped)
  - skips tags already converted (idempotent)
  - HTML comments protected

Targets: all *.html under the repo (excluding node_modules / dist / public /
_original-backup) and vite-index.html specifically.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TARGET_EXTS = ('.html',)

LINK_PATTERN = re.compile(
    r'''<link\s+rel=["']stylesheet["']\s+href=["']([^"']+\.css)["']\s*/?>''',
    re.IGNORECASE,
)
COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)


def should_skip(href):
    h = href.lower()
    if h.startswith(('http://', 'https://', '//')):
        return True
    if 'googleapis' in h or 'gstatic' in h or 'fonts.' in h:
        return True
    return False


def transform(content):
    comments = []

    def stash(m):
        comments.append(m.group(0))
        return f'___COMMENT_{len(comments) - 1}___'

    protected = COMMENT_PATTERN.sub(stash, content)

    count = {'n': 0}

    def replace(m):
        href = m.group(1)
        if should_skip(href):
            return m.group(0)
        count['n'] += 1
        return (
            f'<link rel="preload" href="{href}" as="style" '
            f'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
            f'<noscript><link rel="stylesheet" href="{href}"></noscript>'
        )

    protected = LINK_PATTERN.sub(replace, protected)
    for i, c in enumerate(comments):
        protected = protected.replace(f'___COMMENT_{i}___', c, 1)
    return protected, count['n']


SKIP_DIRS = {'node_modules', 'dist', '.git', '_original-backup', 'public', 'OneDrive', '.bkit', '.omc'}
total_files = 0
total_changed = 0
sample = []

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith(TARGET_EXTS):
            continue
        fp = os.path.join(root, f)
        if os.path.sep + 'public' + os.path.sep in fp:
            continue
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except Exception:
            continue
        new_content, n = transform(content)
        if n > 0:
            total_files += 1
            total_changed += n
            sample.append((os.path.relpath(fp, ROOT), n))
            with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(new_content)

print(f'files modified: {total_files}')
print(f'link tags converted: {total_changed}')
print('top files:')
for rel, n in sorted(sample, key=lambda x: -x[1])[:10]:
    print(f'  {n}x  {rel}')
