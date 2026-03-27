"""
WOCS 제품 카탈로그 — 모델·규격·참고가 데이터
═══════════════════════════════════════════════════
test1.py (Streamlit 견적기) 및 make_quotation.py (Excel 견적서) 공용
"""

# ──────────────────────────────────────────────────
# 카테고리 정의
# ──────────────────────────────────────────────────
CATEGORIES = {
    'dome':      'D-시리즈 돔 (지오데식)',
    'safari':    'S-시리즈 사파리 텐트',
    'signature': 'Signature 시리즈',
    'modular':   '모듈러 시스템',
}

# ──────────────────────────────────────────────────
# 제품 카탈로그
# key: 모델 코드
# area: 바닥 면적 (m²) — 자재 산출 기준
# ref_price: 본체 참고가 (프레임+커버+조인트, VAT별도)
# options: 기본 포함 사항
# ──────────────────────────────────────────────────
PRODUCT_CATALOG = {
    # ══════════════════════════════════════════════
    # D-시리즈 돔 (지오데식)
    # ※ ref_price = 본체(프레임+커버+조인트)만, 시공·데크 별도
    # 시장가 참고: 중국FOB 6m≈150만, 중급완제품 6m≈880~1,080만
    #   FDomes(유럽) 7m≈1,400만, WOCS=자체제조+특허 중상위 포지션
    # ══════════════════════════════════════════════
    # ── D-800 (즉시 출하형, PVC 기본) ──
    'D-800-5m': {
        'category': 'dome',
        'name': 'D-800 돔 5m',
        'size': 'Ø5m / H2.8m / 19.6m²',
        'height': 2.8,
        'area': 19.6,
        'capacity': '2인 (커플)',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC 기본',
        'ref_price': 6_800_000,
        'options': ['180° 파노라마', '즉시 출하'],
        'lead_time': '재고 — 1주 출하',
    },
    'D-800-6m': {
        'category': 'dome',
        'name': 'D-800 돔 6m',
        'size': 'Ø6m / H3.3m / 28.3m²',
        'height': 3.3,
        'area': 28.3,
        'capacity': '2~3인',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC 기본',
        'ref_price': 8_500_000,
        'options': ['180° 파노라마', '즉시 출하'],
        'lead_time': '재고 — 1주 출하',
    },
    'D-800-7m': {
        'category': 'dome',
        'name': 'D-800 돔 7m',
        'size': 'Ø7m / H3.8m / 38.5m²',
        'height': 3.8,
        'area': 38.5,
        'capacity': '가족 4인',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC 기본',
        'ref_price': 11_000_000,
        'options': ['180° 파노라마', '즉시 출하'],
        'lead_time': '재고 — 1주 출하',
    },
    # ── D-600 (프리컨피그, 베이윈도+이중단열 포함) ──
    'D-600-6m': {
        'category': 'dome',
        'name': 'D-600 돔 6m (프리컨피그)',
        'size': 'Ø6m / H3.3m / 28.3m²',
        'height': 3.3,
        'area': 28.3,
        'capacity': '2~3인',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC + 베이윈도 + 이중단열',
        'ref_price': 11_500_000,
        'options': ['180° 파노라마 베이윈도', '이중단열 기본', 'ISO·CE·SGS'],
        'lead_time': '2~3주 제작',
    },
    'D-600-7m': {
        'category': 'dome',
        'name': 'D-600 돔 7m (프리컨피그)',
        'size': 'Ø7m / H3.8m / 38.5m²',
        'height': 3.8,
        'area': 38.5,
        'capacity': '가족 4인',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC + 베이윈도 + 이중단열',
        'ref_price': 14_500_000,
        'options': ['180° 파노라마 베이윈도', '이중단열 기본', 'ISO·CE·SGS'],
        'lead_time': '2~3주 제작',
    },
    'D-600-8m': {
        'category': 'dome',
        'name': 'D-600 돔 8m (프리컨피그)',
        'size': 'Ø8m / H4.3m / 50.3m²',
        'height': 4.3,
        'area': 50.3,
        'capacity': '4~6인 (로프트 가능)',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC + 베이윈도 + 이중단열',
        'ref_price': 18_000_000,
        'options': ['180° 파노라마 베이윈도', '이중단열 기본', '로프트(2층) 옵션'],
        'lead_time': '2~3주 제작',
    },
    # ── D-Pro (풀 커스텀) ──
    'D-Pro-10m': {
        'category': 'dome',
        'name': 'D-Pro 돔 10m (커스텀)',
        'size': 'Ø10m / H5.5m / 78.5m²',
        'height': 5.5,
        'area': 78.5,
        'capacity': '리조트 스위트',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC / 투명 / PVDF 선택',
        'ref_price': 28_000_000,
        'options': ['풀 커스텀', '4겹 버블단열 옵션'],
        'lead_time': '4~6주 제작',
    },
    'D-Pro-12m': {
        'category': 'dome',
        'name': 'D-Pro 돔 12m (커스텀)',
        'size': 'Ø12m / H6.5m / 113m²',
        'height': 6.5,
        'area': 113.0,
        'capacity': '대형 이벤트',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC / 투명 / PVDF 선택',
        'ref_price': 42_000_000,
        'options': ['풀 커스텀', '4겹 버블단열 옵션'],
        'lead_time': '4~6주 제작',
    },
    'D-Pro-15m': {
        'category': 'dome',
        'name': 'D-Pro 돔 15m 메가 (커스텀)',
        'size': 'Ø15m / H8.0m / 177m²',
        'height': 8.0,
        'area': 177.0,
        'capacity': '2층 로프트 가능',
        'frame': '아연도금 스틸 + 무용접 조인트',
        'cover': 'PVC / 투명 / PVDF 선택',
        'ref_price': 65_000_000,
        'options': ['풀 커스텀', '2층 로프트', '4겹 버블단열'],
        'lead_time': '6~8주 제작',
    },

    # ══════════════════════════════════════════════
    # S-시리즈 사파리 텐트
    # ※ 시장가 참고: 소형(~15m²) 본체 500~800만
    #   중형(24~30m²) 850~1,350만, 대형(40~55m²) 1,350~2,200만
    #   극한형(T5알루미늄) +30~50% 프리미엄
    # ══════════════════════════════════════════════
    # ── S-Classic (기본형) ──
    'S-Classic-C15': {
        'category': 'safari',
        'name': 'S-Classic C15',
        'size': '3.3×4.0×H2.6m / 13.2m²',
        'height': 2.6,
        'area': 13.2,
        'capacity': '1~2인',
        'frame': '스틸 프레임',
        'cover': '750g PVC 방수포 (UV/방염)',
        'ref_price': 4_800_000,
        'options': ['PU 5000mm 코팅', '방염 CA117', 'Qcell 조립'],
        'lead_time': '2~3주',
    },
    'S-Classic-C18': {
        'category': 'safari',
        'name': 'S-Classic C18',
        'size': '3.3×3.3×H3.1m / 10.9m²',
        'height': 3.1,
        'area': 10.9,
        'capacity': '1~2인',
        'frame': '스틸 프레임',
        'cover': '750g PVC 방수포 (UV/방염)',
        'ref_price': 4_200_000,
        'options': ['PU 5000mm 코팅', '방염 CA117', 'Qcell 조립'],
        'lead_time': '2~3주',
    },
    # ── S-Suite / Cabin (강철 프레임) ──
    'S-Suite-CBS': {
        'category': 'safari',
        'name': 'S-Suite CB-S (캐빈)',
        'size': '4.0×6.0×H3.5m / 24m²',
        'height': 3.5,
        'area': 24.0,
        'capacity': '2~4인',
        'frame': 'Q235B 강철 프레임',
        'cover': '690g/m² PVC 방수포',
        'ref_price': 9_500_000,
        'options': ['270° 파노라마 윈도'],
        'lead_time': '3~4주',
    },
    'S-Suite-CBL': {
        'category': 'safari',
        'name': 'S-Suite CB-L (캐빈 대형)',
        'size': '6.0×9.0×H4.0m / 54m²',
        'height': 4.0,
        'area': 54.0,
        'capacity': '4~6인',
        'frame': 'Q235B 강철 프레임',
        'cover': '690g/m² PVC 방수포',
        'ref_price': 16_500_000,
        'options': ['270° 파노라마 윈도'],
        'lead_time': '3~4주',
    },
    # ── S-Lodge / Elite (프리미엄) ──
    'S-Lodge-E48': {
        'category': 'safari',
        'name': 'S-Lodge E48 (엘리트)',
        'size': '4.0×8.0×H4.0m / 32m²',
        'height': 4.0,
        'area': 32.0,
        'capacity': '4~6인',
        'frame': '프리미엄 스틸',
        'cover': '고급 방수캔버스',
        'ref_price': 15_000_000,
        'options': ['다층 방음단열', '부티크 마감'],
        'lead_time': '3~4주',
    },
    'S-Lodge-E67': {
        'category': 'safari',
        'name': 'S-Lodge E67 (엘리트)',
        'size': '6.0×7.0×H4.2m / 42m²',
        'height': 4.2,
        'area': 42.0,
        'capacity': '4~6인',
        'frame': '프리미엄 스틸',
        'cover': '고급 방수캔버스',
        'ref_price': 19_000_000,
        'options': ['다층 방음단열', '부티크 마감'],
        'lead_time': '3~4주',
    },
    # ── S-Lodge LX (럭셔리 빌라) ──
    'S-Lodge-LX': {
        'category': 'safari',
        'name': 'S-Lodge LX-Villa (럭셔리)',
        'size': '8.0×12.0×H4.5m / 96m²',
        'height': 4.5,
        'area': 96.0,
        'capacity': '4~8인 빌라',
        'frame': '프리미엄 프레임',
        'cover': '풀 글라스월 + 캔버스',
        'ref_price': 48_000_000,
        'options': ['자립형 빌라', '풀 글라스월', '독립 모듈러 욕실'],
        'lead_time': '6~8주',
    },
    # ── S-Classic EX (극한기후, T5 알루미늄) ──
    'S-EX-A3p': {
        'category': 'safari',
        'name': 'S-Classic EX A3p (극한)',
        'size': '3.2×4.8×H3.2m / 15.4m²',
        'height': 3.2,
        'area': 15.4,
        'capacity': '1~2인',
        'frame': 'T5 알루미늄 합금',
        'cover': '내후성 PVC (이중 방풍)',
        'ref_price': 7_800_000,
        'options': ['적설 0.3kN/m²', '4계절'],
        'lead_time': '4~6주',
    },
    'S-EX-A5p': {
        'category': 'safari',
        'name': 'S-Classic EX A5p (극한)',
        'size': '4.0×5.6×H3.5m / 22.4m²',
        'height': 3.5,
        'area': 22.4,
        'capacity': '2~3인',
        'frame': 'T5 알루미늄 합금',
        'cover': '내후성 PVC (이중 방풍)',
        'ref_price': 11_000_000,
        'options': ['적설 0.3kN/m²', '4계절'],
        'lead_time': '4~6주',
    },
    'S-EX-B5p': {
        'category': 'safari',
        'name': 'S-Classic EX B5p (극한)',
        'size': '4.8×6.0×H3.8m / 28.8m²',
        'height': 3.8,
        'area': 28.8,
        'capacity': '2~4인',
        'frame': 'T5 알루미늄 합금',
        'cover': '내후성 PVC (이중 방풍)',
        'ref_price': 14_500_000,
        'options': ['적설 0.3kN/m²', '4계절'],
        'lead_time': '4~6주',
    },
    'S-EX-F7p': {
        'category': 'safari',
        'name': 'S-Classic EX F7p (극한 대형)',
        'size': '7.2×10.8×H4.5m / 77.8m²',
        'height': 4.5,
        'area': 77.8,
        'capacity': '4~7인',
        'frame': 'T5 알루미늄 합금',
        'cover': '내후성 PVC (이중 방풍)',
        'ref_price': 35_000_000,
        'options': ['적설 0.3kN/m²', '4계절'],
        'lead_time': '4~6주',
    },

    # ══════════════════════════════════════════════
    # Signature 시리즈
    # ※ 시장가 참고 (2025 웹조사):
    #   벨텐트: 소매 4m=$1,360(188만), 5m=$1,590(220만), 6m≈250만+
    #     → WOCS 금속프레임+480g캔버스+욕실 포함 글램핑 사양 = 소매의 2~3배
    #   티피: FOB $80~125/m² → 28m²≈310~485만, WOCS 알루미늄+특허 프리미엄
    #   코쿤: TENTSXPERT Standard급 $3,200~7,000(440~970만), 6063T6 알루미늄
    #   세일링/에이펙스: 950g PVDF 고급원단, 알루미늄, $5,000~10,000급
    #   버드케이지: 알루미늄 오픈프레임 특수구조, $8,000~15,000급
    #   피크로지/헥사: 에어로스페이스급 알루미늄 24~42m², $7,000~15,000급
    #   큐브캐빈: 프리팹 모듈러 50m², 미국소매 $25,000~30,000, FOB $8,000~15,000
    #   STROHBOID(오스트리아 프리미엄) 시작가 $23,300(3,220만)
    # ══════════════════════════════════════════════
    # ── Sig-M 마이크로 쉘터 (벨텐트) ──
    'Sig-M-4m': {
        'category': 'signature',
        'name': 'Signature-M 벨텐트 4m',
        'size': 'Ø4m / H2.5m 원형',
        'height': 2.5,
        'area': 12.6,
        'capacity': '2인',
        'frame': '센터폴 + 알루미늄',
        'cover': '캔버스 350g',
        'ref_price': 2_800_000,
        'options': ['간편 설치 (수 시간)', '넉넉한 헤드룸'],
        'lead_time': '1~2주',
    },
    'Sig-M-5m': {
        'category': 'signature',
        'name': 'Signature-M 벨텐트 5m',
        'size': 'Ø5m / H3.0m 원형',
        'height': 3.0,
        'area': 19.6,
        'capacity': '2~3인',
        'frame': '센터폴 + 알루미늄',
        'cover': '캔버스 350g',
        'ref_price': 3_800_000,
        'options': ['간편 설치 (수 시간)', '넉넉한 헤드룸'],
        'lead_time': '1~2주',
    },
    'Sig-M-6m': {
        'category': 'signature',
        'name': 'Signature-M 벨텐트 6m',
        'size': 'Ø6m / H3.5m 원형',
        'height': 3.5,
        'area': 28.3,
        'capacity': '3~4인',
        'frame': '센터폴 + 알루미늄',
        'cover': '캔버스 350g',
        'ref_price': 4_800_000,
        'options': ['간편 설치 (수 시간)', '넉넉한 헤드룸'],
        'lead_time': '1~2주',
    },
    # ── Sig-T 트라이앵글 독채 (노르딕 티피) ──
    'Sig-T': {
        'category': 'signature',
        'name': 'Signature-T 노르딕티피',
        'size': 'Ø6.0m×H4.0m 원뿔형 / 28m²',
        'height': 4.0,
        'area': 28.0,
        'capacity': '2~6인',
        'frame': '알루미늄 합금',
        'cover': '캔버스 + PVC',
        'ref_price': 7_500_000,
        'options': ['캐노피 슬리브 (특허)', '시공 2~3일'],
        'lead_time': '2~3주',
    },
    # ── Sig-O 오벌 스위트 (코쿤하우스) ──
    'Sig-O': {
        'category': 'signature',
        'name': 'Signature-O 코쿤하우스',
        'size': '5.0×3.0×H3.0m 오벌형 / 15m²',
        'height': 3.0,
        'area': 15.0,
        'capacity': '1~2인 독채',
        'frame': '6063 T6 알루미늄',
        'cover': 'PVC / PVDF',
        'ref_price': 8_500_000,
        'options': ['60° 파노라마', '시공 1~2일'],
        'lead_time': '2~3주',
    },
    # ── Sig-A 에이펙스 로지 (세일링텐트) ──
    'Sig-A': {
        'category': 'signature',
        'name': 'Signature-A 세일링텐트',
        'size': '5.0×8.0×H4.5m 에이펙스형 / 25m²',
        'height': 4.5,
        'area': 25.0,
        'capacity': '2~4인',
        'frame': '알루미늄 합금',
        'cover': '950g PVDF',
        'ref_price': 12_000_000,
        'options': ['높은 천장', '이중단열', '시공 2~3일'],
        'lead_time': '2~3주',
    },
    # ── Sig-P 파노라마 파빌리온 (버드케이지) ──
    'Sig-P': {
        'category': 'signature',
        'name': 'Signature-P 버드케이지',
        'size': 'Ø6.0m×H3.5m 파빌리온 / 30m²',
        'height': 3.5,
        'area': 30.0,
        'capacity': '2~4인 / 라운지',
        'frame': '알루미늄 합금 오픈프레임',
        'cover': 'PVC + 캔버스',
        'ref_price': 15_000_000,
        'options': ['360° 개방 구조', '시공 3~5일'],
        'lead_time': '3~4주',
    },
    # ── Sig-H 헥사 라운지 (피크로지) ──
    'Sig-H': {
        'category': 'signature',
        'name': 'Signature-H 피크로지',
        'size': '변4.0m 육각×H4.5m / 42m²',
        'height': 4.5,
        'area': 42.0,
        'capacity': '4~8인',
        'frame': '알루미늄 합금',
        'cover': 'PVC / PVDF',
        'ref_price': 19_000_000,
        'options': ['칼럼 없는 100% 공간', '시공 3~7일'],
        'lead_time': '3~4주',
    },
    # ── Sig-Q 큐브 모듈 (큐브캐빈) ──
    'Sig-Q': {
        'category': 'signature',
        'name': 'Signature-Q 큐브캐빈',
        'size': '6.0×9.0×H3.0m 큐브 / 54m²',
        'height': 3.0,
        'area': 54.0,
        'capacity': '2~4인',
        'frame': '스틸 + 패널',
        'cover': '샌드위치 패널 (EPS 50mm)',
        'ref_price': 22_000_000,
        'options': ['모듈러 조립', '시공 2~3일'],
        'lead_time': '3~4주',
    },

    # ══════════════════════════════════════════════
    # 모듈러 시스템
    # ※ 시장가 참고: 데크 15~20만/m², 모듈러욕실 300~700만
    #   모듈러유닛(컨테이너형) 평당 300~450만
    # ══════════════════════════════════════════════
    'MOD-Unit-S': {
        'category': 'modular',
        'name': '모듈러 유닛 3×6m',
        'size': '3m×6m×H2.8m / 18m²',
        'height': 2.8,
        'area': 18.0,
        'capacity': '리셉션/라운지/스태프룸',
        'frame': '아연도금 스틸 프레임',
        'cover': '샌드위치 패널 50mm',
        'ref_price': 12_000_000,
        'options': ['EPS/우레탄 단열', '시공 2~3일'],
        'lead_time': '2~3주',
    },
    'MOD-Unit-L': {
        'category': 'modular',
        'name': '모듈러 유닛 3×9m',
        'size': '3m×9m×H2.8m / 27m²',
        'height': 2.8,
        'area': 27.0,
        'capacity': '레스토랑/라운지',
        'frame': '아연도금 스틸 프레임',
        'cover': '샌드위치 패널 50mm',
        'ref_price': 16_000_000,
        'options': ['EPS/우레탄 단열', '시공 2~3일'],
        'lead_time': '2~3주',
    },
    'MOD-Deck': {
        'category': 'modular',
        'name': '모듈러 데크 (높이조절)',
        'size': '3m×3m 모듈 / H0.2~0.6m',
        'height': 0.6,
        'area': 9.0,
        'capacity': '-',
        'frame': '방부목 / WPC',
        'cover': '-',
        'ref_price': 1_350_000,
        'options': ['200~600mm 높이조절', '500kg/m² 하중', '시공 1일'],
        'lead_time': '1~2주',
    },
    'MOD-Bath-S': {
        'category': 'modular',
        'name': '모듈러 욕실 2×2.5m',
        'size': '2m×2.5m×H2.4m / 5m²',
        'height': 2.4,
        'area': 5.0,
        'capacity': '-',
        'frame': '조립식',
        'cover': '-',
        'ref_price': 4_500_000,
        'options': ['레인샤워+양변기+세면대', '전기온수기 내장', '시공 반나절'],
        'lead_time': '2~3주',
    },
    'MOD-Bath-L': {
        'category': 'modular',
        'name': '모듈러 욕실 2×3m',
        'size': '2m×3m×H2.4m / 6m²',
        'height': 2.4,
        'area': 6.0,
        'capacity': '-',
        'frame': '조립식',
        'cover': '-',
        'ref_price': 5_500_000,
        'options': ['레인샤워+양변기+세면대', '전기온수기 내장', '시공 반나절'],
        'lead_time': '2~3주',
    },
    'MOD-Solar': {
        'category': 'modular',
        'name': '태양광 시스템',
        'size': '3~10kW',
        'height': 0,
        'area': 0,
        'capacity': '1~5동 커버',
        'frame': '-',
        'cover': '-',
        'ref_price': 6_500_000,
        'options': ['독립 전원'],
        'lead_time': '2~4주',
    },
}

