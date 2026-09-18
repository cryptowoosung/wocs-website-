"""auto_writer 드라이런 — 레포 복사본(임시 폴더)에서 실행, LLM은 OpenAI(gpt-4.1)로 대체.

실제 레포 파일·커밋·LinkedIn·Unsplash에 영향 없음. 생성된 HTML을 검사해 AEO/GEO 요소를 보고한다.
키: OPENAI_API_KEY env 또는 C:\\Users\\user\\secrets\\openai_api_key.txt
실행: python scripts/dryrun_auto_writer.py
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def openai_key() -> str:
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k
    p = Path(r"C:\Users\user\secrets\openai_api_key.txt")
    return p.read_text(encoding="utf-8").strip().splitlines()[0].strip()


def openai_generate(prompt: str, label: str = "gen") -> str:
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {openai_key()}"},
                      json={"model": "gpt-4.1", "temperature": 0.7,
                            "messages": [{"role": "user", "content": prompt}]}, timeout=180)
    r.raise_for_status()
    print(f"  [{label}] openai ok")
    return r.json()["choices"][0]["message"]["content"]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="wocs_dryrun_"))
    for f in ("auto_writer.py", "llm_json.py", "used_topics.json", "cta_counter.json"):
        shutil.copy(ROOT / f, tmp / f)
    (tmp / "assets" / "js").mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "js" / "blog-data.js", tmp / "assets" / "js" / "blog-data.js")
    (tmp / "content").mkdir()
    os.chdir(tmp)
    os.environ.setdefault("GEMINI_API_KEY", "dryrun")
    sys.argv = ["auto_writer.py"]
    spec = importlib.util.spec_from_file_location("aw", tmp / "auto_writer.py")
    aw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aw)
    aw.gemini_generate_with_retry = openai_generate          # LLM 대체
    aw.get_unsplash_image = lambda kw: "https://example.com/dryrun.jpg"
    aw.generate_linkedin_post = lambda *a, **k: ""          # 외부 호출 차단
    print(f"임시 폴더: {tmp}")
    aw.main()

    html_files = sorted((tmp / "content").glob("auto_post_*.html"))
    if not html_files:
        print("생성물 없음")
        return 1
    h = html_files[-1].read_text(encoding="utf-8")
    lds = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h, re.S)
    types = []
    for s in lds:
        j = json.loads(s)
        types += [x.get("@type") for x in j.get("@graph", [j])]
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", h)
    q = [x for x in h2 if re.search(r"\?|나요|인가요|하나요|까요", x)]
    title = re.search(r"<title>(.*?)</title>", h).group(1)
    report = {
        "file": html_files[-1].name, "title": title, "title_len": len(title.replace(" | WOCS", "")),
        "ld_json_blocks": len(lds), "FAQPage": "FAQPage" in types, "BlogPosting": "BlogPosting" in types,
        "h2_total": len(h2), "h2_question": len(q), "tldr_block": 'class="tldr"' in h,
        "faq_section": "자주 묻는 질문" in h, "faq_details": h.count("<details>"),
        "keypoints_block": 'class="keypoints"' in h, "eeat_block": 'class="eeat"' in h,
        "hedge_phrases": h.count("현장 확인") + h.count("견적 시"), "experience_signal": h.count("16년"),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("H2:", h2)
    shutil.copy(html_files[-1], ROOT / "scripts" / "dryrun_last.html")
    print("샘플 저장: scripts/dryrun_last.html (git 무시 대상)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
