import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html.original')
DST = os.path.join(ROOT, 'vite-index.html')

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# <head>...</head>
head_match = re.search(r'<head>.*?</head>', content, re.DOTALL)
head_content = head_match.group(0) if head_match else ''

# Remove babel-standalone CDN
head_content = re.sub(r'<script[^>]*babel[^>]*></script>\s*', '', head_content)

# Remove react/react-dom CDNs (Vite bundles them)
head_content = re.sub(r'<script[^>]*unpkg\.com/react[^>]*></script>\s*', '', head_content)
head_content = re.sub(r'<script[^>]*cdnjs[^>]*react[^>]*></script>\s*', '', head_content)

# Body from <body> up to babel script
body_start_match = re.search(r'<body[^>]*>(.*?)<script type="text/babel">', content, re.DOTALL)
body_pre_script = body_start_match.group(1) if body_start_match else ''

has_root = '<div id="root"' in body_pre_script or "<div id='root'" in body_pre_script

new_html = f'''<!DOCTYPE html>
<html lang="ko">
{head_content}
<body>
{body_pre_script}
'''

if not has_root:
    new_html += '<div id="root"></div>\n'

new_html += '''<script type="module" src="/src/main.jsx"></script>
</body>
</html>
'''

with open(DST, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"vite-index.html written: {len(new_html)} bytes")
print(f"#root already present: {has_root}")
