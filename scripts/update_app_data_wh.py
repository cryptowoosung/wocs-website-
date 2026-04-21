"""
Update existing `, w: N, h: N` fields inside object literals in src/App.jsx
to match the latest image_dimensions.json values.

Handles only the pattern:
  img: "assets/images/<file>", w: <num>, h: <num>

Object literals that don't yet have w/h are left alone (they were handled
by inject_jsx_img_dims.py previously).
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'src', 'App.jsx')
with open(os.path.join(ROOT, 'scripts', 'image_dimensions.json'), 'r', encoding='utf-8') as f:
    DIMS = json.load(f)

with open(APP, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

PATTERN = re.compile(
    r'(img\s*:\s*)"([^"]+\.(?:webp|jpg|jpeg|png))"\s*,\s*w\s*:\s*\d+\s*,\s*h\s*:\s*\d+'
)


def update(m):
    prefix = m.group(1)
    path = m.group(2)
    fname = os.path.basename(path.replace('%20', ' ').split('?')[0])
    d = DIMS.get(fname)
    if not d or 'w' not in d:
        return m.group(0)
    return f'{prefix}"{path}", w: {d["w"]}, h: {d["h"]}'


content = PATTERN.sub(update, content)

if content == original:
    print('no changes')
else:
    with open(APP, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    changed = sum(
        1 for line in content.split('\n') if re.search(r'img\s*:\s*"[^"]+", w:', line)
    )
    print(f'App.jsx data fields with w/h (post-update): {changed}')
