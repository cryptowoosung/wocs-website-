"""내부링크 공용 모듈 — 상품 카탈로그 구성 + 링크 주입/검사.

auto_writer.py(신규 글)와 scripts/backfill_internal_links.py(기존 138편)가
같은 카탈로그·같은 규칙을 쓰도록 한 곳에 모았다.

상품 목록은 하드코딩하지 않고 products/ 디렉토리를 읽어 동적으로 구성한다.
"""
import os
import re
import glob

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# 본문에 있어야 하는 최소 내부링크 수 (products/ + content/ 합산)
MIN_INTERNAL_LINKS = 3

# 카탈로그에서 제외할 상품 페이지 (목록 페이지·미렌더 템플릿)
PRODUCT_EXCLUDE = frozenset(("index.html", "product-template.html"))

# 글 제목 키워드 -> 상품 slug 힌트. 카탈로그 이름만으로는 잡히지 않는
# 구어체 검색어("화장실", "혹한", "전기")를 상품에 연결한다.
KEYWORD_HINTS = {
    "dome-tent": ("돔텐트", "돔 텐트", "돔"),
    "geodesic-domes": ("지오데식", "돔 구조", "돔하우스"),
    "geodesic-domes-custom": ("맞춤", "커스텀", "주문제작"),
    "geodesic-domes-preconfigured": ("d-600", "패키지"),
    "geodesic-domes-ready": ("d-800", "재고", "즉시"),
    "safari-tents": ("사파리텐트", "사파리 텐트", "사파리"),
    "safari-basic": ("입문", "베이직", "소형", "창업 비용"),
    "safari-cabin": ("캐빈", "원목", "하이브리드"),
    "safari-elite": ("엘리트", "단열", "방음"),
    "safari-extreme": ("혹한", "극한", "겨울", "적설", "폭설"),
    "safari-luxury": ("럭셔리", "고급", "프리미엄"),
    "luxury-tents": ("시그니처", "럭셔리"),
    "bell-tent": ("벨텐트", "원형", "마이크로"),
    "nordic-tipi": ("티피", "원뿔", "독채"),
    "peak-lodge": ("헥사", "라운지"),
    "sailing-tent": ("에이펙스", "층고", "로지"),
    "birdcage": ("파빌리온", "360", "전망", "조망"),
    "cocoon-house": ("코쿤", "오벌", "내풍"),
    "cube-cabin": ("큐브", "프리패브", "조립"),
    "modular-bath": ("욕실", "화장실", "샤워", "위생"),
    "modular-deck": ("데크", "기초", "바닥"),
    "modular-systems": ("모듈러", "턴키", "단지"),
    "modular-units": ("유닛", "리셉션", "레스토랑", "공용"),
    "solar-system": ("태양광", "전기", "전원", "오프그리드", "발전"),
    "universal-joint": ("조인트", "무용접", "특허", "프레임", "구조 강도"),
    "addons": ("가구", "애드온", "액세서리", "침대", "조명", "인테리어"),
}

# 주제 매칭이 하나도 없을 때 쓰는 기본 상품 3종
DEFAULT_SLUGS = ("dome-tent", "safari-tents", "universal-joint")

_TAG_RE = re.compile(r"<[^>]+>")


def _text_of(html, pattern):
    m = re.search(pattern, html, re.S | re.I)
    if not m:
        return ""
    # <br> 는 줄바꿈이지 단어 경계가 아니다. 앞부분만 취하지 않으면
    # "무용접 유니버설 조인트WOCS 핵심 특허 기술"처럼 부제가 붙어버린다.
    head = re.split(r"<br\s*/?>", m.group(1), maxsplit=1, flags=re.I)[0]
    return re.sub(r"\s+", " ", _TAG_RE.sub("", head)).strip()


