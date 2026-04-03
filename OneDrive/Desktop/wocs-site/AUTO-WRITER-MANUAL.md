# WOCS AI 블로그 자동 작성기 — 세팅 매뉴얼

## 전체 구조
```
auto_writer.py 실행 (매일 자동 또는 수동)
  ↓
Gemini AI가 SEO 블로그 글 생성
  ↓ 동시 저장
  ├─ blog-data.js에 새 포스트 추가 (홈페이지 즉시 반영)
  └─ content/ 폴더에 txt 백업 저장
```
비용: **Gemini 1.5 Flash 무료** (하루 1,500회 호출 가능)

---

## STEP 1: Gemini API 키 발급 (2분)

1. https://aistudio.google.com/apikey 접속
2. 구글 계정으로 로그인
3. **Create API Key** 클릭
4. 키가 생성됨 (AIza로 시작하는 긴 문자열)
5. **복사**

---

## STEP 2: API 키 설정 (30초)

### 방법 A: config.json (가장 쉬움)
`wocs-site` 폴더 안의 `config.json` 파일을 메모장으로 열어서:
```json
{
  "gemini_api_key": "AIza여기에복사한키붙여넣기"
}
```
저장.

### 방법 B: 환경변수 (고급)
```
Windows CMD: set GEMINI_API_KEY=AIza어쩌구
Windows PowerShell: $env:GEMINI_API_KEY="AIza어쩌구"
```

---

## STEP 3: 테스트 실행 (1분)

### 주제 선정만 테스트 (API 호출 안 함)
```
cd C:\Users\user\Desktop\wocs-site
python auto_writer.py --dry-run
```
→ "📌 주제: ..." 출력되면 성공

### 실제 글 생성 테스트
```
python auto_writer.py
```
→ 1개 글이 생성되어 blog-data.js + content/ 폴더에 저장됨

### 특정 주제로 지정 생성
```
python auto_writer.py --topic "글램핑 시공 단가"
```

### 한 번에 3개 생성
```
python auto_writer.py --count 3
```

---

## STEP 4: 매일 자동 실행 설정 (택 1)

### 방법 A: 윈도우 작업 스케줄러 (내 컴퓨터)

1. 시작 메뉴 → **작업 스케줄러** 검색 → 열기
2. 우측 **작업 만들기** 클릭
3. **일반** 탭:
   - 이름: `WOCS 블로그 자동 작성`
   - ✅ 사용자의 로그온 여부에 관계없이 실행
4. **트리거** 탭 → **새로 만들기**:
   - 시작: **매일**
   - 시간: **오전 9:00**
5. **동작** 탭 → **새로 만들기**:
   - 프로그램: `python`
   - 인수: `auto_writer.py`
   - 시작 위치: `C:\Users\user\Desktop\wocs-site` (실제 경로)
6. **확인** → 비밀번호 입력

→ 매일 오전 9시에 블로그 글 1개가 자동 생성됩니다.

### 방법 B: GitHub Actions (클라우드, 컴퓨터 꺼도 됨)

1. GitHub에 wocs-site 레포지토리 생성
2. `.github/workflows/blog.yml` 파일 생성:

```yaml
name: WOCS Auto Blog
on:
  schedule:
    - cron: '0 0 * * *'  # 매일 UTC 00:00 (한국 09:00)
  workflow_dispatch:  # 수동 실행 버튼

jobs:
  write:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python auto_writer.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      - run: |
          git config user.name "WOCS Bot"
          git config user.email "bot@wocs.kr"
          git add -A
          git diff --staged --quiet || git commit -m "🤖 자동 블로그 포스트 추가"
          git push
```

3. GitHub 레포 → Settings → Secrets → **GEMINI_API_KEY** 추가
4. Actions 탭에서 수동 실행(Run workflow) 테스트

→ 매일 한국 시간 오전 9시에 자동 실행, 블로그 글 커밋&푸시.

---

## 수동 글과 충돌 없음 — 확인

| 상황 | 결과 |
|------|------|
| auto_writer.py 자동 실행 | blog-data.js 맨 위에 새 글 추가 |
| 내가 blog-data.js를 직접 편집 | 정상 작동 (id만 겹치지 않으면 됨) |
| content/ 폴더에 txt 수동 추가 | auto_writer와 무관, 충돌 없음 |
| auto_writer + 수동 동시 운영 | 완벽 공존 |

auto_writer의 id는 100번부터 시작하고, 기존 수동 포스트는 1~99 범위이므로 **절대 충돌하지 않습니다.**

---

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| "API 키가 설정되지 않았습니다" | config.json 미생성 또는 키 오류 | STEP 2 다시 확인 |
| "API 에러 429" | 무료 한도 초과 (분당 15회) | 1분 후 재시도 |
| "blog-data.js 파일을 찾을 수 없습니다" | 경로 불일치 | auto_writer.py를 wocs-site 폴더에 넣기 |
| 글이 이상하게 생성됨 | AI 할루시네이션 | content/ 폴더의 txt를 검토 후 수정 |
| 한글 깨짐 | 파이썬 인코딩 | `python -X utf8 auto_writer.py` |

---

## 비용 요약

| 항목 | 비용 |
|------|------|
| Gemini 1.5 Flash API | **무료** (하루 1,500회) |
| GitHub Actions | **무료** (월 2,000분) |
| 서버 | **0원** |
| **합계** | **0원/월** |
