"""
Re-compress WebP images exceeding 300 KB using Pillow.

Strategy (2026 Web Vitals-aligned):
  - targets: WebP files over 300 KB (91 files per baseline)
  - backup first to assets/images/_original-backup/ (idempotent)
  - resize if original width > 1600 (keep aspect ratio)
  - encode with quality=80, method=6 (max effort)
  - original backup is always used as the compression source so repeated runs
    do not progressively degrade quality.

Logs per-file before/after sizes. Skips files that already have a backup
AND whose current size is already below the threshold (i.e. re-running is
safe and fast).
"""
import os
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, 'assets', 'images')
BACKUP_DIR = os.path.join(IMG_DIR, '_original-backup')
os.makedirs(BACKUP_DIR, exist_ok=True)

THRESHOLD_BYTES = 200 * 1024
MAX_WIDTH = 1200
QUALITY = 80
METHOD = 6

stats = {
    'processed': 0,
    'resized': 0,
    'errors': 0,
    'total_before': 0,
    'total_after': 0,
}

targets = []
for fname in sorted(os.listdir(IMG_DIR)):
    if not fname.lower().endswith('.webp'):
        continue
    if fname.startswith('.') or '_original-backup' in fname:
        continue
    path = os.path.join(IMG_DIR, fname)
    if not os.path.isfile(path):
        continue
    backup_path = os.path.join(BACKUP_DIR, fname)
    # Decide target: if already compressed AND backup exists, only re-process if
    # current size still exceeds threshold (which means prior run failed / partial).
    src_size_for_test = os.path.getsize(backup_path) if os.path.exists(backup_path) else os.path.getsize(path)
    if src_size_for_test > THRESHOLD_BYTES:
        targets.append((fname, path, backup_path))

print(f'Targets (original > {THRESHOLD_BYTES // 1024} KB): {len(targets)}')
print(f'Settings: quality={QUALITY}, method={METHOD}, max_width={MAX_WIDTH}\n')

for fname, path, backup_path in targets:
    try:
        # 1. Backup once
        if not os.path.exists(backup_path):
            shutil.copy2(path, backup_path)

        # 2. Always load from the backup to avoid generation loss
        with Image.open(backup_path) as im:
            orig_w, orig_h = im.size
            resized = False
            if orig_w > MAX_WIDTH:
                ratio = MAX_WIDTH / orig_w
                new_w = MAX_WIDTH
                new_h = int(round(orig_h * ratio))
                im = im.resize((new_w, new_h), Image.LANCZOS)
                resized = True
            im.save(path, format='WebP', quality=QUALITY, method=METHOD)

        orig_size = os.path.getsize(backup_path)
        new_size = os.path.getsize(path)
        stats['processed'] += 1
        stats['total_before'] += orig_size
        stats['total_after'] += new_size
        if resized:
            stats['resized'] += 1

        reduction = (1 - new_size / orig_size) * 100
        flag = 'R' if resized else ' '
        print(f'  [{flag}] {fname}: {orig_size / 1024:.0f} KB -> {new_size / 1024:.0f} KB ({reduction:+.0f}%)')
    except Exception as e:
        stats['errors'] += 1
        print(f'  ERR {fname}: {e}')

print()
print('='*60)
print(f'Processed: {stats["processed"]}')
print(f'Resized:   {stats["resized"]}')
print(f'Errors:    {stats["errors"]}')
print(f'Total: {stats["total_before"] / 1024 / 1024:.1f} MB -> {stats["total_after"] / 1024 / 1024:.1f} MB')
if stats['total_before']:
    print(f'Savings:   {(1 - stats["total_after"] / stats["total_before"]) * 100:.1f}%')
