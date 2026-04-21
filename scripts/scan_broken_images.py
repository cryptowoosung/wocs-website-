"""
Scan HTML/JSX/JS for <img src=...> references and report any whose target
file does not exist on disk. Also flags filenames with unencoded spaces.
"""
import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {'node_modules', 'dist', '.git', 'public'}
EXTENSIONS = ('.html', '.jsx', '.js', '.tsx', '.ts')
IMG_EXTS = ('png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'avif')

# src="..." / src='...' — only local (not http/data)
RE_SRC = re.compile(
    r'''src=["']((?!https?:|data:|mailto:)[^"']+\.(?:''' + '|'.join(IMG_EXTS) + r'''))["']''',
    re.IGNORECASE,
)

def walk_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(EXTENSIONS):
                yield os.path.join(dirpath, name)


def resolve_ref(file_path, ref):
    ref_decoded = unquote(ref)
    ref_clean = ref_decoded.split('?', 1)[0].split('#', 1)[0]
    if ref_clean.startswith('/'):
        candidate = os.path.join(ROOT, ref_clean.lstrip('/'))
    else:
        candidate = os.path.normpath(os.path.join(os.path.dirname(file_path), ref_clean))
    return candidate


def main():
    broken = []
    spaced = []
    total_refs = 0
    for fp in walk_files():
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        # Strip HTML comments so placeholder src="..." inside <!-- --> is ignored.
        if fp.lower().endswith('.html'):
            scan_src = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        else:
            scan_src = content
        for m in RE_SRC.finditer(scan_src):
            total_refs += 1
            ref = m.group(1)
            line_no = scan_src.count('\n', 0, m.start()) + 1
            resolved = resolve_ref(fp, ref)
            if not os.path.isfile(resolved):
                broken.append((os.path.relpath(fp, ROOT), line_no, ref, os.path.relpath(resolved, ROOT)))
            if ' ' in ref:
                spaced.append((os.path.relpath(fp, ROOT), line_no, ref))

    print(f"Scanned {total_refs} image references across code files.\n")

    if broken:
        print(f"BROKEN references (file does not exist): {len(broken)}")
        for rel_fp, ln, ref, resolved in broken:
            print(f"  {rel_fp}:{ln}")
            print(f"    ref      : {ref}")
            print(f"    resolved : {resolved}")
    else:
        print("BROKEN: none")

    print()
    if spaced:
        print(f"Unencoded spaces in src (may or may not be broken): {len(spaced)}")
        for rel_fp, ln, ref in spaced:
            print(f"  {rel_fp}:{ln}  {ref!r}")
    else:
        print("Spaces: none")

    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
