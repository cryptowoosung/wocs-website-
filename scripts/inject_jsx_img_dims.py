"""
Inject width/height into dynamic <img> tags in src/App.jsx.

Two passes:
  1. For every `img: "assets/images/xxx.webp"` object literal field, append
     `, w: <W>, h: <H>` using scripts/image_dimensions.json.
  2. For every `<img ... src={<var>.img} ...>` JSX, add `width={<var>.w} height={<var>.h}`.

Also handles:
  - conditional ternary src: `src={a ? "assets/..." : b ? "assets/..." : ...}` — skipped
    for safety (multiple possible sizes); the caller can handle these manually.
  - External URLs (https://...) — untouched.

Idempotent: tags that already have `width=` are skipped.
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
stats = {'data_fields': 0, 'jsx_imgs': 0}


def dims_for_path(p):
    decoded = p.replace('%20', ' ')
    fname = os.path.basename(decoded.split('?')[0].split('#')[0])
    return DIMS.get(fname)


# Pass 1: `img: "..."` → `img: "...", w: W, h: H`
# Skip if already followed by `, w:` (idempotent).
def pass1_sub(m):
    full = m.group(0)
    img_val = m.group(1)
    tail = content_view[m.end():m.end() + 80]
    if re.match(r'\s*,\s*w\s*:', tail):
        return full
    d = dims_for_path(img_val)
    if not d or 'w' not in d:
        return full
    stats['data_fields'] += 1
    return f'{full}, w: {d["w"]}, h: {d["h"]}'


IMG_FIELD_RE = re.compile(r'''img\s*:\s*"([^"]+\.(?:webp|jpg|jpeg|png))"''')
content_view = content
content = IMG_FIELD_RE.sub(pass1_sub, content)


# Pass 2: `<img ... src={<expr>.img} ...>` JSX
def pass2_sub(m):
    tag = m.group(0)
    if re.search(r'\swidth\s*=', tag):
        return tag
    src_m = re.search(r'src=\{([^}]+)\.img\}', tag)
    if not src_m:
        return tag
    var_expr = src_m.group(1).strip()
    stats['jsx_imgs'] += 1
    # Insert width/height right after the opening <img
    return tag.replace(
        '<img', f'<img width={{{var_expr}.w}} height={{{var_expr}.h}}', 1
    )


JSX_IMG_RE = re.compile(r'<img\s[^>]*src=\{[^}]+\.img\}[^>]*?/?>', re.DOTALL)
content = JSX_IMG_RE.sub(pass2_sub, content)


if content == original:
    print('no changes')
else:
    with open(APP, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f'Pass 1: {stats["data_fields"]} object-literal img fields augmented with w/h')
    print(f'Pass 2: {stats["jsx_imgs"]} dynamic <img> JSX tags got width/height')
