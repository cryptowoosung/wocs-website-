"""
Inject `width` and `height` attributes into every <img> tag whose src
resolves to a file listed in scripts/image_dimensions.json.

Idempotent: a tag that already has both width and height is skipped.
HTML comments are protected from modification.
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, 'scripts', 'image_dimensions.json'), 'r', encoding='utf-8') as f:
    DIMS = json.load(f)


def dims_for_src(src):
    decoded = src.replace('%20', ' ')
    fname = os.path.basename(decoded.split('?')[0].split('#')[0])
    return DIMS.get(fname)


IMG_TAG_RE = re.compile(r'<img\s[^>]*?>', re.IGNORECASE)
SRC_RE = re.compile(r'''src\s*=\s*['"]([^'"]+)['"]''', re.IGNORECASE)
HAS_W = re.compile(r'\swidth\s*=', re.IGNORECASE)
HAS_H = re.compile(r'\sheight\s*=', re.IGNORECASE)
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


def process(content):
    comments = []

    def stash(m):
        comments.append(m.group(0))
        return f'___COMMENT_{len(comments) - 1}___'

    protected = COMMENT_RE.sub(stash, content)

    counter = {'mod': 0}

    def repl(m):
        tag = m.group(0)
        if HAS_W.search(tag) and HAS_H.search(tag):
            return tag
        src_m = SRC_RE.search(tag)
        if not src_m:
            return tag
        d = dims_for_src(src_m.group(1))
        if not d or 'w' not in d:
            return tag
        insert = f' width="{d["w"]}" height="{d["h"]}"'
        new_tag = tag[:4] + insert + tag[4:]
        counter['mod'] += 1
        return new_tag

    protected = IMG_TAG_RE.sub(repl, protected)
    for i, c in enumerate(comments):
        protected = protected.replace(f'___COMMENT_{i}___', c, 1)
    return protected, counter['mod']


SKIP_DIR_NAMES = {'node_modules', 'dist', '.git', 'backup', 'public', 'OneDrive', '.bkit', '.omc'}
TARGET_EXTS = ('.html', '.jsx')

total_files = 0
total_modified = 0
changed = []

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
    for f in files:
        if not f.endswith(TARGET_EXTS):
            continue
        fp = os.path.join(root, f)
        # also skip any path inside a public/ junction at any depth
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
            total_modified += n
            changed.append((os.path.relpath(fp, ROOT), n))
            with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(new_content)

print(f'files changed: {total_files}')
print(f'imgs injected: {total_modified}')
print('top files:')
for rel, n in sorted(changed, key=lambda x: -x[1])[:15]:
    print(f'  {n:4d}  {rel}')
