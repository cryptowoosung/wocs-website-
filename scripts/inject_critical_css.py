"""
Inject a small Critical CSS block into vite-index.html (and optionally other
entry HTML files) immediately after the opening <head>.

The inlined rules cover the above-the-fold baseline — background, color, font
stack, and reset basics — so the first paint matches the site theme even
before the async-loaded wocs-common.css finishes.

Idempotent: re-running is a no-op once the marker CRITICAL-CSS-INLINE-V1
is present in the file.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MARKER = 'CRITICAL-CSS-INLINE-V1'
CRITICAL_BLOCK = f"""<style>/* {MARKER} - above-the-fold baseline */
html {{ background:#09090b; color:#f0ebe0; }}
body {{ background:#09090b; color:#f0ebe0; margin:0;
       font-family:'Noto Sans KR','Pretendard',-apple-system,sans-serif;
       -webkit-font-smoothing:antialiased; }}
a {{ color:inherit; text-decoration:none; }}
img {{ max-width:100%; height:auto; display:block; }}
</style>
"""

TARGETS = [os.path.join(ROOT, 'vite-index.html')]

for fp in TARGETS:
    if not os.path.isfile(fp):
        print(f'skip (not found): {os.path.relpath(fp, ROOT)}')
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    if MARKER in content:
        print(f'skip (already injected): {os.path.relpath(fp, ROOT)}')
        continue
    new_content, n = re.subn(
        r'(<head[^>]*>)', r'\1\n' + CRITICAL_BLOCK, content, count=1
    )
    if n == 0:
        print(f'skip (no <head>): {os.path.relpath(fp, ROOT)}')
        continue
    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    print(f'injected: {os.path.relpath(fp, ROOT)}')
