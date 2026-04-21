"""
Replace Unsplash placeholder images in each product page's OPTIONAL FURNITURE
section with local photos, and strip the now-dead `data-replace="true"`
attribute.

Matching strategy:
  - Find every <img> whose src is an https:// URL (Unsplash/Pexels) and
    which sits inside a <div class="furn-card ...">.
  - Determine target local image by inspecting the card's alt text (label).
  - Write the relative path from the HTML file to assets/images/<target>.

Mapping (keyword in alt text → local file):
  bedroom/bed/침실/침대           → 53-furniture-bed.webp
  bathroom/bath/욕실              → 43-modular-bath.webp
  sofa/table/소파/테이블/라운지 세트 → 68-furniture-sofa-set.webp
  kitchen/dining/키친/주방/미니바   → 67-furniture-dining.webp
  lounge/deck/라운지/데크/계단/난간/브릿지/확장 → 64-furniture-lounge.webp

Solar-system page special mapping:
  panel/패널   → solar1.webp
  charging/충전 → solar2.webp
  fallback     → solar3.webp

Idempotent:
  - Skips tags whose src is already a local (relative) path.
  - Regex supports extra attributes (loading, fetchPriority, width/height, etc)
    between src= and alt= provided alt is somewhere in the same tag.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PRODUCTS_DIR = os.path.join(ROOT, 'products')

MAPPING_RULES = [
    (['침실', '침대', 'bedroom', 'bed module', 'bed '], 'assets/images/53-furniture-bed.webp'),
    (['욕실', 'bath', 'bathroom'], 'assets/images/43-modular-bath.webp'),
    (['소파', '티 테이블', '테이블', 'sofa', 'table', '라운지 세트', '테라스'], 'assets/images/68-furniture-sofa-set.webp'),
    (['키친', '주방', '미니바', 'kitchen', '다이닝', 'dining', 'mini bar'], 'assets/images/67-furniture-dining.webp'),
    (['데크 라운지', '라운지', 'lounge', '데크', 'deck', '계단', '난간', '브릿지', '확장'], 'assets/images/64-furniture-lounge.webp'),
    # Furniture sub-items mapped to available local assets
    (['의자', 'chair'], 'assets/images/56-furniture-chair.webp'),
    (['수납', '옷장', '캐비닛', '드레싱', 'wardrobe', 'cabinet', 'storage', 'dressing'], 'assets/images/69-furniture-wardrobe.webp'),
    # Nightstand / sidetable / lamp / lantern — use nightstand as the visual stand-in
    (['사이드테이블', 'nightstand', 'side table', '조명', 'lamp', 'light', 'lantern', '랜턴', '러그', '쿠션', 'rug', 'cushion'], 'assets/images/54-furniture-nightstand.webp'),
]

# Fallback for furn-card imgs whose label doesn't match any keyword above.
# Prevents an external-URL leak: the card will still show a generic furniture photo.
FALLBACK_IMAGE = 'assets/images/64-furniture-lounge.webp'

SOLAR_MAPPING = [
    (['패널', 'panel'], 'assets/images/solar1.webp'),
    (['충전', 'charging', 'charge'], 'assets/images/solar2.webp'),
]
SOLAR_DEFAULT = 'assets/images/solar3.webp'


def pick_image(label, is_solar):
    low = label.lower()
    if is_solar:
        for keywords, img in SOLAR_MAPPING:
            if any(kw.lower() in low for kw in keywords):
                return img
        return SOLAR_DEFAULT
    for keywords, img in MAPPING_RULES:
        if any(kw.lower() in low for kw in keywords):
            return img
    return FALLBACK_IMAGE


def relpath_from_html(html_path, asset_rel):
    html_dir = os.path.dirname(os.path.abspath(html_path))
    asset_abs = os.path.join(ROOT, asset_rel)
    return os.path.relpath(asset_abs, html_dir).replace('\\', '/')


# Match any <img ...> tag. We'll inspect individual attrs inside.
IMG_TAG_RE = re.compile(r'<img\b[^>]*?/?>', re.IGNORECASE)
SRC_RE = re.compile(r'''src=["']([^"']+)["']''', re.IGNORECASE)
ALT_RE = re.compile(r'''alt=["']([^"']+)["']''', re.IGNORECASE)


def tag_is_in_furn_card(content, tag_start, lookback=200):
    # Check the 200 chars before the tag for "class=\"furn-card" or similar
    window = content[max(0, tag_start - lookback):tag_start]
    return 'furn-card' in window


def process(html_path, content):
    is_solar = 'solar' in os.path.basename(html_path).lower()
    modifications = {'cards': 0, 'data_replace_removed': 0}

    out_parts = []
    last_end = 0
    for m in IMG_TAG_RE.finditer(content):
        tag = m.group(0)
        out_parts.append(content[last_end:m.start()])
        last_end = m.end()

        # Only touch imgs inside a furn-card wrapper
        if not tag_is_in_furn_card(content, m.start()):
            out_parts.append(tag)
            continue

        src_m = SRC_RE.search(tag)
        alt_m = ALT_RE.search(tag)
        if not src_m or not alt_m:
            out_parts.append(tag)
            continue

        src = src_m.group(1)
        alt = alt_m.group(1)

        # Skip local paths (idempotent)
        if not src.lower().startswith(('http://', 'https://', '//')):
            out_parts.append(tag)
            continue

        target = pick_image(alt, is_solar=is_solar)
        if not target:
            out_parts.append(tag)
            continue

        new_src = relpath_from_html(html_path, target)
        new_tag = tag[:src_m.start()] + f'src="{new_src}"' + tag[src_m.end():]
        modifications['cards'] += 1
        out_parts.append(new_tag)

    out_parts.append(content[last_end:])
    new_content = ''.join(out_parts)

    # Strip dead data-replace="true" attributes everywhere
    dr_before = new_content.count('data-replace="true"')
    new_content = re.sub(r'\s+data-replace="true"', '', new_content)
    dr_after = new_content.count('data-replace="true"')
    modifications['data_replace_removed'] = dr_before - dr_after

    return new_content, modifications


def main():
    files = sorted(
        os.path.join(PRODUCTS_DIR, f)
        for f in os.listdir(PRODUCTS_DIR)
        if f.endswith('.html')
    )
    totals = {'files_checked': 0, 'files_modified': 0, 'cards_replaced': 0, 'dr_removed': 0}
    for fp in files:
        totals['files_checked'] += 1
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content, mods = process(fp, content)
        if new_content != content:
            with open(fp, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
            totals['files_modified'] += 1
            totals['cards_replaced'] += mods['cards']
            totals['dr_removed'] += mods['data_replace_removed']
            rel = os.path.relpath(fp, ROOT).replace('\\', '/')
            print(f'  {rel}: {mods["cards"]} cards replaced, {mods["data_replace_removed"]} data-replace stripped')

    print()
    print('=' * 60)
    print(f'files checked:       {totals["files_checked"]}')
    print(f'files modified:      {totals["files_modified"]}')
    print(f'furn-card imgs replaced: {totals["cards_replaced"]}')
    print(f'data-replace removed:    {totals["dr_removed"]}')


if __name__ == '__main__':
    main()
