"""List HTML files missing meta description and/or og:title."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SKIP = {'node_modules', 'dist', '.git', '_original-backup', 'venv', 'OneDrive', 'public', '.bkit', '.omc'}

missing_desc = []
missing_og = []

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith('.html') or f == 'vite-index.html':
            continue
        fp = os.path.join(root, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                head = fh.read(8000)
        except Exception:
            continue
        rel = os.path.relpath(fp, ROOT).replace(os.sep, '/')
        if 'name="description"' not in head:
            missing_desc.append(rel)
        if 'property="og:title"' not in head:
            missing_og.append(rel)

print(f'missing description: {len(missing_desc)}')
for x in missing_desc[:20]:
    print(f'  - {x}')
if len(missing_desc) > 20:
    print(f'  ... +{len(missing_desc)-20}')

print()
print(f'missing og:title: {len(missing_og)}')
for x in missing_og[:20]:
    print(f'  - {x}')
if len(missing_og) > 20:
    print(f'  ... +{len(missing_og)-20}')

print()
print(f'both missing: {len(set(missing_desc) & set(missing_og))}')