# ──────────────────────────────────────────────────
# 부대비용 기본 단가 (m² 또는 식 기준)
# ──────────────────────────────────────────────────
ADDON_DEFAULTS = {
    # ══════════════════════════════════════════════
    # 부대비용 기본 단가 — 2025년 시장조사 기반
    # ══════════════════════════════════════════════
    # ※ 데크: Soomgo 평균 469,159원/건, Miso 평당 13~20만
    #   → 방부목 m² 재료비 ~10만 + 기초 ~3.5만 + 방수 ~2만 = 약 15.5만/m²
    'deck_per_m2':      100_000,   # 방부목 데크 재료비 m² (방부목 20×120 @7,150/장 기준)
    'foundation_per_m2': 35_000,   # 기초 블록·합성목·말뚝 m²
    'waterproof_per_m2': 20_000,   # 바닥 우레탄 방수 2회 m² (시장가 2~10만 하단)
    # ※ 전기: 글램핑 1동 기본 전기공사 40~80만 (2017→인플레 반영)
    #   LED 조명+분전반+콘센트+인입분담금 포함
    'electric':         750_000,   # 전기 인입+분전반+LED조명+콘센트 (1동 일식)
    # ※ 냉난방: 캐리어 인버터 벽걸이 기본설치 포함 83~91만원 (2025 하이마트)
    #   → 글램핑은 배관 연장+앵글 추가 고려
    'aircon':           950_000,   # 인버터 냉난방기 1대 (설치+배관 연장 포함)
    # ※ 온수기: Soomgo 평균 25만, 경동나비엔 50L 설치비 포함 ~35만
    'hotwater':         350_000,   # 전기온수기 50L 1대 (설치비 포함)
    # ※ 울타리: 우드펜스 m당 5~12만, 대나무 3~8만 (자재+시공)
    'fence_per_m':       65_000,   # 프라이빗 울타리 m당 (우드/대나무 시공 포함)
    # ※ 인테리어: 글램핑 침실 기본세트 (퀸침대+사이드테이블+의자+러그+조명)
    #   IKEA 기준 퀸침대 40~80만+매트리스 30~50만+소품 20~30만
    'interior_set':     800_000,   # 침실 패키지 1동 (침대+매트리스+테이블+의자+러그)
    # ※ 단열: 우레탄 뿜칠 m² 2~10만, 글램핑 이중단열(내외 이너막) 1동 기준
    #   Soomgo 평균 130만/건, 텐트 이중단열은 커버+이너 구조
    'insulation':       450_000,   # 이중단열 시스템 1동 (이너막+단열층)
    # ── 시공비 ──
    'labor_install':  1_200_000,   # 텐트 설치 인건비 (2인 1팀, 2~3일, 1동)
    'labor_deck':       650_000,   # 데크 시공 인건비 (1동 분)
    'transport':        400_000,   # 운반비 (전국 직시공)
    'survey':           150_000,   # 현장 답사·실측
    'misc':             150_000,   # 공과잡비·소모품
}


