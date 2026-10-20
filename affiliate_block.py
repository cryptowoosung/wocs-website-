"""제휴 상품 블록 렌더러 (정의: shared/affiliate_block.json, n8n glampingtentgo 와 공용).

링크는 환경변수 COUPANG_LINK_1~3 / NAVER_CONNECT_LINK_1~3 에서만 읽는다 (쿠파스 API 호출 없음).
빈 값인 프로그램은 표시하지 않고, 둘 다 비면 블록 자체를 생략한다.
"""
import html
import json
import os

_SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared", "affiliate_block.json")


def load_spec():
    with open(_SPEC_PATH, encoding="utf-8") as f:
        return json.load(f)


def pick_slot(site, text, cat_key, spec=None):
    """제목·키워드 텍스트의 단어로 상품 슬롯을 고르고, 없으면 카테고리 → 사이트 기본값"""
    spec = spec or load_spec()
    conf = spec["sites"][site]
    for slot, words in conf.get("keyword_slots", []):
        if any(w in (text or "") for w in words):
            return slot
    return conf.get("category_slots", {}).get(cat_key or "", conf["default_slot"])


def _link(env, prefix, slot):
    url = str(env.get(prefix + slot) or "").strip()
    return url if url.startswith("https://") else ""


PROGRAMS = ("coupang", "naver")
PRODUCT_KEYS = {"coupang": "product", "naver": "naver_product"}  # 프로그램별 상품명 필드 (slots.n)


def _active(env, slot, spec):
    """해당 슬롯에 https 링크가 있는 프로그램 목록 (쿠팡 → 네이버 순)"""
    return [prog for prog in PROGRAMS if _link(env, spec["programs"][prog]["env"], slot)]


def _combined(spec, progs):
    return spec["combined_disclosure"].replace("{names}", " 및 ".join(spec["programs"][p]["name"] for p in progs))


def render_top_notice(slot, env=None, spec=None):
    """본문 맨 위 '#광고' 1줄. 두 프로그램 모두면 합친 고지문, 링크가 없으면 빈 문자열"""
    spec = spec or load_spec()
    env = os.environ if env is None else env
    progs = _active(env, slot, spec)
    if not progs:
        return ""
    if len(progs) > 1:
        text = _combined(spec, progs)
    else:
        text = spec["top_notice_text"].replace("{names}", spec["programs"][progs[0]]["name"])
    return spec["html"]["top_notice"].replace("{text}", html.escape(text))


def render(site, slot, env=None, spec=None):
    """슬롯 하나의 블록 HTML. 표시할 링크가 없으면 빈 문자열"""
    spec = spec or load_spec()
    env = os.environ if env is None else env
    conf = spec["sites"][site]
    tpl = spec["html"]
    progs = _active(env, slot, spec)
    if not progs:
        return ""
    item = spec["slots"][slot]
    if len(progs) > 1:
        texts = [_combined(spec, progs)]
    else:
        texts = [spec["programs"][progs[0]]["disclosure"]]
    disclosures = "".join(tpl["disclosure"].replace("{text}", html.escape(t)) for t in texts)
    buttons = "".join(tpl["button"].replace("{url}", html.escape(_link(env, spec["programs"][p]["env"], slot), quote=True))
                      .replace("{label}", html.escape(spec["programs"][p]["label"])) for p in progs)
    products = []
    for p in progs:
        name = item.get(PRODUCT_KEYS[p]) or item["product"]
        if name not in products:
            products.append(name)
    note = conf.get("notes", {}).get(slot, item["note"])
    return (tpl["wrap"].replace("{slot}", slot)
            .replace("{disclosures}", disclosures)
            .replace("{heading}", html.escape(conf["heading"]))
            .replace("{product}", html.escape(" · ".join(products)))
            .replace("{note}", html.escape(note))
            .replace("{buttons}", buttons))
