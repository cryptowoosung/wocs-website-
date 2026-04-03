# AGENTS.md — WOCS 프로젝트 에이전트 가이드

> 최종 업데이트: 2026-04-02  
> 적용 레포: cryptowoosung/wocs-website-  
> 운영자: 우성 (1인 사업자, 전남 화순)

---

## 프로젝트 개요

**WOCS (우성어닝천막공사캠프시스템)**  
글램핑 구조물 제조·시공, 천막·어닝 시공, OEM 수입 판매 사업.  
핵심 특허: 무용접 다방향 유니버설 조인트 (더블 쐐기 압착 방식).  
운영 철학: 1인 최대 자동화, O4O 쇼룸 모델, 저비용·고마진.

---

## 레포 구조

```
cryptowoosung/wocs-website-/
├── AGENTS.md                          ← 이 파일
├── CLAUDE.md                          ← Claude Code 전용 메모리
├── .github/
│   └── workflows/
│       ├── blog_post.yml              ← 매일 09:00 블로그 자동포스팅
│       ├── linkedin.yml               ← 매일 11:00 LinkedIn
│       └── threads.yml                ← 매일 11:30 Threads
├── OneDrive/Desktop/wocs-gojeong/
│   └── app.py                         ← Streamlit 견적앱 (메인 앱)
└── emoticons/                         ← 이모티콘 생성 파이프라인
    └── emoticon_generator.py          ← 현재 최종: commit f31b7f0
```

---

## 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| 웹사이트 | Next.js + Vercel | wocs.kr |
| CMS | WordPress (Cafe24) | glampingtentgo.com |
| 자동화 | n8n Cloud | wocs.app.n8n.cloud |
| CDN | Cloudinary | Cloud: dd0jjn8bl |
| 영상 생성 | fal.ai (Grok) | grok-imagine-image/video |
| TTS | ElevenLabs | speed 1.5, 8가지 voice |
| 배포 | Upload-Post.com | 11개 플랫폼 |
| 견적앱 | Streamlit | Python, Pillow, openpyxl |
| 로그/DB | Google Sheets | ID: 1OGZplXhNReH5M6rbNHH-ENjA_yJqIhorxSRSi3SYqmg |

---

## 빌드 & 실행 명령

```bash
# wocs.kr 로컬 개발
npm run dev

# Streamlit 견적앱 실행
streamlit run OneDrive/Desktop/wocs-gojeong/app.py

# 이모티콘 생성
python emoticons/emoticon_generator.py

# 이미지 플랫폼별 리사이즈 (Claude Code 변환)
# DATE="2026-04-02" CHARACTER="솜사탕" 로 상단 변수만 변경

# GitHub Actions 수동 트리거
gh workflow run blog_post.yml
gh workflow run linkedin.yml
gh workflow run threads.yml

# 의존성 설치 (Python)
pip install pillow openpyxl streamlit requests --break-system-packages

# 의존성 설치 (Node)
npm install
```

---

## 코드 스타일

- **Python**: PEP8 준수, 변수명에 한글 주석 필수
- **JavaScript/TypeScript**: 단순 유지, 복잡한 추상화 금지
- **n8n JSON**: 직접 편집 금지 — wocs.app.n8n.cloud 에서만 수정
- **커밋 메시지**: 한글로 간결하게 (`견적앱 모델 추가`, `이모티콘 변환 스크립트 수정`)
- **파일 200~400줄 유지**, 최대 800줄 초과 금지

---

## 절대 건드리지 말 것 (NEVER)

```
❌ .env 파일 직접 수정
❌ Cloudinary upload_preset (ml_default) 변경
❌ Google Sheets 헤더 순서 변경 (A~K열 고정)
❌ n8n 워크플로우 JSON 직접 파일 수정
❌ 우성어닝.한국 도메인/사이트 수정 (웹에이전시 관리)
❌ WordPress 관리자 비밀번호 변경
❌ LinkedIn RefreshToken 직접 수정 (만료: 2027-03-22)
❌ WOCS_MASTER Active 토글 ON (테스트 완료 전)
```

