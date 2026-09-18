"""blog-data.js / content HTML에서 80자를 넘는 '제목'(실제로는 첫 문단이 제목으로 저장된 결함)을 복원.

배경: auto_writer.parse_content()가 LLM 출력에 '# 제목' 줄이 없으면 첫 문단을 제목으로 삼았다.
그래서 원본 HTML의 <title>/<h1>도 300자 문단이며 '실제 제목'이 존재하지 않는다.
복원 방법: 각 글의 본문 앞부분 + (날짜가 일치하면) 배정 주제 long_tail 힌트 → LLM이 60자 이내 제목 생성.
적용 범위: blog-data.js title + content/auto_post_*.html 의 <title>, <h1>, og:title, twitter:title, JSON-LD headline.

실행: python scripts/fix_long_titles.py [--dry-run]
키: OPENAI_API_KEY env 또는 C:\\Users\\user\\secrets\\openai_api_key.txt (프로젝트 폴더에 키 저장 금지)
"""
import html
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
TITLE_MAX = 80
GEN_MAX = 60
MODEL = "gpt-4.1"

spec = importlib.util.spec_from_file_location("bbs", ROOT / "scripts" / "build_blog_static.py")
bbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbs)
DRY_RUN = "--dry-run" in sys.argv          # auto_writer import 전에 캡처 (아래서 argv를 비움)
spec2 = importlib.util.spec_from_file_location("aw", ROOT / "auto_writer.py")
aw = importlib.util.module_from_spec(spec2)
sys.argv = [sys.argv[0]]
os.environ.setdefault("GEMINI_API_KEY", "x")  # auto_writer import 시 키 검사 우회 (호출 안 함)
spec2.loader.exec_module(aw)


def openai_key() -> str:
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k
    p = Path(r"C:\Users\user\secrets\openai_api_key.txt")
    return p.read_text(encoding="utf-8").strip().splitlines()[0].strip() if p.exists() else ""


def topic_hint(date: str) -> str:
    used = json.loads((ROOT / "used_topics.json").read_text(encoding="utf-8"))
    for key, d in used.items():
        if d == date:
            kw, region = key.split("|", 1)
            for t in aw.TOPICS:
                if t["keyword"] == kw and t["region"] == region:
                    return t["long_tail"]
    return ""


def generate_titles(items: list) -> dict:
    """items: [{id, excerpt, hint, category}] → {id: title}. 한 번의 호출로 일괄 생성."""
    lines = [f"- id {it['id']} | 카테고리 {it['category']} | 배정 주제 힌트: {it['hint'] or '없음'}\n  본문: {it['excerpt'][:400]}"
             for it in items]
    prompt = (
        "다음 각 블로그 글의 본문 앞부분을 읽고 한국어 제목을 지어라. 규칙: 60자 이내, 낚시성 금지, 본문 내용과 일치, "
        "지역명/키워드가 본문에 있으면 포함, '배정 주제 힌트'가 있으면 그 표현을 우선 활용. "
        "JSON object로만 출력: {\"<id>\": \"<제목>\", ...}\n\n" + "\n".join(lines)
    )
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {openai_key()}"},
                      json={"model": MODEL, "temperature": 0.3, "response_format": {"type": "json_object"},
                            "messages": [{"role": "user", "content": prompt}]}, timeout=180)
    r.raise_for_status()
    out = json.loads(r.json()["choices"][0]["message"]["content"])
    return {int(k): v.strip() for k, v in out.items()}


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def patch_content_file(path: Path, old_title: str, new_title: str) -> int:
    h = path.read_text(encoding="utf-8", errors="ignore")
    esc_old, esc_new = html.escape(old_title, quote=True), html.escape(new_title, quote=True)
    n = 0
    for old, new in ((old_title, new_title), (esc_old, esc_new), (json.dumps(old_title, ensure_ascii=False)[1:-1], json.dumps(new_title, ensure_ascii=False)[1:-1])):
        if old and old in h and old != new:
            n += h.count(old)
            h = h.replace(old, new)
    if n:
        path.write_text(h, encoding="utf-8")
    return n


def main() -> int:
    dry = DRY_RUN
    data_path = ROOT / "assets" / "js" / "blog-data.js"
    src = data_path.read_text(encoding="utf-8")
    posts = bbs.parse_blog_data(src)
    bbs.resolve_links(posts)
    targets = [p for p in posts if len(p["title"]) > TITLE_MAX]
    print(f"80자 초과 제목: {len(targets)}건")
    if not targets:
        return 0
    items = [{"id": p["id"], "excerpt": p["title"] + " " + p["excerpt"], "hint": topic_hint(p["date"]),
              "category": bbs.CATEGORY_LABELS.get(p["category"], "")} for p in targets]
    titles = generate_titles(items)
    problems = []
    for p in targets:
        new = titles.get(p["id"], "")
        if not new or len(new) > GEN_MAX:
            problems.append((p["id"], f"생성 실패/길이 {len(new)}"))
            continue
        old_literal = "title:'" + js_escape(p["title"]) + "'"
        if src.count(old_literal) != 1:
            problems.append((p["id"], f"blog-data literal 매치 {src.count(old_literal)}건"))
            continue
        touched = 0
        if p["href"].startswith("../content/"):
            fpath = ROOT / "content" / p["href"].split("/")[-1]
            touched = 0 if dry else patch_content_file(fpath, p["title"], new)
        print(f"  id={p['id']} ({p['date']}) {len(p['title'])}→{len(new)}자: {new}  [content 치환 {touched}곳]{'  hint✓' if topic_hint(p['date']) else ''}")
        if not dry:
            src = src.replace(old_literal, "title:'" + js_escape(new) + "'")
    for pid, why in problems:
        print(f"  UNRESOLVED id={pid}: {why}")
    if not dry:
        data_path.write_text(src, encoding="utf-8")
    print(f"{'[dry-run] ' if dry else ''}done: fixed={len(targets) - len(problems)} unresolved={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
