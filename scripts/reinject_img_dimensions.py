"""
Overwrite `width` and `height` attributes on every <img> whose src
resolves to a known local image (per scripts/image_dimensions.json).

Difference from inject_img_dimensions.py:
  - inject_*   : skips tags that already have width+height (idempotent add)
  - reinject_* : replaces any existing numeric width/height with the
                 current file's actual dimensions (needed after resize)

HTML comments are protected. JSX-style attributes like width={slide.w}
are left untouched (non-numeric value).
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, 'scripts', 'image_dimensions.json'), 'r', encoding='utf-8') as f:
    DIMS = json.load(f)

SRC_RE = re.compile(r'''src\s*=\s*['"]([^'"]+)['"]''', re.IGNORECASE)
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
IMG_TAG_RE = re.compile(r'<img\s[^>]*?>', re.IGNORECASE)
# Only match numeric width/height in quotes - preserves JSX {var.w} forms
W_ATTR_RE = re.compile(r'''\s+width\s*=\s*["']\d+["']''', re.IGNORECASE)
H_ATTR_RE = re.compile(r'''\s+height\s*=\s*["']\d+["']''', re.IGNORECASE)


def dims_for_src(src):
    decoded = src.replace('%20', ' ')
    fname = os.path.basename(decoded.split('?')[0].split('#')[0])
    return DIMS.get(fname)


def process(content):
    comments = []

    def stash(m):
        comments.append(m.group(0))
        return f'___COMMENT_{len(comments) - 1}___'

    protected = COMMENT_RE.sub(stash, content)

    counter = {'changed': 0}

    def repl(m):
        tag = m.group(0)
        src_m = SRC_RE.search(tag)
        if not src_m:
            return tag
        d = dims_for_src(src_m.group(1))
        if not d or 'w' not in d:
            return tag
        new_tag = W_ATTR_RE.sub('', tag)
        new_tag = H_ATTR_RE.sub('', new_tag)
        insert = f' width="{d["w"]}" height="{d["h"]}"'
        new_tag = new_tag[:4] + insert + new_tag[4:]
        if new_tag != tag:
            counter['changed'] += 1
        return new_tag

    protected = IMG_TAG_RE.sub(repl, protected)
    for i, c in enumerate(comments):
        protected = protected.replace(f'___COMMENT_{i}___', c, 1)
    return protected, counter['changed']


SKIP_DIR_NAMES = {'node_modules', 'dist', '.git', 'backup', '_original-backup', 'public', 'OneDrive', '.bkit', '.omc'}
TARGET_EXTS = ('.html', '.jsx')

total_files = 0
total_changed = 0

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
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
        new_content, n = process(content)
        if n > 0:
            total_files += 1
            total_changed += n
            with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(new_content)

print(f'files updated: {total_files}')
print(f'imgs updated:  {total_changed}')
