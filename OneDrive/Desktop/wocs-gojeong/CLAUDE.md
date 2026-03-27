# WOCS 견적 시스템 프로젝트

## 사업자 정보
- **상호:** 우성어닝천막공사캠프시스템 (WOCS)
- **대표:** 김우성
- **사업자번호:** 465-02-03270
- **계좌:** 기업은행 323-077581-01-014 (김우성)
- **전화:** 010-4337-0582
- **주소:** 전남 화순군 사평면 유마로 592
- **사이트:** wocs.kr
- **이메일:** candlejs6@gmail.com

## 프로젝트 개요
전남 화순에서 천막, 어닝, 글램핑 구조물을 직접 시공하는 1인 사업자의 **현장용 자동 견적 시스템**.
핸드폰에서 Streamlit 웹앱으로 접속하여 즉석 견적서를 생성·다운로드할 수 있다.

## 기술 스택
- **언어:** Python
- **프레임워크:** Streamlit (멀티페이지 앱)
- **Excel:** openpyxl (v7 수식 포함 정식 견적서)
- **이미지:** Pillow (견적서 이미지 생성)
- **폰트:** NanumGothic.ttf (코드 내 자동 다운로드 — Streamlit Cloud Linux 한글 깨짐 해결)
- **배포:** Streamlit Community Cloud (GitHub 연결, 24시간 무료 호스팅)
- **저장소:** https://github.com/cryptowoosung/wocs-website-

## 파일 구조
```
app.py                          ← Streamlit 메인 (메뉴 페이지)
pages/
  1_천막_구조물_견적.py           ← 천막 철골 구조물 (test.py 복사)
  2_글램핑_텐트_견적.py           ← 글램핑 텐트 35개 모델 (test1.py 복사)
  3_고정식_어닝_견적.py           ← 고정식 어닝 (appg1.py 복사)
  4_접이식_어닝_견적.py           ← 접이식 어닝 (appp.py 복사)
wocs_catalog.py                 ← 제품 카탈로그 (35개 모델, 4개 카테고리)
make_quotation.py               ← Excel 견적서 원본 (천막+글램핑 통합)
make_quotation_awning.py        ← 천막·어닝 전용 정식 견적서 (build_sheet)
make_quotation_glamping.py      ← 글램핑 전용 정식 견적서 (build_sheet)
logo.png                        ← WOCS 회사 로고
stamp.png                       ← 도장 원본
stamp_clean.png                 ← 도장 (누끼, 투명 배경)
WOCS_견적서_v7.xlsx             ← v7 Excel 템플릿 (수식 참고용)
requirements.txt                ← streamlit, Pillow, openpyxl
```

## 원본 Streamlit 앱 파일 (개발용)
- `test.py` — 천막·구조물 자동 견적 (심플)
- `test1.py` — 글램핑 텐트 자동 견적 (카탈로그 기반)
- `appg1.py` — 고정식 어닝 자동 견적
- `appp.py` — 접이식 어닝 자동 견적
- `appg.py` — 고정어닝 구버전 (로고 업로드 방식)

## 견적 워크플로우
1. **가견적** — test.py/test1.py/appg1.py/appp.py에서 즉시 발행 (이미지+간이Excel)
2. **정식 견적서** — 📋 버튼 → make_quotation_awning/glamping.py → v7 수식 포함 Excel
3. **다운로드 3종** — 💾 이미지(PNG) / 📊 Excel(간이) / 📋 정식 견적서(v7 Excel)

## 제품 카탈로그 (wocs_catalog.py)
- **D-시리즈 돔** (9개): D-800 5~7m, D-600 6~8m, D-Pro 10~15m
- **S-시리즈 사파리** (11개): Classic C15/C18, Suite CB-S/CB-L, Lodge E48/E67/LX, EX A3p/A5p/B5p/F7p
- **Signature 시리즈** (9개): 벨텐트 4~6m, 티피, 코쿤, 세일링, 버드케이지, 피크로지, 큐브캐빈
- **모듈러 시스템** (6개): 유닛 3×6/3×9, 데크, 욕실 S/L, 태양광
- 모든 가격은 2025 웹검색 시장가 기반

## 결제 조건 (전체 통일)
- **계약금 50%:** 계약 체결 시 납부 (입금 완료 후 시공 착수)
- **중도금 30%:** 자재 반입 완료 후 3일 이내 납부
- **잔금 20%:** 공사 완료 후 7일 이내 납부
- **지체상금:** 지체일수 × 계약금액의 1/100 (천재지변·불가항력 제외)
- **하자보증:** 시공 완료일로부터 1년 (과실·개조·소모품·자연열화 제외)

## 정식 견적서 Excel 수식 (v7 동일)
- G열: `=IF(AND(ISNUMBER(E),ISNUMBER(F)),E*F,"")` (공급가)
- H열: `=IF(ISNUMBER(G),INT(G*0.1),"")` (부가세)
- I열: `=IF(ISNUMBER(G),G+H,"")` (합계)
- 합계: `ArrayFormula — SUMPRODUCT(IFERROR(G:G*1,0))` ← openpyxl 3.x 버그 우회 필요 (첫글자 중복)
- 한글금액: `=IF(I="","","일금 "&NUMBERSTRING(I,1)&"원정 (부가세 포함)")`
- 도장: stamp_clean.png 서명란 F열에 삽입

## openpyxl 3.x ArrayFormula 버그 주의
openpyxl 3.1.5에서 ArrayFormula의 텍스트 첫 글자가 잘리는 버그가 있다.
`ArrayFormula('I50', 'SUMPRODUCT(...)')` → XML에서 `UMPRODUCT(...)` 됨.
**우회법:** 첫 글자를 중복: `ArrayFormula('I50', 'S' + 'SUMPRODUCT(...)')`

## Streamlit Cloud 배포 설정
- Repository: `cryptowoosung/wocs-website-`
- Branch: `main`
- Main file: `OneDrive/Desktop/wocs-gojeong/app.py`
- pages/ 폴더의 set_page_config 제거됨
- pages/ 폴더의 __file__ 경로는 상위 폴더 기준으로 수정됨

## 주요 트러블슈팅 히스토리
1. Streamlit Cloud에서 한글 깨짐 → NanumGothic.ttf 자동 다운로드
2. 제품 카탈로그 가격 부정확 → 2025 웹검색 시장가 반영
3. '내풍' 데이터 전체 제거 → GLAMPING_SECTIONS S-Extreme 튜플 3개→4개 수정
4. openpyxl ArrayFormula 첫글자 잘림 → 첫글자 중복 우회
5. Excel 수식 자동 계산 안됨 → forceFullCalc + calcId=0 적용