---

## 주요 설정값 (읽기 전용 참조)

```
Cloudinary Cloud:       dd0jjn8bl
Cloudinary upload_preset: ml_default
Upload-Post API key:    wocs_n8n
Pinterest Board ID:     805370414554152325
Bluesky:                @wocs83.bsky.social
Instagram:              @woosung_tent
YouTube:                @countrydiy

Google Sheets 헤더:
  A=date / B=topic / C=scene1_image_prompt / D=scene1_video_prompt
  E=scene2_image_prompt / F=scene2_video_prompt
  G=scene3_image_prompt / H=scene3_video_prompt
  I=narration_script / J=posted / K=voice_id
```

---

## 자동화 파이프라인 현황

### WOCS_01 (매일 09:00, 활성)
```
Schedule → Edit Fields → Sheets 읽기 → Claude 주제생성(중복방지)
→ Edit Fields3 v5(장르/훅/텐트 조합) → Claude 대본생성
→ Sheets 기록 → Telegram 알림
```

### WOCS_MASTER (현재 OFF — 테스트 완료 후 ON)
```
Sheets 읽기 → ElevenLabs TTS → 씬1/2/3 이미지생성(fal.ai)
→ 씬1/2/3 영상생성 → FFmpeg 병합(30초) → Cloudinary → 11개 플랫폼 배포
```
**주의**: Execute 1회 수동 테스트 → 30초 영상 확인 → 그 후 Active 토글 ON

### WOCS_UPLOAD (수동)
```
폼 제출 → Cloudinary → Claude 캡션생성(9개 플랫폼) → Upload-Post → Telegram → Sheets
```
**사용법**: "On form submission → Execute Step" 먼저 클릭 → 폼 URL 접근

### 이모티콘 파이프라인 (GitHub Actions, 매일 09:00)
```
Claude Haiku 기획 → GPT Image 32개 생성 → Cloudinary 저장 → Telegram 알림
→ [수동] 다운로드 → Claude Code 변환 → OGQ/라인/카카오 제출
```

---

## 플랫폼 상태 (2026-04-02 기준)

| 플랫폼 | 상태 | 메모 |
|--------|------|------|
| Instagram Reels | ✅ | |
| YouTube Shorts | ✅ | |
| TikTok | ✅ | |
| Threads | ✅ | GitHub Actions 11:30 |
| LinkedIn | ✅ | GitHub Actions 11:00 |
| Pinterest | ✅ | Board: 805370414554152325 |
| Google Business | ✅ | STANDARD 타입, 광고성 문구 금지 |
| Bluesky | ⚠️ | 이메일 인증 필요 |
| X (Twitter) | ❌ | 403 에러, Upload-Post 재연결 필요 |
| Facebook | ❌ | Upload-Post 버그, Disable 유지 |
| Reddit | ⏳ | 카르마 0, 3~5일 후 |

---

## 이모티콘 심사 현황

| 플랫폼 | 캐릭터 | 상태 |
|--------|--------|------|
| 라인 | 초록스카프 곰 | ✅ 승인 완료 |
| OGQ | 초록스카프 곰 v1 | 심사 중 |
| 카카오 | 초록스카프 곰 v5 | 심사 중 |
| 라인 | 거북이 | 심사 중 |
| 카카오 | 거북이 | 심사 중 |
| OGQ/라인/카카오 | 고슴도치 | 제출 완료 |
| OGQ/라인/카카오 | 라면 | 제출 완료 |

---

## 에이전트 배치 가이드 (188개 중 WOCS 업무 매핑)

> Claude Code가 이 파일을 읽고 자동으로 적절한 에이전트를 선택함.
> 명시적으로 지정하려면: "video-pipeline 에이전트로 작업해줘"

