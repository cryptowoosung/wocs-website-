"""
Walk every HTML file (excluding build/backup dirs) and verify every internal
.html href resolves to a real file on disk.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SKIP = {'node_modules', 'dist', '.git', '_original-backup', 'venv', 'OneDrive', 'public', '.bkit', '.omc'}

# href="<path>.html" or href="<path>.html#anchor" or ?query — only local paths
HREF_RE = re.compile(
    r'''href=["'](?!https?://|#|mailto:|tel:|//)([^"'#?]+\.html)(?:[#?][^"']*)?["']''',
    re.IGNORECASE,
)

broken = []
checked = 0

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except Exception:
            continue
        for link in HREF_RE.findall(content):
            checked += 1
            if link.startswith('/'):
                target = os.path.normpath(os.path.join(ROOT, link.lstrip('/')))
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(fp), link))
            if not os.path.exists(target):
                broken.append((os.path.relpath(fp, ROOT), link, os.path.relpath(target, ROOT)))

print(f'internal .html links checked: {checked}')
print(f'broken (file missing):       {len(broken)}')
for src, link, tgt in broken[:20]:
    print(f'  {src} -> {link}')
    print(f'    resolved: {tgt}')
