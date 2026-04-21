"""
Count how many times each image under assets/images/ is referenced across
HTML/JSX/JS/CSS files. Useful to see top-used assets for LCP prioritization.
"""
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

counter = Counter()
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('node_modules', 'dist', '.git', 'scripts', 'backup', 'public')]
    for f in files:
        if not f.endswith(('.html', '.jsx', '.js', '.css')):
            continue
        fp = os.path.join(root, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except Exception:
            continue
        for m in re.finditer(r'(?:/?assets/images/)([^"\'\s)]+\.(?:webp|jpg|jpeg|png))', content):
            name = m.group(1).replace('%20', ' ')
            counter[name] += 1

for name, n in counter.most_common(20):
    print(f'  {n:3d}  {name}')
print(f'\n  unique referenced images: {len(counter)}')
