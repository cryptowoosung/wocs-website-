"""
Extract the 15 language blocks from the inline `const TR = { ... };` object
in src/App.jsx and write each to src/locales/<lang>.js as ESM.

Strategy:
- Parse brace depth starting from `const TR = {` (line 144).
- Within TR (depth == 1 relative to TR open), find entries like `<lang>: {`
  at brace level 1 and capture the contiguous object literal through its
  matching closing `}` then the optional trailing comma.

Writes `src/locales/<lang>.js` with:
  export default { ... };   // contents of the inner object

Idempotent: overwrites existing files.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'src', 'App.jsx')
OUTDIR = os.path.join(ROOT, 'src', 'locales')

with open(APP, 'r', encoding='utf-8') as f:
    src = f.read()

# Locate `const TR = {`
m = re.search(r'\bconst\s+TR\s*=\s*\{', src)
if not m:
    sys.exit('TR declaration not found')
tr_body_start = m.end()  # right after '{'

# Walk braces to find the matching '}' of TR
depth = 1
i = tr_body_start
while i < len(src) and depth > 0:
    ch = src[i]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            break
    i += 1
if depth != 0:
    sys.exit('Unbalanced braces in TR object')
tr_body_end = i  # position of TR's closing '}'

tr_body = src[tr_body_start:tr_body_end]

# Now parse top-level entries inside TR: `<identifier>: {...},`
LANG_KEYS = ['ko', 'en', 'ja', 'zh', 'es', 'fr', 'de', 'pt', 'it', 'ar', 'ru', 'tr', 'tw', 'id', 'th']

os.makedirs(OUTDIR, exist_ok=True)

# Iterate character by character, tracking depth within TR body
results = {}

j = 0
n = len(tr_body)
while j < n:
    # Skip whitespace and commas
    while j < n and tr_body[j] in ' \t\r\n,':
        j += 1
    if j >= n:
        break
    # Skip line/block comments
    if tr_body[j:j+2] == '//':
        nl = tr_body.find('\n', j)
        j = nl + 1 if nl != -1 else n
        continue
    if tr_body[j:j+2] == '/*':
        end = tr_body.find('*/', j + 2)
        j = end + 2 if end != -1 else n
        continue
    # Expect identifier followed by ':' then value
    idm = re.match(r'([A-Za-z_$][\w$-]*|"([^"]+)"|\'([^\']+)\')\s*:\s*', tr_body[j:])
    if not idm:
        # Unexpected; bail with diagnostic
        snippet = tr_body[j:j+80].replace('\n', '\\n')
        sys.exit(f'Parse error at offset {j}: {snippet!r}')
    key_raw = idm.group(1)
    key = idm.group(2) or idm.group(3) or key_raw
    j += idm.end()
    # Now at the value. We need its span.
    # The language values start with '{' — capture braced object.
    if tr_body[j] != '{':
        sys.exit(f'Expected object literal for key {key!r} at offset {j}')
    val_start = j
    d = 1
    j += 1
    while j < n and d > 0:
        ch = tr_body[j]
        if ch == '{':
            d += 1
        elif ch == '}':
            d -= 1
            if d == 0:
                break
        elif ch == '"' or ch == "'":
            # Skip quoted string
            quote = ch
            j += 1
            while j < n and tr_body[j] != quote:
                if tr_body[j] == '\\':
                    j += 2
                    continue
                j += 1
        elif ch == '`':
            # Skip template literal (no nested ${} parsing because TR uses plain strings here)
            j += 1
            while j < n and tr_body[j] != '`':
                if tr_body[j] == '\\':
                    j += 2
                    continue
                j += 1
        j += 1
    val_end = j + 1  # include the closing '}'
    value = tr_body[val_start:val_end]
    results[key] = value
    j = val_end

# Verify coverage
missing = [k for k in LANG_KEYS if k not in results]
extra = [k for k in results if k not in LANG_KEYS]
if missing:
    print(f'WARN: missing languages: {missing}', file=sys.stderr)
if extra:
    print(f'WARN: unexpected keys: {extra}', file=sys.stderr)

# Write each to a separate locale file
for key, value in results.items():
    out = os.path.join(OUTDIR, f'{key}.js')
    content = f'// Auto-generated from src/App.jsx TR["{key}"] block\n'
    content += 'export default ' + value + ';\n'
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f'wrote {out} ({len(value)} chars)')

# Emit TR span marker (start/end indices in original App.jsx) for the caller to use.
# Also capture leading '{' and trailing '}' positions in the original file.
print(f'\nTR body span (after opening {{ through closing }}):')
print(f'  start offset: {tr_body_start}')
print(f'  end offset:   {tr_body_end}')
# Line numbers for convenience
pre = src[:tr_body_start]
print(f'  start line:   {pre.count(chr(10)) + 1}')
print(f'  end line:     {src[:tr_body_end].count(chr(10)) + 1}')
