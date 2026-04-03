# WOCS AI 에이전트 팀 — 프로젝트 메모리

## 🏢 회사 정보
- **회사명**: WOCS (우성어닝천막공사캠프시스템)
- **대표**: 김우성
- **연락처**: 010-4337-0582
- **이메일**: candlejs6@gmail.com / info@wocs.kr
- **주소**: 전남 화순군 사평면 유마로 592
- **웹사이트**: wocs.kr
- **GitHub**: cryptowoosung/wocs-website-

## 🎯 사업 목표
- 1인 사업자의 한계를 AI 자동화로 완전히 극복
- 글램핑 구조물 제조·시공 분야 SEO 1위
- 리드 수집 → 자동 응답 → 견적 → 계약 전 과정 자동화
- 핵심 키워드: "글램핑창업"

## 🤖 AI 에이전트 팀 구성

### 1. SEO 에이전트 (auto_writer.py)
- 매일 오전 9시 블로그 글 자동 생성
- Gemini 2.0 Flash API 사용
- GitHub Actions로 자동 실행 → Vercel 자동 배포
- 주제 20개 로테이션 (글램핑창업, 시공단가 등)

### 2. 리드 에이전트 (wocs-lead-popup.js)
- 팝업 문의폼 → Google Sheets 자동 저장
- contact/index.html 일반문의 → 저장
- contact/quote.html 견적요청 → 저장
- 접수 즉시 candlejs6@gmail.com 이메일 알림

### 3. 데이터 에이전트 (Google Sheets)
- 스프레드시트: WOCS 문의 리드
- 시트1: 일반문의 (접수시간/이름/연락처/문의내용/페이지)
- 시트2: 견적요청 (이름/연락처/회사명/지역/면적/예산/모델 등)
- GAS URL: https://script.google.com/macros/s/AKfycby7cq4Krqif_h0A059Rz4ip0KOJb3uJv8XU8fdHZRknNW-Zsmlsz8C2DQ_oQ2eHideE/exec

### 4. 콘텐츠 에이전트 (예정)
- SNS 자동 포스팅 (Instagram, 네이버 블로그)
- 블로그 글 → SNS 카드뉴스 자동 변환

### 5. 견적 에이전트 (예정)
- 견적 요청 접수 → 자동 견적서 생성 → 이메일 발송
- ROI 계산기 연동

### 6. CS 에이전트 (예정)
- 문의 자동 분류 (견적/AS/일반)
- 1차 자동 응답 이메일 발송

## 📁 프로젝트 구조
```
wocs-site/
├── index.html          # 메인 홈페이지 (React JSX)
├── assets/
│   ├── css/
│   │   └── wocs-common.css    # 전체 공통 스타일
│   ├── js/
│   │   ├── wocs-lead-popup.js # 리드 팝업
│   │   ├── wocs-header.js     # 공통 헤더
│   │   └── wocs-footer.js     # 공통 푸터
│   └── images/                # 이미지 101개
├── contact/
│   ├── index.html      # 일반 문의폼
│   └── quote.html      # 견적 요청폼
├── products/           # 제품 상세 페이지
├── occasions/          # 활용 분야 페이지
├── auto_writer.py      # SEO 블로그 자동 작성
└── .github/
    └── workflows/
        └── auto_blog.yml  # 매일 9시 자동 실행
```

## 🔑 핵심 계정 정보
- **Vercel**: wocs-website-.vercel.app → wocs.kr
- **Google Sheets**: WOCS 문의 리드
- **Gemini API**: GitHub Secret GEMINI_API_KEY
- **이메일 전달**: ImprovMX (info@wocs.kr → candlejs6@gmail.com)

## ⚙️ 개발 규칙
1. 작업 전 반드시 `git pull origin main` 먼저 실행
2. 커밋 메시지: feat(새기능) / fix(버그수정) / style(디자인)
3. 모바일 반응형 필수 확인 (767px 기준)
4. 법적 금지 문구 절대 사용 금지: 태풍/풍속수치/시공기간보장
5. 작업 완료 후 항상 git push origin main

## gstack

Use the `/browse` skill from gstack for ALL web browsing tasks. Never use `mcp__claude-in-chrome__*` tools.

### Available gstack skills
- `/office-hours` — Office hours workflow
- `/plan-ceo-review` — CEO review planning
- `/plan-eng-review` — Engineering review planning
- `/plan-design-review` — Design review planning
- `/design-consultation` — Design consultation
- `/review` — Code review
- `/ship` — Ship code
- `/land-and-deploy` — Land and deploy
- `/canary` — Canary deployment
- `/benchmark` — Performance benchmarking
- `/browse` — Web browsing (use this instead of mcp__claude-in-chrome__*)
- `/qa` — Quality assurance
- `/qa-only` — QA only
- `/design-review` — Design review
- `/setup-browser-cookies` — Browser cookie setup
- `/setup-deploy` — Deploy setup
- `/retro` — Retrospective
- `/investigate` — Investigation
- `/document-release` — Document release
- `/codex` — Codex
- `/cso` — CSO workflow
- `/autoplan` — Auto planning
- `/careful` — Careful mode
- `/freeze` — Freeze deployments
- `/guard` — Guard mode
- `/unfreeze` — Unfreeze deployments
- `/gstack-upgrade` — Upgrade gstack

