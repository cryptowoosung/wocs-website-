"""
Rename files in assets/images/ whose names contain spaces, parentheses, or
commas. Produces web-safe filenames (hyphens only) and rewrites every
HTML/JSX/JS/MD/XML reference — both literal and %20-encoded forms.

Rules:
  - space → hyphen
  - ( ) removed
  - , → hyphen
  - collapse consecutive hyphens
  - strip trailing hyphen before extension (e.g. `foo-.pdf` → `foo.pdf`)
"""
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMG_DIR = os.path.join(ROOT, 'assets', 'images')


def sanitize(name):
    new = name.replace(' ', '-')
    new = re.sub(r'[()]', '', new)
    new = re.sub(r',', '-', new)
    new = re.sub(r'-+', '-', new)
    new = re.sub(r'-(\.[^.]+)$', r'\1', new)
    return new


rename_map = {}
for fname in os.listdir(IMG_DIR):
    if fname.startswith('.') or fname == '_original-backup':
        continue
    if not os.path.isfile(os.path.join(IMG_DIR, fname)):
        continue
    if not re.search(r'[ (),]', fname):
        continue
    new_name = sanitize(fname)
    if new_name != fname:
        rename_map[fname] = new_name

print('Rename plan:')
for old, new in rename_map.items():
    print(f'  {old}')
    print(f'    -> {new}')

if not rename_map:
    print('\nNo spaced files to rename.')
    raise SystemExit(0)

print('\nExecuting...')

# 1) Physical rename
for old, new in rename_map.items():
    old_path = os.path.join(IMG_DIR, old)
    new_path = os.path.join(IMG_DIR, new)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        shutil.move(old_path, new_path)
        print(f'  renamed: {old} -> {new}')
    elif os.path.exists(new_path):
        print(f'  target exists, skipping rename: {new}')

# 2) Reference rewrite across source files
TARGET_EXTS = ('.html', '.jsx', '.js', '.md', '.xml')
SKIP_DIRS = {'node_modules', 'dist', '.git', '_original-backup', 'venv', 'public', 'OneDrive', '.bkit', '.omc'}

total_files = 0
total_edits = 0

for root_dir, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith(TARGET_EXTS):
            continue
        fp = os.path.join(root_dir, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except Exception:
            continue
        original = content
        file_edits = 0
        for old, new in rename_map.items():
            encoded_old = old.replace(' ', '%20')
            for variant in (old, encoded_old):
                if variant != new and variant in content:
                    count = content.count(variant)
                    content = content.replace(variant, new)
                    file_edits += count
        if content != original:
            total_files += 1
            total_edits += file_edits
            with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(content)
            rel = os.path.relpath(fp, ROOT).replace('\\', '/')
            print(f'  updated ({file_edits} refs): {rel}')

print()
print('=' * 50)
print(f'files physically renamed: {len(rename_map)}')
print(f'source files updated:    {total_files}')
print(f'total reference edits:   {total_edits}')