def get_product(code: str) -> dict:
    """모델 코드로 제품 정보 조회"""
    return PRODUCT_CATALOG.get(code, {})


def get_models_by_category(cat: str) -> dict:
    """카테고리별 모델 목록 반환"""
    return {k: v for k, v in PRODUCT_CATALOG.items() if v['category'] == cat}


def estimate_total(code: str, qty: int = 1,
                   include_deck: bool = True,
                   include_electric: bool = True,
                   include_aircon: bool = False) -> dict:
    """
    간편 견적 산출 (참고용)
    반환: {'본체': int, '데크': int, '설비': int, '시공': int, '공급가': int, 'VAT': int, '총액': int}
    """
    p = PRODUCT_CATALOG.get(code)
    if not p:
        return {}

    body = p['ref_price'] * qty
    area = p['area'] * qty

    deck = 0
    if include_deck and area > 0:
        deck = int(area * (ADDON_DEFAULTS['deck_per_m2']
                           + ADDON_DEFAULTS['foundation_per_m2']
                           + ADDON_DEFAULTS['waterproof_per_m2']))

    equip = 0
    if include_electric:
        equip += ADDON_DEFAULTS['electric'] * qty
    if include_aircon:
        equip += ADDON_DEFAULTS['aircon'] * qty

    labor = (ADDON_DEFAULTS['labor_install'] * qty
             + (ADDON_DEFAULTS['labor_deck'] if include_deck else 0)
             + ADDON_DEFAULTS['transport']
             + ADDON_DEFAULTS['survey']
             + ADDON_DEFAULTS['misc'])

    supply = body + deck + equip + labor
    vat = int(supply * 0.1)

    return {
        '본체': body,
        '데크': deck,
        '설비': equip,
        '시공': labor,
        '공급가': supply,
        'VAT': vat,
        '총액': supply + vat,
    }
