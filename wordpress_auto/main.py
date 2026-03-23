"""
glampingtentgo.com 워드프레스 자동 포스팅
- 매일 1개 블로그 글 자동 발행
- GitHub Actions 또는 로컬 실행
"""

import logging
import re
import sys

from content_source import get_today_content
from wordpress import create_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def markdown_to_html(md: str) -> str:
    """간단한 Markdown → HTML 변환"""
    try:
        import markdown

        return markdown.markdown(
            md.strip(),
            extensions=["extra", "sane_lists"],
        )
    except ImportError:
        logger.warning("markdown 패키지 없음, 수동 변환 사용")
        return _simple_md_to_html(md)


def _simple_md_to_html(md: str) -> str:
    """markdown 패키지 없을 때 최소 변환"""
    lines = md.strip().split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")
            continue

        # Headings
        if stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        # List items
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        # Horizontal rule
        elif stripped == "---":
            html_lines.append("<hr>")
        # Paragraph
        else:
            html_lines.append(f"<p>{stripped}</p>")

    if in_list:
        html_lines.append("</ul>")

    html = "\n".join(html_lines)
    # Bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    # Links
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)
    return html


def add_featured_image(post_id: int, image_url: str) -> None:
    """
    대표 이미지 설정 (스텁)

    구현 시:
    1. image_url에서 이미지 다운로드
    2. WP Media API로 업로드
    3. 포스트 featured_media 필드 업데이트
    """
    # media_id = upload_media(image_url)
    # requests.post(api_url(f"posts/{post_id}"), json={"featured_media": media_id}, auth=auth)
    logger.info("Featured image stub: post_id=%d", post_id)


def main():
    logger.info("=== 글램핑텐트고 자동 포스팅 시작 ===")

    # 1. 오늘의 콘텐츠 가져오기
    content = get_today_content()
    logger.info("오늘의 콘텐츠: %s", content.title)

    # 2. Markdown → HTML
    html_body = markdown_to_html(content.body_markdown)
    logger.info("HTML 변환 완료 (%d bytes)", len(html_body))

    # 3. 워드프레스 포스트 생성
    try:
        post_id, post_url = create_post(
            title=content.title,
            content_html=html_body,
            categories=content.categories,
            tags=content.tags,
            meta_description=content.meta_description,
            focus_keyword=content.focus_keyword,
        )
        logger.info("포스팅 성공! post_id=%d", post_id)
        logger.info("URL: %s", post_url)
    except Exception:
        logger.exception("포스팅 실패")
        sys.exit(1)

    logger.info("=== 자동 포스팅 완료 ===")


if __name__ == "__main__":
    main()