def _display_name(html, slug):
    """상품 표시명: h1 > og:title > title 순으로 채택하고 군더더기를 정리한다."""
    for pat in (r"<h1[^>]*>(.*?)</h1>",
                r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
                r"<title[^>]*>(.*?)</title>"):
        name = _text_of(html, pat)
        if not name:
            continue
        name = re.split(r"\s*[|—–]\s*", name)[0].strip()
        name = re.sub(r"^WOCS\s+", "", name).strip()
        if name:
            return name
    return slug.replace("-", " ")


def load_products(repo_root=REPO_ROOT):
    """products/ 를 읽어 [{slug, url, name, keywords}] 반환 (slug 오름차순)."""
    products = []
    for path in sorted(glob.glob(os.path.join(repo_root, "products", "*.html"))):
        fname = os.path.basename(path)
        if fname in PRODUCT_EXCLUDE:
            continue
        slug = fname[:-len(".html")]
        try:
            html = open(path, encoding="utf-8").read()
        except OSError:
            continue
        name = _display_name(html, slug)
        keywords = set(KEYWORD_HINTS.get(slug, ()))
        keywords.update(w.lower() for w in re.split(r"[\s·,/]+", name) if len(w) > 1)
        products.append({
            "slug": slug,
            "url": "/products/" + fname,
            "name": name,
            "keywords": tuple(sorted(keywords)),
        })
    return products


# 제목에서 잡힌 키워드는 본문에서 잡힌 것보다 이만큼 더 쳐준다.
TITLE_WEIGHT = 3


def match_products(text, products, limit=3, body=""):
    """글 제목(text) 키워드와 상품명을 매칭해 관련도 높은 순으로 최대 limit개 반환.

    제목만으로는 변별력이 부족해 대부분 기본값으로 떨어지므로, 본문(body)을
    가중치 낮은 보조 신호로 함께 본다. 매칭이 없으면 DEFAULT_SLUGS 를 쓴다.
    """
    title_low = (text or "").lower()
    body_low = (body or "").lower()
    scored = []
    for p in products:
        score = 0
        for k in p["keywords"]:
            if not k:
                continue
            kl = k.lower()
            if kl in title_low:
                score += TITLE_WEIGHT
            elif kl in body_low:
                score += 1
        if score:
            scored.append((score, p))
    scored.sort(key=lambda t: (-t[0], t[1]["slug"]))
    picked = [p for _, p in scored[:limit]]

    if not picked:
        by_slug = {p["slug"]: p for p in products}
        picked = [by_slug[s] for s in DEFAULT_SLUGS if s in by_slug]

    # 부족분은 기본 상품으로 채운다.
    if len(picked) < limit:
        by_slug = {p["slug"]: p for p in products}
        for s in DEFAULT_SLUGS:
            if len(picked) >= limit:
                break
            cand = by_slug.get(s)
            if cand and cand not in picked:
                picked.append(cand)
    return picked[:limit]


def recent_posts(repo_root=REPO_ROOT, limit=5, exclude=None):
    """최근 content/auto_post_*.html 글 [{url, title}] (최신순)."""
    posts = []
    paths = sorted(glob.glob(os.path.join(repo_root, "content", "auto_post_*.html")),
                   reverse=True)
    for path in paths:
        fname = os.path.basename(path)
        if exclude and fname == exclude:
            continue
        try:
            html = open(path, encoding="utf-8").read()
        except OSError:
            continue
        title = _text_of(html, r"<title[^>]*>(.*?)</title>")
        title = re.split(r"\s*\|\s*", title)[0].strip()
        if not title:
            continue
        posts.append({"url": "/content/" + fname, "title": title})
        if len(posts) >= limit:
            break
    return posts


def count_internal_links(html_or_md):
    """검증 기준과 동일하게 href="/products/ · href="/content/ 개수를 센다."""
    text = html_or_md or ""
    return (text.count('href="/products/') + text.count("href='/products/")
            + text.count('href="/content/') + text.count("href='/content/"))