## 📌 현재 남은 작업
- [ ] 서브페이지 메가메뉴 가로 배치 수정
- [ ] 가비아 환불 (1544-4370)
- [ ] 콘텐츠 에이전트 구축
- [ ] 견적 에이전트 구축
- [ ] CS 자동응답 에이전트 구축

---

# ═══════════════════════════════════════
# WOCS AI 콘텐츠 제국 — 마스터 설정
# 업데이트: 2026년 3월
# ═══════════════════════════════════════

## 🤖 활성화된 커스텀 에이전트 7개

| 에이전트 | 역할 | 핵심 AI |
|---------|------|---------|
| webtoon-creator | 웹툰 5개 언어 | Claude + FLUX + SD |
| video-pipeline-agent | 영상 5개 언어 | Claude + ElevenLabs + Kling |
| music-pipeline-agent | 음악 5개 언어 | Suno v4 + MusicFX |
| newsletter-agent | 뉴스레터 5개 언어 | Gemini + Claude + DeepSeek |
| novel-agent | 소설 5개 언어 | Claude Opus + GPT-4o |
| glamping-game-agent | 글램핑 게임 | Godot 4 + Claude (7월 시작) |
| trading-bot-agent | 트레이딩 3단계 | Freqtrade + Alpaca + KIS API |

## 🌍 5개 언어 전략

| 언어 | 담당 AI | 시장 규모 |
|------|---------|---------|
| 🇰🇷 한국어 | Claude | 5천만명 |
| 🇺🇸 영어 | GPT-4o | 15억명 |
| 🇯🇵 일본어 | GPT-4o | 1.2억명 |
| 🇪🇸 스페인어 | GPT-4o | 5억명 |
| 🇨🇳 중국어 | DeepSeek | 14억명 |

## 💰 수익 채널 전체

### 콘텐츠 수익
- YouTube AdSense (구독 1,000명 목표)
- 네이버 애드포스트 (블로그)
- Google AdSense (wocs.kr + 독립 사이트)
- 카카오 애드핏 (모바일)
- 카카오페이지 유료 회차 (소설/웹툰)
- 네이버시리즈 쿠키 수익
- Kindle KDP 전자책 (영어/일본어/스페인어/중국어)
- Wattpad 유료 스토리
- 小説家になろう 일본어 소설
- Spotify + Apple Music 스트리밍
- YouTube Content ID (음악 패시브 인컴)
- 멜론/지니/벅스 국내 스트리밍
- itch.io 게임 판매 (7월 이후)

### B2B 수익
- 글램핑장 BGM 라이선스 월 구독
- 음악 싱크 라이선싱 (드라마/광고)
- 뉴스레터 스폰서 광고
- WOCS 제품 → 콘텐츠 유입 → 실제 판매

### 트레이딩 수익 (검증 후)
- 1단계: 코인 자동매매 (Freqtrade)
- 2단계: 미국주식 (Alpaca API)
- 3단계: 국내주식 (한국투자증권 API)

## ⚙️ Agent Teams 병렬 실행
```json
설정 완료:
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = 1
CLAUDE_CODE_SUBAGENT_MODEL = claude-sonnet-4-6
```

### 병렬 실행 예시 (이 문장 그대로 Claude Code에 입력)
```
Agent Teams로 다음을 병렬 실행해줘:
- webtoon-creator: 이번 주 에피소드 1화 기획서
- video-pipeline-agent: 오늘의 유튜브 영상 대본
- newsletter-agent: 이번 주 뉴스레터 초안
- novel-agent: 1화 첫 3,000자
```

## 📅 실행 타임라인

### 지금~4월 (피크 시즌 전 — 자동화 구축)
```
Week 1 완료: Agent Teams 활성화 + 에이전트 7개 ✅
Week 2: AI-Content-Studio 설치 + YouTube 채널 개설
Week 3: 첫 영상 10개 업로드 + AdSense 신청
Week 4: 소설 1화 + 뉴스레터 첫 발송
```

### 4월~6월 (피크 시즌 — WOCS 본업 집중)
```
자동화 시스템만 가동
에이전트들이 매일 콘텐츠 자동 생성/배포
우성님은 시공 현장에 집중
```

### 7월~9월 (비수기 — 게임 개발 + 트레이딩)
```
글램핑 게임 Phase 1 개발 (Godot 4)
Freqtrade 백테스트 환경 구축
Alpaca API 미국주식 페이퍼트레이딩
```

### 10월~12월 (수확기)
```
게임 wocs.kr 임베드 + itch.io 출시
트레이딩봇 소액 실거래 시작 (검증 후)
연간 콘텐츠 340곡 + 영상 365개 + 소설 연재 중
```

## 🚨 절대 규칙
1. 트레이딩봇 — 백테스트 없이 실거래 절대 금지
2. 비용 발생 작업 전 반드시 확인
3. 할루시네이션 금지 — 모르면 검색 먼저
4. 피크 시즌(4~6월) — 본업 우선, 자동화만 가동

## 📦 설치된 에이전트 패키지
- agency-agents: 144개 전문 에이전트
- gstack: Garry Tan YC 28개 커맨드 (★45.7k)
- game-studios: 게임 스튜디오 48에이전트 (★3.9k)
- 커스텀 에이전트: 7개 (WOCS 전용)
