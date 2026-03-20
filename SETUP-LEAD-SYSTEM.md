# WOCS 리드 수집 자동화 시스템 설정 가이드

## 시스템 구성도

```
[사용자 브라우저]
    ├─ 팝업 폼 제출 ──→ [GAS 웹앱] ──→ [구글시트 "리드DB"]
    │
    └─ 팝업 폼 제출 ──→ [FastAPI 서버] ──→ [구글시트 "리드DB"]
                                       └──→ [텔레그램 봇 알림]
```

---

## 1. 구글시트 API 설정 (5분)

### 서비스 계정 생성
1. [console.cloud.google.com](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 (이름: "WOCS-Leads")
3. **API 및 서비스 → 라이브러리**에서:
   - `Google Sheets API` 검색 → **사용 설정**
   - `Google Drive API` 검색 → **사용 설정**
4. **API 및 서비스 → 사용자 인증 정보**
   - **사용자 인증 정보 만들기 → 서비스 계정**
   - 서비스 계정 이름: `wocs-leads`
   - 역할: 편집자
5. 생성된 서비스 계정 클릭 → **키** 탭 → **키 추가 → JSON**
6. 다운로드된 파일을 `lead-server/credentials.json`으로 저장

### 구글시트 준비
1. [sheets.google.com](https://sheets.google.com) 에서 새 스프레드시트 생성
2. 이름: `WOCS_리드_DB`
3. Sheet1 헤더 (첫 행):
   ```
   접수시간 | 성함 | 연락처 | 시공지역 | 관심제품 | 유입페이지 | 언어 | 소스
   ```
4. "견적요청" 시트 추가 → 헤더:
   ```
   접수시간 | 이름 | 연락처 | 이메일 | 국가 | 회사 | 시공지역 | 면적 | 예산 | 오픈목표 | 모델 | 메시지 | 유입페이지
   ```
5. 서비스 계정 이메일(credentials.json의 `client_email`)을 시트 **공유 → 편집자**로 추가

---

## 2. 텔레그램 봇 설정 (3분)

1. 텔레그램에서 `@BotFather` 검색
2. `/newbot` 입력 → 봇 이름: `WOCS Lead Bot`
3. 생성된 **HTTP API 토큰** 복사
4. `@userinfobot` 검색 → 메시지 보내기 → 표시되는 **chat_id** 복사
5. `lead-server/main.py`에서:
   ```python
   TELEGRAM_BOT_TOKEN = "복사한_봇_토큰"
   TELEGRAM_CHAT_ID = "복사한_chat_id"
   ```

---

## 3. GAS 웹앱 배포 (5분)

1. [script.google.com](https://script.google.com) 접속
2. **새 프로젝트** 생성
3. `gas-lead-capture.js`의 `/* ... */` 안의 코드를 복사하여 붙여넣기
4. 위에서 만든 구글시트를 연결:
   - **프로젝트 설정** → 스프레드시트 ID 연결
5. **배포 → 새 배포**
   - 유형: 웹 앱
   - 실행 주체: 본인
   - 액세스: 누구나
6. **배포** 클릭 → 생성된 URL 복사
7. `assets/js/wocs-lead-popup.js`에서:
   ```javascript
   const POPUP_GAS_URL = "복사한_GAS_웹앱_URL";
   ```

---

## 4. 백엔드 서버 실행

```bash
cd lead-server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 테스트
```bash
curl -X POST http://localhost:8000/lead \
  -H "Content-Type: application/json" \
  -d '{"name":"테스트","phone":"010-1234-5678","product":"s-series"}'
```

### 프로덕션 배포 옵션
- **Railway.app**: GitHub 연동 → 자동 배포
- **Render.com**: 무료 플랜 사용 가능
- **AWS EC2 / GCP**: 직접 서버 운영

배포 후 URL을 `wocs-lead-popup.js`에 설정:
```javascript
const POPUP_API_URL = "https://your-server.com/lead";
```

---

## 5. 프론트엔드 URL 설정

`assets/js/wocs-lead-popup.js` 파일 상단:
```javascript
const POPUP_GAS_URL = "https://script.google.com/macros/s/xxxx/exec";  // GAS 웹앱 URL
const POPUP_API_URL = "https://your-server.com/lead";                   // 백엔드 API URL
```

---

## 리드 흐름

1. **사용자가 페이지 방문** → 15초 후 또는 스크롤 50% 시 팝업
2. **폼 제출** → GAS + 백엔드 동시 전송
3. **GAS** → 구글시트에 행 추가
4. **백엔드** → 구글시트에 행 추가 + 텔레그램 알림 발송
5. **텔레그램** → 대표 핸드폰으로 즉시 알림
6. **사용자** → 성공 메시지 + 카탈로그 다운로드 링크

---

## 문의
WOCS | 김우성 | 010-4337-0582 | candlejs6@gmail.com
