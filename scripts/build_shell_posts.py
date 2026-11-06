#!/usr/bin/env python3
"""껍데기(blog-post.html?id=)로만 열리던 글을 /content/ 정적 HTML 로 만든다. 1회성 스크립트.

템플릿·canonical·메타는 auto_writer.save_to_html 을 그대로 호출해 기존 글과 같게 한다.
본문은 blog-data.js 원문을 쓰며 문장을 고치지 않는다. 공백 두 칸으로만 구분된 문단을 나눌 뿐이다.
이미 파일이 있는 글은 건너뛰므로 다시 실행해도 안전하다.

실행: GEMINI_API_KEY=unused python scripts/build_shell_posts.py
(auto_writer 가 import 때 키 존재만 확인한다. 이 스크립트는 API 를 호출하지 않는다.)
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

import auto_writer  # noqa: E402
import build_blog_static as bbs  # noqa: E402

# 본문이 1,000자 이상이고 대응 /content/ 글이 없는 글 id.
# id 1~12, 13, 100 은 본문이 57~650자라 만들지 않고 뷰어 주소로 둔다.
POST_IDS = (130, 129, 128, 123, 119, 115, 101)
MIN_BODY_CHARS = 1000
META_DESC_MAX = 155
REGIONS = ("보성", "해남", "여수", "고흥", "나주", "전남")  # 제목에서 찾을 지역명
CATEGORY_TOPICS = {"cat_startup": "창업가이드", "cat_construction": "시공정보"}
KEYWORDS = {"cat_startup": "글램핑 창업", "cat_construction": "글램핑 시공"}


def load_posts() -> dict:
    """blog-data.js 의 글을 id 로 찾을 수 있게 읽는다 (본문·이미지·설명 포함)."""
    text = bbs.BLOG_DATA.read_text(encoding="utf-8")
    body = text.split("var BLOG_POSTS = [", 1)[1]
    posts = {}
    for chunk in re.findall(r"^\{\s*\n(.*?)^\}", body, re.S | re.M):
        pid = re.search(r"\bid:\s*(\d+)", chunk)
        if pid:
            posts[int(pid.group(1))] = chunk
    return posts


def field(chunk: str, name: str) -> str:
    """작은따옴표 또는 큰따옴표 문자열 필드를 읽는다."""
    found = re.search(name + r""":\s*(?:'((?:\\.|[^'\\])*)'|"((?:\\.|[^"\\])*)")""", chunk, re.S)
    if not found:
        return ""
    raw = found.group(1) if found.group(1) is not None else found.group(2)
    return raw.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def to_paragraphs(content: str) -> str:
    """공백 두 칸 이상을 문단 구분으로 보고 줄을 나눈다. 구분선(---)은 뺀다."""
    lines = [line.strip() for line in re.split(r"\s{2,}", content)]
    return "\n".join(line for line in lines if line and line != "---")


def meta_description(chunk: str) -> str:
    """description 이 있으면 쓰고, 없으면 excerpt 를 쓴다."""
    text = field(chunk, "description") or field(chunk, "excerpt")
    return text[:META_DESC_MAX].strip()


def region_of(title: str) -> str:
    return next((name for name in REGIONS if name in title), "전남")


def fixed_clock(date: str) -> type:
    """save_to_html 이 글의 원래 날짜로 파일명·메타를 쓰도록 today 를 고정한다."""
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.strptime(date, "%Y-%m-%d")
    return FixedDatetime


def build_post(chunk: str, existing: dict) -> str | None:
    title = field(chunk, "title")
    if bbs._title_key(title) in existing:
        return None
    category = field(chunk, "category")
    body = to_paragraphs(field(chunk, "content"))
    if len(body) < MIN_BODY_CHARS:
        raise ValueError(f"본문이 {len(body)}자: {title}")
    keyword = KEYWORDS[category]
    topic = {"keyword": keyword, "region": region_of(title), "category": CATEGORY_TOPICS[category]}
    auto_writer.datetime = fixed_clock(field(chunk, "date"))
    auto_writer.save_to_html(0, title, body, topic, meta_description(chunk),
                             image_url=field(chunk, "image"), extra={"focus_keyword": keyword})
    return title


def main() -> int:
    posts = load_posts()
    existing = bbs.content_titles()
    made = [title for title in (build_post(posts[i], existing) for i in POST_IDS) if title]
    print(f"생성 {len(made)}편 / 대상 {len(POST_IDS)}편")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
