"""wocs.kr /llms.txt 생성 (정적 사이트용). 사이트 소개 + 주요 페이지 + 최신 글 30건.

auto_blog.yml에서 글 발행 후 매번 실행되어 최신 글 섹션이 자동 갱신된다. 단독 실행: python scripts/build_llms_txt.py
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "llms.txt"
SITE = "https://wocs.kr"
LATEST_N = 30

spec = importlib.util.spec_from_file_location("bbs", ROOT / "scripts" / "build_blog_static.py")
bbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbs)

PAGES = [
    ("/", "홈 — WOCS 모듈러 글램핑 구조물(사파리텐트·돔·시그니처) 제조·시공"),
    ("/products/", "제품 — D-시리즈 돔, S-시리즈 사파리텐트, 시그니처 구조물"),
    ("/portfolio/", "시공 포트폴리오 — 전남·광주·전국 글램핑 단지 사례"),
    ("/resources/blog.html", "블로그 — 글램핑 창업·시공·수익 분석 가이드"),
    ("/resources/faq.html", "자주 묻는 질문"),
    ("/about/", "WOCS 소개 — 16년 현장 경력, 특허 무용접 유니버설 조인트"),
    ("/contact/", "견적·상담 문의, 화순 쇼룸 방문 예약"),
]


def main() -> int:
    posts = bbs.parse_blog_data((ROOT / "assets" / "js" / "blog-data.js").read_text(encoding="utf-8"))
    bbs.resolve_links(posts)
    tr = bbs.translation_lookup((ROOT / "resources" / "blog.html").read_text(encoding="utf-8"))
    lines = [
        "# WOCS 우성어닝천막공사 (wocs.kr)",
        "",
        "> 전남 화순에서 사파리텐트·돔텐트·시그니처 글램핑 구조물을 직접 제조·시공하는 WOCS. 16년 현장 경력, "
        "특허 무용접 유니버설 조인트(볼트 조립식) 기술. 글램핑 창업 상담부터 3D 가설계, 시공, 사후관리까지.",
        "",
        "연락처: 010-4337-0582 · 전남 화순군 사평면 유마로 592 · 사업자 우성어닝천막공사캠프시스템",
        "관련 사이트: https://yanglim.kr (양림기업 — 광주·전남 금속·철구조물·판넬 시공) · https://glampingtentgo.com (우성어닝천막공사 — 어닝·천막)",
        "",
        "## 주요 페이지",
    ]
    lines += [f"- [{label}]({SITE}{path})" for path, label in PAGES]
    lines += ["", f"## 최신 글 (최근 {LATEST_N}건, 자동 갱신)"]
    for p in posts[:LATEST_N]:
        title = tr.get(p["title"], p["title"]) if p["title"].startswith("bt") else p["title"]
        excerpt = (tr.get(p["excerpt"], p["excerpt"]) if p["excerpt"].startswith("be") else p["excerpt"])[:120].replace("\n", " ")
        href = p["href"].replace("../", "/") if p["href"].startswith("../") else "/resources/" + p["href"]
        lines.append(f"- [{title}]({SITE}{href}) ({p['date']}): {excerpt}")
    lines += ["", "## 참고", f"- 사이트맵: {SITE}/sitemap.xml", f"- RSS: {SITE}/feed.xml", "- 언어: ko-KR"]
    text = "\n".join(lines) + "\n"
    if OUT.exists() and OUT.read_text(encoding="utf-8") == text:
        print("llms.txt 변경 없음")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"llms.txt 생성: 페이지 {len(PAGES)} + 최신 글 {min(len(posts), LATEST_N)}건")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
