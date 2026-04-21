"""
Phase 2D patches for vite-index.html:
  1. Convert relative assets/* paths to /assets/* (absolute)
  2. Append wocs-lead-popup.js and wocs-header.js before </body>
Idempotent: safe to re-run.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'vite-index.html')

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 1. Relative → absolute for assets/ in src= and href=
content = re.sub(r'src="assets/', 'src="/assets/', content)
content = re.sub(r"src='assets/", "src='/assets/", content)
content = re.sub(r'href="assets/', 'href="/assets/', content)
content = re.sub(r"href='assets/", "href='/assets/", content)

# 2. Append missing scripts before </body>
#    Match only <script src="..."> occurrences, not comments.
has_header_script = re.search(r'<script[^>]+src=["\'][^"\']*wocs-header\.js', content) is not None
has_lead_popup_script = re.search(r'<script[^>]+src=["\'][^"\']*wocs-lead-popup', content) is not None
if not has_header_script or not has_lead_popup_script:
    lines_to_add = []
    if not has_lead_popup_script:
        lines_to_add.append('<script src="/assets/js/wocs-lead-popup.js"></script>')
    if not has_header_script:
        lines_to_add.append('<script src="/assets/js/wocs-header.js"></script>')
    insertion = '\n<!-- [Phase 2D] Restored subpage shared scripts -->\n' + '\n'.join(lines_to_add) + '\n'
    content = content.replace('</body>', insertion + '</body>')

if content != original:
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"patched vite-index.html: {len(original)} -> {len(content)} bytes")
else:
    print("no changes (already patched)")
