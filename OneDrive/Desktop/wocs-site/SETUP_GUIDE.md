# WOCS 이모티콘 자동화 - GitHub Actions 설정 가이드

## 파일 배치

GitHub repo (cryptowoosung/wocs-website-)에 아래 구조로 파일 배치:

```
wocs-website-/
├── .github/
│   └── workflows/
│       └── emoticon.yml        ← 워크플로우 파일
├── emoticon_generator.py       ← 메인 스크립트 (루트에 배치)
└── (기존 파일들...)
```

## GitHub Secrets 설정 (6개)

GitHub repo → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 | 설명 |
|------------|-----|------|
| `OPENAI_API_KEY` | sk-... | OpenAI API 키 (이미 있음) |
| `ANTHROPIC_API_KEY` | sk-ant-... | Anthropic API 키 |
| `TELEGRAM_BOT_TOKEN` | 123456:ABC... | 텔레그램 봇 토큰 (이미 있음) |
| `TELEGRAM_CHAT_ID` | 숫자 | 텔레그램 채팅 ID (이미 있음) |
| `GOOGLE_CREDENTIALS_JSON` | {"type":"service_account",...} | Google 서비스 계정 JSON 전체 |
| `DRIVE_PARENT_FOLDER_ID` | 폴더ID문자열 | WOCS_emoticons 폴더 ID |

## Google 서비스 계정 만드는 법

### 1. 서비스 계정 생성
1. https://console.cloud.google.com 접속
2. 프로젝트 선택 (또는 새로 생성)
3. 좌측 메뉴 → IAM 및 관리자 → 서비스 계정
4. "서비스 계정 만들기" 클릭
5. 이름: `wocs-emoticon` → 만들기
6. 역할: 건너뛰기 (필요 없음)
7. 완료

### 2. JSON 키 발급
1. 생성된 서비스 계정 클릭
2. "키" 탭 → 키 추가 → 새 키 만들기 → JSON
3. 다운로드된 JSON 파일 내용 전체를 GOOGLE_CREDENTIALS_JSON secret에 붙여넣기

### 3. Google API 활성화
1. Google Cloud Console → API 및 서비스 → 라이브러리
2. "Google Sheets API" 검색 → 사용 설정
3. "Google Drive API" 검색 → 사용 설정

### 4. 시트/폴더 공유
1. Google Sheets(WOCS_콘텐츠_로그) → 공유 → 서비스 계정 이메일 추가 (편집자)
2. Google Drive의 WOCS_emoticons 폴더 → 공유 → 서비스 계정 이메일 추가 (편집자)
   - 서비스 계정 이메일: JSON 파일의 "client_email" 값

### 5. WOCS_emoticons 폴더 ID 찾기
- Google Drive에서 WOCS_emoticons 폴더 열기
- 브라우저 URL: `https://drive.google.com/drive/folders/XXXXXX`
- XXXXXX 부분이 폴더 ID → DRIVE_PARENT_FOLDER_ID secret에 입력

## 실행 확인

### 자동 실행
- 매일 한국시간 오전 9시에 자동 실행
- GitHub repo → Actions 탭에서 실행 기록 확인

### 수동 실행 (테스트)
1. GitHub repo → Actions 탭
2. 좌측에서 "WOCS Emoticon Auto Generator" 클릭
3. 우측 "Run workflow" → "Run workflow" 클릭

### 실행 결과 확인
- GitHub Actions 로그에서 단계별 진행 확인
- Google Drive WOCS_emoticons 폴더에 오늘 날짜 폴더 + 32개 이미지
- Google Sheets 이모티콘_캐릭터_로그에 새 행 추가
- Telegram으로 완료 알림 수신

## n8n과의 차이점

| 항목 | n8n Cloud | GitHub Actions |
|------|-----------|---------------|
| RAM | 320MiB (12개에서 크래시) | 7GB (32개 여유) |
| 비용 | $20/월 (Starter) | **$0 (무료)** |
| 실행 횟수 | 2,500회/월 | **2,000분/월 무료** |
| 설정 | 웹 GUI | 코드 (Python) |

## 비용 구조 (GitHub Actions 이동 후)

| 항목 | 월 비용 |
|------|--------|
| GitHub Actions | **$0** |
| GPT Image low × 32개 × 10회 | ~$5~8 |
| Claude Haiku × 10회 | ~$0.01 |
| **합계** | **~$5~8/월** |

기존 n8n Starter $20/월 포함 ~$31/월 → **$5~8/월로 절감**