### WOCS 커스텀 에이전트 (최우선)
| 에이전트 | 사용 시점 |
|---------|----------|
| `video-pipeline` | WOCS_MASTER 영상 파이프라인 수정/디버깅 |
| `webtoon-creator` | 글램핑 웹툰 콘텐츠 제작 |
| `music-pipeline` | Kie.ai 음악 파이프라인 작업 |
| `newsletter` | Stibee 뉴스레터 콘텐츠 작성 |
| `novel` | 글램핑 스토리/소설 콘텐츠 |
| `trading-bot` | 주식 자동매매 봇 (Freqtrade) |
| `glamping-game` | 글램핑 관련 게임 콘텐츠 |

### 엔지니어링
| 에이전트 | 사용 시점 |
|---------|----------|
| `python-developer` | app.py, emoticon_generator.py 수정 |
| `api-integration-specialist` | n8n HTTP 노드, fal.ai, ElevenLabs 연동 |
| `code-reviewer` | 코드 작성 후 품질 검토 |
| `security-engineer` | API 키 노출 점검, .env 보안 |
| `devops-engineer` | GitHub Actions 워크플로우 수정 |

### 마케팅/콘텐츠
| 에이전트 | 사용 시점 |
|---------|----------|
| `seo-specialist` | glampingtentgo.com SEO, 메타태그, canonical |
| `content-strategist` | 글램핑 블로그 주제 기획 |
| `social-media-strategist` | 플랫폼별 캡션 전략 |
| `marketing-copywriter` | 상세페이지, 제안서, 광고 카피 |

### 세일즈/비즈니스
| 에이전트 | 사용 시점 |
|---------|----------|
| `proposal-writer` | 글램핑 창업 제안서 작성 |
| `deal-closer` | 고객 협상, 견적 마감 전략 |

---

## 나레이션 분량 규칙 (30초 영상)

```
씬1 = 10초 = 약 80자 / 2~3문장
씬2 = 10초 = 약 75자 / 2~3문장 (WOCS 1회 자연 삽입)
씬3 =  8초 = 약 65자 / 2문장 (여운으로 마무리)
전체 = 215~230자 (ElevenLabs speed 1.5 기준 약 28~30초)

WOCS 삽입 예시:
✅ "화순에서 온 WOCS 사람들이 이 땅을 보더니 된다고 했습니다"
✅ "WOCS라는 곳에서 14일 만에 지어줬습니다"
❌ 씬3에서 WOCS 재등장 금지
❌ 광고 문구/전화번호/외부링크 금지
```

---

## 이모티콘 플랫폼별 변환 규격

| 플랫폼 | 크기 | 개수 | 추가파일 | 용량 |
|--------|------|------|---------|------|
| OGQ | 740×640 | 24개 | main 240×240, tab 96×74 | 제한 없음 |
| 라인 | 370×320 | 24개 | main 240×240, tab 96×74 | ZIP 60MB |
| 카카오 | 360×360 | 32개 | icon 78×78 | 150KB/개 |

---

## 월 비용 현황

| 항목 | 월 비용 |
|------|---------|
| n8n Cloud | $20.0 |
| ElevenLabs Starter | $5.0 |
| fal.ai | ~$10.0 |
| Upload-Post Basic | $19.0 |
| 이모티콘 GPT Image | ~$10.6 |
| Cloudinary | $0 (무료) |
| **합계** | **~$64.6/월** |

---

## 우선 처리 대기 작업

1. WOCS_MASTER Execute 1회 → 30초 영상 확인 → Active 토글 ON
2. Bluesky 이메일 인증 (bsky.app)
3. X Twitter 403 에러 → Upload-Post 재연결
4. 솜사탕 캐릭터 Cloudinary 다운 → OGQ/라인/카카오 제출
5. glampingtentgo.com 색인 확인 (4/7)

---

## SEO 확인 일정

- **4/7**: glampingtentgo.com Google 색인 1차 확인
- **4/21**: 2차 확인 및 추가 최적화 판단
- Naver Search Advisor 색인 현황 병행 확인

---

*이 파일은 Claude Code, Cursor, GitHub Copilot, OpenAI Codex 등 모든 AI 코딩 에이전트가 읽습니다.*  
*수정 시 날짜와 변경 내용을 맨 위 업데이트 날짜에 반영해주세요.*
