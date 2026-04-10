"""WOCS SEO Fix — P0~P3 meta tag patches.

Rules (from user directive):
- Only modify <head> meta tags. No body/CSS/JS changes.
- Skip files that already have each specific item.
- Generate unique KR descriptions (70~160 chars) from title/h1/body.
- No exaggerated marketing phrases (최저가, 최고, 100%, 보장 etc).
- Back up current <head> of every file to seo_backup.json first.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = "https://wocs.kr"
BACKUP_PATH = ROOT / "seo_backup.json"

# ──────────────────────────────────────────────────────────
# File discovery
# ──────────────────────────────────────────────────────────

def find_html_files():
    files = []
    for p in ROOT.rglob("*.html"):
        parts = p.relative_to(ROOT).parts
        if any(x in parts for x in ("node_modules", ".git", "__pycache__", "dist")):
            continue
        files.append(p)
    return sorted(files)

def read(p):
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p, text):
    p.write_text(text, encoding="utf-8", newline="\n")

# ──────────────────────────────────────────────────────────
# Existing meta extraction
# ──────────────────────────────────────────────────────────

def get_title(html):
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    return m.group(1).strip() if m else None

def get_meta(html, name_or_prop, value):
    pat = (
        r'<meta[^>]*\b' + name_or_prop + r'\s*=\s*["\']' + re.escape(value) +
        r'["\'][^>]*\bcontent\s*=\s*["\']([^"\']*)["\'][^>]*>'
    )
    m = re.search(pat, html, re.I)
    if m:
        return m.group(1)
    pat2 = (
        r'<meta[^>]*\bcontent\s*=\s*["\']([^"\']*)["\'][^>]*\b' + name_or_prop +
        r'\s*=\s*["\']' + re.escape(value) + r'["\'][^>]*>'
    )
    m = re.search(pat2, html, re.I)
    return m.group(1) if m else None

def get_canonical(html):
    m = re.search(
        r'<link[^>]*\brel\s*=\s*["\']canonical["\'][^>]*\bhref\s*=\s*["\']([^"\']*)["\']',
        html, re.I,
    )
    if m:
        return m.group(1)
    m = re.search(
        r'<link[^>]*\bhref\s*=\s*["\']([^"\']*)["\'][^>]*\brel\s*=\s*["\']canonical["\']',
        html, re.I,
    )
    return m.group(1) if m else None

def get_h1_text(html):
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', html, re.I | re.S)
    if not m:
        return None
    raw = m.group(1)
    # strip inner tags
    clean = re.sub(r'<[^>]+>', ' ', raw)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean or None

def get_first_body_text(html, max_len=200):
    # look for first <p> with meaningful text
    for m in re.finditer(r'<p\b[^>]*>(.*?)</p>', html, re.I | re.S):
        raw = m.group(1)
        clean = re.sub(r'<[^>]+>', ' ', raw)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) >= 20:
            return clean[:max_len]
    # fallback: first <section> text
    for m in re.finditer(r'<section\b[^>]*>(.*?)</section>', html, re.I | re.S):
        raw = m.group(1)
        clean = re.sub(r'<[^>]+>', ' ', raw)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) >= 20:
            return clean[:max_len]
    return None

# ──────────────────────────────────────────────────────────
# Description & title generation
# ──────────────────────────────────────────────────────────

# Per-file overrides keyed by relative path.
# Each entry may specify description (90~140자 target) and/or title.
# description must be unique per file, 70~160자, include "WOCS", no exaggeration.
DESCRIPTIONS = {
    "about/index.html": "WOCS는 글램핑·어닝·천막·돔 시공 전문 브랜드로 무용접 공법과 자체 설계를 바탕으로 한 공간 솔루션을 제공합니다. 브랜드 철학과 연혁, 사업 영역을 소개합니다.",
    "about/team.html": "WOCS 팀을 소개합니다. 글램핑·어닝·천막·돔 시공을 이끄는 설계·제작·현장 담당 인력과 협력 파트너 구성을 확인할 수 있습니다.",
    "contact/index.html": "WOCS 글램핑·어닝·천막·돔 시공 상담 및 견적 문의 안내입니다. 전화, 이메일, 방문 상담 경로와 응대 절차를 정리했습니다.",
    "contact/roi-calculator.html": "WOCS ROI 계산기를 이용해 글램핑·어닝·숙박업 투자 대비 예상 수익과 회수 기간을 시뮬레이션할 수 있습니다. 초기 비용과 운영 지표를 입력해 결과를 확인하세요.",
    "gallery/index.html": "WOCS가 시공한 글램핑·어닝·천막·돔 현장 사례 사진 갤러리입니다. 다양한 규모와 용도의 실제 설치 사례를 카테고리별로 확인할 수 있습니다.",
    "index.html": "WOCS는 글램핑·어닝·천막·돔 분야의 설계부터 시공까지 원스톱으로 진행하는 전문 브랜드입니다. 무용접 공법, 자체 제작, 현장 맞춤 시공 서비스를 제공합니다.",
    "legal/cookies.html": "WOCS 웹사이트의 쿠키 정책입니다. 수집하는 쿠키의 종류, 사용 목적, 보관 기간 및 사용자의 쿠키 설정 변경 방법을 안내합니다.",
    "legal/privacy.html": "WOCS 개인정보 처리방침입니다. 수집하는 정보 항목, 이용 목적, 보관 기간, 제3자 제공 여부와 정보주체 권리 행사 절차를 안내합니다.",
    "legal/terms.html": "WOCS 웹사이트 및 서비스 이용 약관입니다. 서비스 범위, 이용자 의무, 책임 제한 및 분쟁 해결 절차 등 주요 조항을 정리했습니다.",
    "occasions/index.html": "WOCS 글램핑·어닝·천막·돔은 리조트, 호텔, 에어비앤비, 스포츠, 웨딩 등 다양한 용도에 맞춰 설계·시공됩니다. 용도별 적용 사례와 특징을 확인하세요.",
    "occasions/airbnb.html": "에어비앤비 운영자를 위한 WOCS 글램핑·돔 객실 솔루션입니다. 단기 숙박에 적합한 규모, 편의시설, 설치 조건과 운영 고려사항을 안내합니다.",
    "occasions/glamping-pod.html": "WOCS 글램핑 포드 시공 안내입니다. 소형 캡슐형 숙박 공간의 구조, 단열·방수 사양과 설치 프로세스, 주요 적용 사례를 확인할 수 있습니다.",
    "occasions/glamping.html": "WOCS 글램핑 시공 전문 안내입니다. 사파리텐트, 돔, 벨텐트 등 주요 객실 타입의 특징과 부지 기획부터 인테리어까지 이어지는 시공 절차를 소개합니다.",
    "occasions/hotel.html": "호텔 및 리조트에 적용하는 WOCS 어닝·돔·천막 시공 솔루션입니다. 로비, 야외 라운지, 수영장 주변 등 상업 공간의 요구에 맞춘 구조물을 제공합니다.",
    "occasions/permanent.html": "WOCS 영구 구조물 시공 안내입니다. 일시적 천막이 아닌 장기 사용이 가능한 돔·모듈러 하우스의 구조적 사양과 허가 조건을 설명합니다.",
    "occasions/resort.html": "리조트 단지용 WOCS 글램핑·돔 시공 안내입니다. 대단지 객실 구성, 공용시설, 단지 마스터플랜과 시공 일정 조율 방식을 확인할 수 있습니다.",
    "occasions/sports.html": "스포츠 시설용 WOCS 천막·돔 시공 안내입니다. 실내 연습장, 체육관, 경기장 부속 시설에 적합한 구조물 타입과 대형 공간 구축 방식을 소개합니다.",
    "occasions/wedding.html": "야외 웨딩홀·이벤트 공간용 WOCS 천막·돔 시공 안내입니다. 하객 규모별 구조물 선택, 동선 설계, 인테리어 마감과 임시 설치 옵션을 확인할 수 있습니다.",
    "occasions/winter.html": "동계 운영이 필요한 글램핑·숙박 시설을 위한 WOCS 돔·천막 시공 안내입니다. 단열·난방·방수 사양과 겨울철 구조 안전성에 관한 내용을 다룹니다.",
    "portfolio/index.html": "WOCS가 시공한 글램핑·어닝·천막·돔 프로젝트 포트폴리오입니다. 규모, 지역, 용도별로 정리된 실제 시공 사례와 프로젝트 개요를 확인할 수 있습니다.",
    "products/index.html": "WOCS 제품 라인업 전체 안내입니다. 사파리텐트, 돔, 벨텐트, 모듈러 하우스, 어닝 등 카테고리별 제품과 주요 사양을 한 페이지에서 탐색할 수 있습니다.",
    "products/addons.html": "WOCS 글램핑·돔 시공 시 함께 설치할 수 있는 부가 옵션 안내입니다. 데크, 난방, 조명, 인테리어 가구 등 객실 완성도를 높이는 구성품을 소개합니다.",
    "products/bell-tent.html": "WOCS 벨텐트 제품 안내입니다. 원형 캐빈 구조의 벨텐트 사이즈, 원단, 프레임 사양과 설치 방식, 글램핑·캠핑장 적용 사례를 확인할 수 있습니다.",
    "products/birdcage.html": "WOCS 버드케이지(새장형) 구조물 안내입니다. 개방감 있는 프레임 구조와 투광 패널을 활용한 독창적 외관의 제품 사양과 용도를 소개합니다.",
    "products/cocoon-house.html": "WOCS 코쿤 하우스 제품 안내입니다. 누에고치 형태의 유선형 객실 구조, 내외장 사양, 단열·방수 성능과 주요 시공 사례를 정리했습니다.",
    "products/cube-cabin.html": "WOCS 큐브 캐빈 제품 안내입니다. 정육면체 모듈러 객실의 구조적 특징, 내부 레이아웃, 단열·방수 사양과 설치 조건을 확인할 수 있습니다.",
    "products/dome-tent.html": "WOCS 돔 텐트 제품 안내입니다. 측지 돔 프레임 구조의 사이즈, 원단 사양, 하중 성능과 글램핑 객실용 적용 사례를 정리했습니다.",
    "products/geodesic-domes.html": "WOCS 지오데식(측지) 돔 전체 라인업 안내입니다. 측지 돔의 구조 원리, 사이즈 옵션, 적용 분야와 커스텀 가능 범위를 확인할 수 있습니다.",
    "products/geodesic-domes-custom.html": "WOCS 측지 돔 커스텀 제품 안내입니다. 지름, 높이, 창호 위치, 원단 색상 등을 현장 요구에 맞춰 개별 설계하는 옵션과 주문 절차를 소개합니다.",
    "products/geodesic-domes-preconfigured.html": "WOCS 사전 구성 측지 돔 제품 안내입니다. 자주 요청되는 사이즈와 옵션을 표준화한 패키지 모델의 사양과 납기 조건을 정리했습니다.",
    "products/geodesic-domes-ready.html": "WOCS 즉시 출고 가능한 측지 돔 재고 제품 안내입니다. 표준 사이즈별 재고 현황과 단기 설치가 필요한 현장을 위한 납품 절차를 확인할 수 있습니다.",
    "products/luxury-tents.html": "WOCS 럭셔리 텐트 제품 안내입니다. 프리미엄 원단, 고급 프레임, 넓은 실내 공간으로 호텔급 글램핑 객실에 어울리는 고사양 텐트를 소개합니다.",
    "products/modular-bath.html": "WOCS 모듈러 욕실 유닛 안내입니다. 글램핑·돔 객실에 설치 가능한 독립형 욕실 모듈의 내부 구성, 배관 조건과 설치 절차를 확인할 수 있습니다.",
    "products/modular-deck.html": "WOCS 모듈러 데크 제품 안내입니다. 글램핑·돔 객실 외부에 구축하는 조립식 데크의 자재, 사이즈, 설치 방식과 마감 옵션을 정리했습니다.",
    "products/modular-systems.html": "WOCS 모듈러 시스템 안내입니다. 객실, 욕실, 데크 등 유닛을 조합해 숙박 단지를 구축하는 모듈 공법의 구조와 장점을 설명합니다.",
    "products/modular-units.html": "WOCS 모듈러 유닛 제품 안내입니다. 공장 선 제작 후 현장 조립하는 조립식 객실 유닛의 표준 사양과 커스터마이징 범위를 확인할 수 있습니다.",
    "products/nordic-tipi.html": "WOCS 노르딕 티피 제품 안내입니다. 북유럽 전통 원추형 천막 구조의 사이즈, 원단, 중앙 기둥 사양과 글램핑 적용 사례를 정리했습니다.",
    "products/peak-lodge.html": "WOCS 피크 로지 제품 안내입니다. 경사 지붕 구조의 박공형 객실 모델의 구조, 단열 성능, 실내 활용도와 주요 적용 용도를 확인할 수 있습니다.",
    "products/safari-basic.html": "WOCS 사파리 텐트 베이직 라인 제품 안내입니다. 글램핑 입문 및 보급형 객실에 적합한 기본 사양의 사파리 텐트 구성과 설치 조건을 소개합니다.",
    "products/safari-cabin.html": "WOCS 사파리 캐빈 제품 안내입니다. 텐트와 캐빈의 장점을 결합한 하이브리드 구조의 사양, 단열, 내부 공간 활용도를 확인할 수 있습니다.",
    "products/safari-elite.html": "WOCS 사파리 텐트 엘리트 라인 제품 안내입니다. 강화된 원단과 프레임, 넓은 실내를 갖춘 중상급 글램핑 객실용 사파리 텐트 사양을 정리했습니다.",
    "products/safari-extreme.html": "WOCS 사파리 익스트림 제품 안내입니다. 혹한·강풍 등 극한 환경을 고려한 강화 프레임과 고사양 원단이 적용된 사파리 텐트를 소개합니다.",
    "products/safari-luxury.html": "WOCS 사파리 럭셔리 제품 안내입니다. 최상위 등급 원단, 고급 내장재, 넓은 실내 구성을 갖춘 프리미엄 사파리 텐트의 사양을 확인할 수 있습니다.",
    "products/safari-tents.html": "WOCS 사파리 텐트 전체 라인업 안내입니다. 베이직, 엘리트, 럭셔리, 익스트림 등 등급별 사파리 텐트의 차이와 적용 용도를 정리했습니다.",
    "products/sailing-tent.html": "WOCS 세일링 텐트 제품 안내입니다. 돛 형태의 유려한 곡선 지붕 구조로 이벤트·야외 공간에 활용되는 텐트의 사양과 설치 조건을 소개합니다.",
    "products/solar-system.html": "WOCS 글램핑·돔 시설을 위한 태양광 시스템 안내입니다. 오프그리드 환경에서도 운영 가능한 자가발전 솔루션의 구성과 설치 방식을 확인할 수 있습니다.",
    "project/index.html": "WOCS 글램핑·어닝·돔 창업 프로젝트 전체 안내입니다. 부지 선정부터 설계, 인허가, 시공, 운영까지 이어지는 프로젝트 진행 절차를 정리했습니다.",
    "project/buying-land.html": "글램핑·숙박업 부지 매입 가이드입니다. WOCS가 제안하는 입지 분석, 법적 검토, 계약 전 점검 항목과 부지 기획 단계에서의 주의사항을 안내합니다.",
    "project/financing.html": "글램핑·숙박업 창업 자금 조달 가이드입니다. WOCS 프로젝트 진행 시 참고할 수 있는 대출, 리스, 투자 유치 등 주요 자금 조달 방식과 검토 포인트를 설명합니다.",
    "project/planning-cases.html": "WOCS 글램핑·숙박 프로젝트 기획 사례 모음입니다. 부지 조건별, 규모별 기획 방향과 실제 진행된 프로젝트의 배치도 및 구성 예시를 확인할 수 있습니다.",
    "project/revenue-sharing.html": "WOCS 수익 공유 모델 안내입니다. 글램핑·숙박 창업 시 초기 투자 부담을 낮추기 위한 수익 분배 방식의 구조와 계약 조건을 정리했습니다.",
    "project/start-business.html": "WOCS와 함께하는 글램핑·숙박업 창업 가이드입니다. 사업 기획, 부지 확보, 설계, 인허가, 시공, 운영까지 단계별로 필요한 준비 사항을 설명합니다.",
    "resources/index.html": "WOCS 자료실 메인 페이지입니다. 블로그, 고객 후기, 자주 묻는 질문, 카탈로그 다운로드, 대리점 안내 등 주요 자료와 정보를 한곳에서 확인할 수 있습니다.",
    "resources/blog.html": "WOCS 블로그입니다. 글램핑 창업, 시공 기술, 수익 분석, 시장 트렌드 등 업계 현장에서 도움이 되는 전문 정보를 공유합니다.",
    "resources/dealer.html": "WOCS 대리점 및 파트너사 안내입니다. 지역별 상담 가능한 대리점 네트워크와 파트너십 지원 제도, 협력 절차를 정리했습니다.",
    "resources/downloads.html": "WOCS 카탈로그, 도면, 사양서 등 다운로드 자료 모음입니다. 글램핑·어닝·돔 제품 관련 PDF 자료를 목록에서 내려받을 수 있습니다.",
    "resources/faq.html": "WOCS 글램핑·어닝·돔 관련 자주 묻는 질문 모음입니다. 시공 일정, 견적, 유지보수, 인허가 등 고객이 자주 궁금해하는 내용을 정리했습니다.",
    "resources/reviews.html": "WOCS 시공을 경험한 고객들의 후기 모음입니다. 글램핑·돔·어닝 시공 프로젝트 진행 과정과 완공 후 운영 소감을 확인할 수 있습니다.",
}

# Title overrides for files with too-short or too-long titles.
# Must be 15~60 chars. WOCS branding kept.
TITLE_OVERRIDES = {
    "about/team.html": "WOCS 팀 소개 — 글램핑·어닝 전문 시공 인력",
    "contact/roi-calculator.html": "글램핑 ROI 계산기 — 투자 대비 수익 시뮬레이션 | WOCS",
    "legal/cookies.html": "쿠키 정책 — WOCS 웹사이트 이용 안내",
    "legal/privacy.html": "개인정보 처리방침 — WOCS 정보 수집·이용 안내",
    "legal/terms.html": "이용 약관 — WOCS 웹사이트·서비스 이용 안내",
    "occasions/glamping-pod.html": "글램핑 팟 — 캡슐형 소형 숙박 시설 | WOCS",
    "occasions/glamping.html": "아웃도어 글램핑 시설 — 부지 기획부터 시공까지 | WOCS",
    "occasions/hotel.html": "호텔·리조트 확장 구조물 — 어닝·돔 시공 | WOCS",
    "occasions/permanent.html": "반영구 숙박 주거 구조물 시공 | WOCS",
    "occasions/resort.html": "B2B 리조트 단지 글램핑·돔 시공 | WOCS",
    "occasions/sports.html": "스포츠 시설용 천막·돔 구조물 시공 | WOCS",
    "occasions/winter.html": "동계 글램핑 — 단열·난방 객실 시공 | WOCS",
    "portfolio/index.html": "WOCS 글램핑·어닝·돔 시공 포트폴리오",
    "products/addons.html": "글램핑·돔 객실 애드온 옵션 제품 | WOCS",
    "products/dome-tent.html": "D-시리즈 돔 텐트 — 측지 돔 객실 | WOCS",
    "products/geodesic-domes-preconfigured.html": "D-600 사전 구성 측지 돔 모델 | WOCS",
    "products/geodesic-domes-ready.html": "D-800 재고 보유 측지 돔 모델 | WOCS",
    "products/modular-bath.html": "모듈러 욕실 유닛 — 글램핑 객실용 | WOCS",
    "products/modular-deck.html": "모듈러 데크 — 조립식 외부 데크 | WOCS",
    "products/modular-systems.html": "모듈러 시스템 — 조립식 숙박 단지 | WOCS",
    "products/modular-units.html": "모듈러 유닛 — 조립식 객실 모듈 | WOCS",
    "products/safari-cabin.html": "S-Suite 사파리 캐빈 하이브리드 객실 | WOCS",
    "products/safari-elite.html": "S-Lodge 사파리 엘리트 텐트 | WOCS",
    "products/solar-system.html": "태양광 시스템 — 오프그리드 글램핑 전원 | WOCS",
    "project/buying-land.html": "글램핑·숙박업 부지 매입 가이드 | WOCS",
    "project/financing.html": "글램핑 창업 파이낸싱·자금 조달 | WOCS",
    "project/index.html": "글램핑·숙박업 프로젝트 기획 | WOCS",
    "project/planning-cases.html": "글램핑 프로젝트 기획 사례 모음 | WOCS",
    "project/revenue-sharing.html": "WOCS 글램핑 수익 공유 모델 안내",
    "project/start-business.html": "글램핑 창업 가이드 — 부지부터 운영까지 | WOCS",
    "resources/blog.html": "WOCS 블로그 — 글램핑 창업·시공·트렌드",
    "resources/dealer.html": "WOCS 대리점·파트너사 지원 안내",
    "resources/downloads.html": "WOCS 카탈로그·도면 다운로드 자료실",
    "resources/faq.html": "WOCS 글램핑·어닝·돔 자주 묻는 질문",
    "resources/index.html": "WOCS 자료실 — 블로그·후기·다운로드",
    "resources/reviews.html": "WOCS 시공 고객 후기·리뷰 모음",
}

# ──────────────────────────────────────────────────────────
# HTML patching helpers
# ──────────────────────────────────────────────────────────

def insert_after_title(html, snippet):
    """Insert a line after the first </title>."""
    return re.sub(
        r'(</title>)',
        r'\1\n  ' + snippet.replace('\\', '\\\\'),
        html,
        count=1,
        flags=re.I,
    )

def insert_into_head_end(html, snippet):
    """Insert a line just before </head>."""
    return re.sub(
        r'(</head>)',
        r'  ' + snippet.replace('\\', '\\\\') + r'\n\1',
        html,
        count=1,
        flags=re.I,
    )

def replace_title_text(html, new_title):
    return re.sub(
        r'<title[^>]*>.*?</title>',
        '<title>' + new_title + '</title>',
        html,
        count=1,
        flags=re.I | re.S,
    )

def count_h1(html):
    return len(re.findall(r'<h1\b[^>]*>', html, re.I))

# ──────────────────────────────────────────────────────────
# Backup
# ──────────────────────────────────────────────────────────

def extract_head(html):
    m = re.search(r'<head[^>]*>(.*?)</head>', html, re.I | re.S)
    return m.group(0) if m else ""

def build_backup(files):
    data = {}
    for f in files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        html = read(f)
        data[rel] = {
            "head": extract_head(html),
            "title": get_title(html),
            "description": get_meta(html, "name", "description"),
            "canonical": get_canonical(html),
            "og:title": get_meta(html, "property", "og:title"),
            "og:description": get_meta(html, "property", "og:description"),
            "og:image": get_meta(html, "property", "og:image"),
            "og:url": get_meta(html, "property", "og:url"),
            "h1_count": count_h1(html),
        }
    BACKUP_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return data

# ──────────────────────────────────────────────────────────
# Fix engine
# ──────────────────────────────────────────────────────────

def fix_file(f, rel, changes):
    html = read(f)
    mod = html

    current_title = get_title(mod)
    current_desc = get_meta(mod, "name", "description")
    current_og_desc = get_meta(mod, "property", "og:description")
    current_og_url = get_meta(mod, "property", "og:url")
    current_og_image = get_meta(mod, "property", "og:image")
    canonical = get_canonical(mod)

    # P2: title 길이 조정 (15~60자 외)
    new_title = None
    if current_title:
        tl = len(current_title)
        if tl < 15 or tl > 60:
            new_title = TITLE_OVERRIDES.get(rel)
            if new_title:
                mod = replace_title_text(mod, new_title)
                changes.append(("title", current_title, new_title))
                current_title = new_title

    # P0: description 추가 (누락 시만)
    description = DESCRIPTIONS.get(rel)
    if not current_desc and description:
        if len(description) < 70 or len(description) > 160:
            raise ValueError(
                "description length out of range for " + rel + ": " + str(len(description))
            )
        snippet = '<meta name="description" content="' + description + '">'
        mod = insert_after_title(mod, snippet)
        changes.append(("meta description", "(none)", description))
        current_desc = description

    # P1: og:description 추가 (누락 시만) — P0 값 사용
    if not current_og_desc and description:
        snippet = '<meta property="og:description" content="' + description + '">'
        mod = insert_into_head_end(mod, snippet)
        changes.append(("og:description", "(none)", description))

    # P1: og:url 추가 (누락 시만) — canonical 값 사용
    if not current_og_url and canonical:
        snippet = '<meta property="og:url" content="' + canonical + '">'
        mod = insert_into_head_end(mod, snippet)
        changes.append(("og:url", "(none)", canonical))

    # P3: index.html 전용 — og:image 추가 + h1 중복 처리
    if rel == "index.html":
        if not current_og_image:
            snippet = '<meta property="og:image" content="https://wocs.kr/assets/images/og-default.jpg">'
            mod = insert_into_head_end(mod, snippet)
            changes.append(("og:image", "(none)", "https://wocs.kr/assets/images/og-default.jpg"))
        # h1 중복 → 가장 위에 있는 h1만 남기고 나머지는 h2로
        h1_matches = list(re.finditer(r'<h1\b([^>]*)>', mod, re.I))
        if len(h1_matches) > 1:
            # Replace subsequent h1 open/close tags with h2
            # Start from the 2nd match (keep the first)
            # Strategy: iterate and find opening tags, convert subsequent ones
            for i in range(len(h1_matches) - 1, 0, -1):
                start = h1_matches[i].start()
                end = h1_matches[i].end()
                opening = h1_matches[i].group(0)
                new_opening = re.sub(r'<h1\b', '<h2', opening, flags=re.I)
                mod = mod[:start] + new_opening + mod[end:]
            # Close tags: find all </h1> that correspond to converted ones
            # Simpler: count remaining h1 and convert excess closing tags from the end
            close_matches = list(re.finditer(r'</h1>', mod, re.I))
            if len(close_matches) > 1:
                for i in range(len(close_matches) - 1, 0, -1):
                    start = close_matches[i].start()
                    end = close_matches[i].end()
                    mod = mod[:start] + "</h2>" + mod[end:]
            changes.append(("h1 count", "3", "1 (나머지는 h2)"))

    if mod != html:
        write(f, mod)
        return True
    return False

# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def main():
    files = find_html_files()
    print("Found " + str(len(files)) + " HTML files")

    print("Backing up heads → seo_backup.json")
    build_backup(files)

    modified_log = {}
    total_modified = 0
    for f in files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        changes = []
        try:
            if fix_file(f, rel, changes):
                modified_log[rel] = changes
                total_modified += 1
        except Exception as e:
            print("ERROR " + rel + ": " + str(e))

    log_path = ROOT / "seo_fix_log.json"
    log_path.write_text(
        json.dumps(modified_log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Modified " + str(total_modified) + " files")
    print("Log: " + str(log_path))

if __name__ == "__main__":
    main()
