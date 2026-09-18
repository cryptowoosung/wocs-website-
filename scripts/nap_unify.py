"""wocs.kr NAP 통일 (2026-09-18). 멱등 — 여러 번 실행해도 결과 동일.

표준값: NAME_FULL/CEO/BIZNUM/ADDR/TEL/SAMEAS (아래 상수). 브랜드명(WOCS 우성어닝 등)은 유지.
범위: 사이트 골격만 — 홈(vite-index.html·index.html) noscript/JSON-LD, about/showroom, contact, 66개 페이지의
      서버 렌더 푸터 줄, JS 푸터(wocs-footer.js), React 홈 푸터(src/App.jsx), llms.txt 템플릿. content/(블로그 본문) 제외.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_FULL = "우성어닝천막공사캠프시스템"
CEO = "김우성"
BIZNUM = "465-02-03270"
ADDR = "전라남도 화순군 사평면 유마로 592"
TEL = "010-4337-0582"
SAMEAS = [
    "https://wocs.kr",
    "https://yanglim.kr",
    "https://glampingtentgo.com",
    "https://blog.naver.com/glampingtentgo",
    "https://www.instagram.com/woosung_tent/",
    "https://bsky.app/profile/wocs83.bsky.social",
    "https://www.youtube.com/@countrydiy",
    "https://www.linkedin.com/company/wocs-glamping",
    "https://www.facebook.com/profile.php?id=61559084995838",
    "https://x.com/mysunshinews",
]
BIZ_LINE = f"정식상호 {NAME_FULL} | 대표 {CEO} | 사업자등록번호 {BIZNUM} | {ADDR} | {TEL}"
BIZ_HTML = f'<p class="biz-line" style="font-size:11px;color:rgba(240,235,224,0.45);margin:12px 0 0;line-height:1.7">{BIZ_LINE}</p>'
STATIC_MARK = 'class="biz-line"'

changes = []


def log(path, what):
    changes.append((str(path.relative_to(ROOT)) if isinstance(path, Path) else path, what))


def sub_file(path: Path, pairs, label):
    s = path.read_text(encoding="utf-8")
    orig = s
    for old, new in pairs:
        if isinstance(old, re.Pattern):
            s = old.sub(new, s)
        else:
            s = s.replace(old, new)
    if s != orig:
        path.write_text(s, encoding="utf-8")
        log(path, label)
    return s != orig


# ── 1. 홈(vite-index.html, index.html): 구주소 → 표준, JSON-LD 정합, noscript 푸터 사업자 줄 ──
def fix_home(path: Path):
    if not path.exists():
        return
    s = path.read_text(encoding="utf-8")
    orig = s
    s = s.replace("전남 화순군 사평면 유마리에 위치한", f"{ADDR}에 위치한")
    s = s.replace("주소: 전라남도 화순군 사평면 유마리", f"주소: {ADDR}")
    # LocalBusiness JSON-LD 블록 재작성 (한 줄 JSON)
    m = re.search(r'<script type="application/ld\+json">\s*(\{"@context":"https://schema\.org","@type":"LocalBusiness".*?\})\s*</script>', s, re.S)
    if m:
        lb = json.loads(m.group(1))
        lb["name"] = NAME_FULL
        alts = ["WOCS 우성어닝", "WOCS", "우성어닝천막공사", "우성천막"] + [a for a in lb.get("alternateName", []) if a not in ("WOCS", "우성천막")]
        lb["alternateName"] = list(dict.fromkeys(alts))
        lb["legalName"] = NAME_FULL
        lb["telephone"] = TEL
        lb["address"] = {"@type": "PostalAddress", "streetAddress": "사평면 유마로 592", "addressLocality": "화순군",
                         "addressRegion": "전라남도", "postalCode": lb.get("address", {}).get("postalCode", "58128"), "addressCountry": "KR"}
        lb["sameAs"] = SAMEAS
        lb["founder"] = {"@type": "Person", "name": CEO}
        lb["vatID"] = BIZNUM
        s = s[:m.start(1)] + json.dumps(lb, ensure_ascii=False, separators=(",", ":")) + s[m.end(1):]
    # noscript 푸터에 사업자 줄
    if STATIC_MARK not in s:
        s = re.sub(r"(<footer>\s*<p>&copy; 2009-2026 WOCS[^\n]*</p>)", r"\1\n    " + BIZ_HTML, s, count=1)
    if s != orig:
        path.write_text(s, encoding="utf-8")
        log(path, "구주소→표준, LocalBusiness 정합, noscript 사업자 줄")


fix_home(ROOT / "vite-index.html")
fix_home(ROOT / "index.html")

# ── 2. about/showroom.html 구주소 ──
sub_file(ROOT / "about" / "showroom.html", [("전라남도 화순군 사평면 유마리", ADDR)], "showroom 주소 표준화")

# ── 3. contact: '전남 화순군 사평면 유마로 592' → 표준 (HTML + 번역 사전) ──
sub_file(ROOT / "contact" / "index.html", [("전남 화순군 사평면 유마로 592", ADDR)], "contact 주소 표준화")

# ── 4. 66개 페이지: 서버 렌더 푸터 줄 (JS가 innerHTML로 덮어쓰므로 화면 중복 없음) ──
n_pages = 0
for p in ROOT.rglob("*.html"):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("OneDrive/", "content/", "dist/", "node_modules/", ".playwright-mcp/")):
        continue
    s = p.read_text(encoding="utf-8", errors="ignore")
    if '<div id="wocs-footer"></div>' in s:
        s = s.replace('<div id="wocs-footer"></div>', f'<div id="wocs-footer">{BIZ_HTML}</div>')
        p.write_text(s, encoding="utf-8")
        n_pages += 1
if n_pages:
    log("(66 pages)", f"#wocs-footer 서버 렌더 사업자 줄 삽입 {n_pages}곳")

# ── 5. JS 푸터 (wocs-footer.js): footer-copy 아래 사업자 줄 ──
fj = ROOT / "assets" / "js" / "wocs-footer.js"
s = fj.read_text(encoding="utf-8")
if STATIC_MARK not in s:
    s = s.replace("      <div class=\"footer-copy\">${tc('footCopy')}\n      </div>\n",
                  "      <div class=\"footer-copy\">${tc('footCopy')}\n      </div>\n      " + BIZ_HTML + "\n", 1)
    fj.write_text(s, encoding="utf-8")
    log(fj, "JS 푸터 사업자 줄")

# ── 6. React 홈 푸터 (src/App.jsx): footCopy 아래 사업자 줄 ──
app = ROOT / "src" / "App.jsx"
s = app.read_text(encoding="utf-8")
if "biz-line" not in s:
    old = '              {t("footCopy")}\n            </div>\n'
    new = ('              {t("footCopy")}\n'
           '              <div className="biz-line" style={{ marginTop: 10, lineHeight: 1.7 }}>' + BIZ_LINE + '</div>\n'
           '            </div>\n')
    assert s.count(old) == 1, f"App.jsx footCopy anchor ({s.count(old)})"
    app.write_text(s.replace(old, new), encoding="utf-8")
    log(app, "React 푸터 사업자 줄")

# ── 7. llms.txt 템플릿 ──
lt = ROOT / "scripts" / "build_llms_txt.py"
s = lt.read_text(encoding="utf-8")
old_line = '        "연락처: 010-4337-0582 · 전남 화순군 사평면 유마로 592 · 사업자 우성어닝천막공사캠프시스템",'
if old_line in s:
    lt.write_text(s.replace(old_line, '        "' + BIZ_LINE + '",'), encoding="utf-8")
    log(lt, "llms.txt 사업자 줄 표준화")

for path, what in changes:
    print(f"  {path}: {what}")
print(f"done: {len(changes)} change groups")
