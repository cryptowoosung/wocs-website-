"""
Scan every product HTML file that has an OPTIONAL FURNITURE section and
extract the (image src, label) pairs. Reports any file where the same
image is used for different labels (content bug: duplicate image, distinct
label).
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PRODUCTS = os.path.join(ROOT, 'products')

FURN_CARD = re.compile(
    r'<div\s+class="furn-card[^"]*"[^>]*>\s*'
    r'<img[^>]*?src="([^"]+)"[^>]*?>\s*'
    r'<div\s+class="furn-label"[^>]*?>([^<]+)<',
    re.IGNORECASE | re.DOTALL,
)


def short_url(u):
    # Extract Unsplash photo id for readability
    m = re.search(r'photo-([a-f0-9\-]+)', u)
    if m:
        return f'unsplash:{m.group(1)[:12]}'
    return u.split('?')[0].rsplit('/', 1)[-1]


for fname in sorted(os.listdir(PRODUCTS)):
    if not fname.endswith('.html'):
        continue
    fp = os.path.join(PRODUCTS, fname)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'OPTIONAL FURNITURE' not in content and '선택 가능한' not in content:
        continue
    pairs = []
    for m in FURN_CARD.finditer(content):
        url = m.group(1)
        label = m.group(2).strip()
        pairs.append((short_url(url), label))
    if not pairs:
        continue
    # Check for duplicate image with different labels
    by_url = {}
    for u, l in pairs:
        by_url.setdefault(u, []).append(l)
    dups = {u: ls for u, ls in by_url.items() if len(ls) > 1}
    if dups:
        print(f'\n{fname}:')
        for u, labels in dups.items():
            print(f'  DUP  {u}  -> {labels}')
