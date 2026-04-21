"""
Scan all web images in assets/images/ and record (width, height, bytes)
into scripts/image_dimensions.json. Keyed by filename (basename only).
"""
import os
import json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, 'assets', 'images')
OUT = os.path.join(ROOT, 'scripts', 'image_dimensions.json')

out = {}
for fname in sorted(os.listdir(IMG_DIR)):
    if not fname.lower().endswith(('.webp', '.jpg', '.jpeg', '.png')):
        continue
    path = os.path.join(IMG_DIR, fname)
    try:
        with Image.open(path) as im:
            w, h = im.size
        size = os.path.getsize(path)
        out[fname] = {'w': w, 'h': h, 'bytes': size}
    except Exception as e:
        out[fname] = {'error': str(e)}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

total = len(out)
over_1500 = sum(1 for v in out.values() if 'w' in v and v['w'] > 1500)
over_500kb = sum(1 for v in out.values() if 'bytes' in v and v['bytes'] > 500_000)
over_200kb = sum(1 for v in out.values() if 'bytes' in v and v['bytes'] > 200_000)
total_bytes = sum(v.get('bytes', 0) for v in out.values())

print(f'scanned: {total} images')
print(f'width > 1500px: {over_1500} (resize candidates)')
print(f'bytes > 500KB:  {over_500kb} (compress candidates)')
print(f'bytes > 200KB:  {over_200kb}')
print(f'total size:     {total_bytes/1024/1024:.1f} MB')
print(f'metadata saved: {os.path.relpath(OUT, ROOT)}')
