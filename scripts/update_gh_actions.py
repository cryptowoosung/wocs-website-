"""
Bump GitHub Actions versions for Node 24 compatibility (deadline 2026-06-02
per GitHub blog 2025-09-19).

Conservative upgrade set (versions verified to exist via gh api):
  actions/checkout           @v4*   -> @v5
  actions/cache              @v4*   -> @v5
  actions/upload-artifact    @v4*   -> @v5
  actions/setup-node         @v4*   -> @v6
  actions/setup-python       stays  (user instruction)

Works on exact pins (v4.2.2 etc) by matching @v4 prefix.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WF_DIR = os.path.join(ROOT, '.github', 'workflows')

REPLACEMENTS = [
    (re.compile(r'actions/checkout@v4(\.\d+\.\d+)?'), 'actions/checkout@v5'),
    (re.compile(r'actions/checkout@v3(\.\d+\.\d+)?'), 'actions/checkout@v5'),
    (re.compile(r'actions/cache@v4(\.\d+\.\d+)?'), 'actions/cache@v5'),
    (re.compile(r'actions/cache@v3(\.\d+\.\d+)?'), 'actions/cache@v5'),
    (re.compile(r'actions/upload-artifact@v4(\.\d+\.\d+)?'), 'actions/upload-artifact@v5'),
    (re.compile(r'actions/upload-artifact@v3(\.\d+\.\d+)?'), 'actions/upload-artifact@v5'),
    (re.compile(r'actions/setup-node@v4(\.\d+\.\d+)?'), 'actions/setup-node@v6'),
    (re.compile(r'actions/setup-node@v3(\.\d+\.\d+)?'), 'actions/setup-node@v6'),
]

total_files = 0
total_edits = 0

for f in sorted(os.listdir(WF_DIR)):
    if not (f.endswith('.yml') or f.endswith('.yaml')):
        continue
    fp = os.path.join(WF_DIR, f)
    with open(fp, 'r', encoding='utf-8') as fh:
        content = fh.read()
    original = content
    edits = 0
    for pat, repl in REPLACEMENTS:
        new_content, n = pat.subn(repl, content)
        if n:
            edits += n
            content = new_content
    if content != original:
        total_files += 1
        total_edits += edits
        with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(content)
        print(f'updated ({edits}): {f}')

print()
print('=' * 40)
print(f'files updated: {total_files}')
print(f'total action refs bumped: {total_edits}')
