"""blog.html 목록 정적 폴백 생성기.

assets/js/blog-data.js(BLOG_POSTS)를 읽어 resources/blog.html 의 #blogGrid 안에
서버 렌더 목록(제목+요약+링크+날짜)을 삽입한다. JS는 로드 후 innerHTML을 덮어쓰므로
화면은 그대로이고, JS 없는 크롤러도 글 목록과 링크를 볼 수 있다.

링크 우선순위: content/auto_post_<date>[_n].html (정적 SEO 페이지) → 없으면 blog-post.html?id=N
auto_writer.py 실행 뒤(auto_blog.yml) 매번 호출된다. 단독 실행도 가능: python scripts/build_blog_static.py
"""
import html
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_DATA = ROOT / "assets" / "js" / "blog-data.js"
BLOG_HTML = ROOT / "resources" / "blog.html"
CONTENT_DIR = ROOT / "content"
SITE_URL = "https://wocs.kr"
MAX_ITEMS = 60          # 정적 목록 상한 (페이지 크기 관리)
START = "<!-- static-blog-list:start -->"
END = "<!-- static-blog-list:end -->"

CATEGORY_LABELS = {
    "cat_startup": "창업가이드", "cat_construction": "시공기술", "cat_trend": "트렌드",
    "cat_revenue": "수익분석", "cat_permit": "인허가", "cat_case": "사례",
}

_STR = r"'((?:\\.|[^'\\])*)'"


def _unescape_js(s: str) -> str:
    return s.replace("\\'", "'").replace("\\n", " ").replace("\\\\", "\\")


def parse_blog_data(text: str) -> list:
    """BLOG_POSTS 배열의 각 객체에서 id/title/excerpt/description/date/category만 추출."""
    body = text.split("var BLOG_POSTS = [", 1)[1]
    posts = []
    # 객체 경계: 줄 시작의 '{' ~ 줄 시작의 '}' (blog-data.js 포맷 고정)
    for chunk in re.findall(r"^\{\s*\n(.*?)^\}", body, re.S | re.M):
        def field(name, pattern=_STR):
            m = re.search(rf"(?:^|,|\s){name}:\s*{pattern}", chunk, re.S)
            return m.group(1) if m else ""
        pid = field("id", r"(\d+)")
        if not pid:
            continue
        posts.append({
            "id": int(pid),
            "title": _unescape_js(field("title")),
            "excerpt": _unescape_js(field("excerpt") or field("description")),
            "date": field("date"),
            "category": field("category"),
        })
    return posts


def translation_lookup(blog_html: str) -> dict:
    """title:'bt1' 같은 번역 키를 blog.html 내 WOCS_PAGE_TR.ko 사전에서 해석."""
    m = re.search(r"WOCS_PAGE_TR=\{ko:\{(.*?)\},", blog_html, re.S)
    if not m:
        return {}
    return {k: v for k, v in re.findall(r'(\w+):"((?:[^"\\]|\\.)*)"', m.group(1))}


def resolve_links(posts: list) -> None:
    """같은 날짜 글이 여러 개면 auto_writer와 같은 규칙(_2, _3…)으로 파일을 배정. 최신 id가 먼저 온다는 점을 반영."""
    by_date = defaultdict(list)
    for p in posts:
        by_date[p["date"]].append(p)
    for date, group in by_date.items():
        group_sorted = sorted(group, key=lambda p: p["id"])  # 오래된 id = 먼저 생성 = 접미사 없음
        for idx, p in enumerate(group_sorted):
            fname = f"auto_post_{date}.html" if idx == 0 else f"auto_post_{date}_{idx + 1}.html"
            if (CONTENT_DIR / fname).exists():
                p["href"] = f"../content/{fname}"
            else:
                p["href"] = f"blog-post.html?id={p['id']}"


def render_static_list(posts: list, tr: dict) -> str:
    items = []
    for p in posts[:MAX_ITEMS]:
        title = tr.get(p["title"], p["title"]) if re.fullmatch(r"bt\d+", p["title"]) else p["title"]
        excerpt = tr.get(p["excerpt"], p["excerpt"]) if re.fullmatch(r"be\d+", p["excerpt"]) else p["excerpt"]
        cat = CATEGORY_LABELS.get(p["category"], "블로그")
        items.append(
            f'<article class="bg-card bg-card--static"><a href="{html.escape(p["href"])}">'
            f'<h3>{html.escape(title)}</h3></a>'
            f'<p class="bg-excerpt">{html.escape(excerpt[:140])}</p>'
            f'<p class="bg-meta"><time datetime="{html.escape(p["date"])}">{html.escape(p["date"])}</time> · {html.escape(cat)}</p>'
            f"</article>"
        )
    return f"{START}\n" + "\n".join(items) + f"\n{END}"


def inject(blog_html: str, static_block: str) -> str:
    # 기존 정적 블록이 있으면 교체, 없으면 #blogGrid 안에 삽입
    if START in blog_html and END in blog_html:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: static_block, blog_html, flags=re.S)
    anchor = '<div class="blog-grid" id="blogGrid">'
    if anchor not in blog_html:
        raise RuntimeError("blog.html에서 #blogGrid 앵커를 찾을 수 없음")
    return blog_html.replace(anchor, anchor + "\n" + static_block, 1)


def main() -> int:
    blog_html = BLOG_HTML.read_text(encoding="utf-8")
    posts = parse_blog_data(BLOG_DATA.read_text(encoding="utf-8"))
    if not posts:
        raise RuntimeError("blog-data.js에서 글을 하나도 파싱하지 못함")
    resolve_links(posts)
    static_block = render_static_list(posts, translation_lookup(blog_html))
    new_html = inject(blog_html, static_block)
    # 빈 상태 문구는 JS가 채우도록 서버 HTML에서 제거 (크롤러가 '글 없음'으로 오독하지 않게)
    new_html = new_html.replace(
        '<div class="blog-empty" id="blogEmpty" style="display:none" data-t="p11">해당 카테고리의 글이 없습니다.</div>',
        '<div class="blog-empty" id="blogEmpty" style="display:none" data-t="p11"></div>',
    )
    # JS 사전의 빈 상태 문구도 '글이 없다'는 단정 표현을 피한 동의어로 (크롤러 텍스트 추출 시 오독 방지)
    new_html = new_html.replace('p11:"해당 카테고리의 글이 없습니다."', 'p11:"선택한 분류에 표시할 글이 없습니다."')
    if new_html == blog_html:
        print("blog.html 변경 없음 (정적 목록 최신 상태)")
        return 0
    BLOG_HTML.write_text(new_html, encoding="utf-8")
    linked_static = sum(1 for p in posts[:MAX_ITEMS] if p["href"].startswith("../content/"))
    print(f"blog.html 정적 목록 갱신: {min(len(posts), MAX_ITEMS)}건 (정적 파일 링크 {linked_static}건, 전체 글 {len(posts)}건)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
