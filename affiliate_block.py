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


def render(site, slot, env=None, spec=None):
    """슬롯 하나의 블록 HTML. 표시할 링크가 없으면 빈 문자열"""
    spec = spec or load_spec()
    env = os.environ if env is None else env
    conf = spec["sites"][site]
    tpl = spec["html"]
    disclosures, buttons = [], []
    for prog in ("coupang", "naver"):
        p = spec["programs"][prog]
        url = _link(env, p["env"], slot)
        if not url:
            continue
        disclosures.append(tpl["disclosure"].replace("{text}", html.escape(p["disclosure"])))
        buttons.append(tpl["button"].replace("{url}", html.escape(url, quote=True))
                       .replace("{label}", html.escape(p["label"])))
    if not buttons:
        return ""
    item = spec["slots"][slot]
    note = conf.get("notes", {}).get(slot, item["note"])
    return (tpl["wrap"].replace("{slot}", slot)
            .replace("{disclosures}", "".join(disclosures))
            .replace("{heading}", html.escape(conf["heading"]))
            .replace("{product}", html.escape(item["product"]))
            .replace("{note}", html.escape(note))
            .replace("{buttons}", "".join(buttons)))
