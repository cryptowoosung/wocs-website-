# WOCS Vite 마이그레이션 — 핸드오프 (2026-04-20 밤)

> 새 세션에서 이어서 작업할 때 이 파일 통째로 Claude에게 제공할 것

---

## 현재 위치

**작업 경로**: `C:/Users/user/OneDrive/Desktop/wocs-website-production`  
**레포 (프로덕션)**: `cryptowoosung/wocs-website-`  
**작업 브랜치**: `vite-migration`  
**main 브랜치**: 건드리지 않음 (production 보호 중)

## 진행 상황

### ✅ 완료 (Phase 0 ~ Phase 3)

| Phase | 내용 | 결과 |
|------|------|------|
| 0 | 안전 태그 생성, 자동 봇 disable | ✅ 태그: `pre-vite-migration-20260420` |
| 1 | Vite + React 18 환경 구축 | ✅ package.json, vite.config.js, src/main.jsx |
| 2A | index.html의 2,599줄 JSX를 src/App.jsx로 분리 | ✅ |
| 2B | React UMD destructuring 제거, 빌드 성공 | ✅ |
| 2C | inline style 리팩터 | ⏭️ 스킵 (Vite 빌드로 자동 해결됨) |
| 2D | public/ 정션으로 자산 연결 + 누락 스크립트 복원 | ✅ |
| 2D-보강 | vite-plugin-static-copy 도입 (Vercel 빌드 호환) | ✅ |
| 3 | vite-migration 브랜치 push, Vercel Preview 배포 성공 | ✅ |

### Preview URL (Vercel)

```
https://wocs-website-git-vite-migration-candlejs6-7863s-projects.vercel.app
```

## 발견된 이슈 (Phase 8 승격 전 수정 필요)

### 🟠 이슈 1: 로고 클릭 시 랜딩페이지로 안 넘어감

- 상단 좌측 **WOCS 로고** 클릭해도 홈(`/`)으로 이동 안 됨
- 추정 원인: `<a href="/">` 또는 `onClick={() => navigate('/')}` 누락
- 수정 위치: `src/App.jsx` 내 헤더 컴포넌트
- 예상 작업 시간: 5분

### 🟠 이슈 2: 시그니처M 마이크로쉘터 페이지 비치글램핑 이미지 누락

- 페이지 경로: 시그니처M (Sig-M) 관련 페이지
- 비치글램핑(Beach Glamping) 이미지가 안 보임
- 추정 원인: 이미지 파일 경로 오류 또는 `assets/images/`에 해당 파일 자체 없음
- 확인 필요 파일:
  - `assets/images/` 내 beach 또는 sig-m 관련 파일 존재 여부
  - `src/App.jsx` 내 해당 페이지 이미지 경로
- 예상 작업 시간: 10~15분

## 남은 Phase

### Phase 4: 발견된 이슈 2개 수정
- 이슈 1, 2 해결
- vite-migration 브랜치에 커밋 & push
- Vercel Preview 재배포 자동 실행
- 실기 재검증

### Phase 5: 실기 전수 검증 (핸드폰)
- 모바일 햄버거 → 서브메뉴 ✅
- 서브페이지 이동 (제품, 활용분야 등)
- 언어 전환 (15개 언어 샘플 3개)
- 전화/이메일/견적 버튼

### Phase 6: Lighthouse 성능 측정
- Preview URL에서 Performance 점수 측정
- 목표: 26점 → 70점+ 
- 실패 시 추가 최적화

### Phase 7: Production 승격
- GitHub에서 PR 생성: `vite-migration` → `main`
- 또는 직접 merge 후 push
- Vercel이 자동으로 production 배포
- wocs.kr 실제 반영 확인

### Phase 8: 후처리
- 자동 블로그 봇 재활성화 (GitHub Actions)
- `index.html`, `index.html.original` 정리 (또는 `index.html.legacy`로 보관)
- SEO 자동화 시스템에 Vite 빌드 고려

## 복구 방법 (만약 문제 발생 시)

### 즉시 복구 (5분 내)
```bash
# 로컬에서
git checkout main
git reset --hard pre-vite-migration-20260420
git push origin main --force-with-lease
```

### Vercel에서 복구
- Vercel 대시보드 → Deployments
- SHA `3c204c51...` 찾아서 **Promote to Production**

## 핵심 설정

### vite.config.js 요약
- `viteStaticCopy` 플러그인으로 `assets/`, 서브페이지 `products/`, `occasions/` 등 전부 `dist/`에 복사
- `publicDir: false` (정션 방식 X, 플러그인 방식 O)
- 빌드 input: `vite-index.html`

### 주요 파일
- `vite-index.html` — Vite 진입점 (원본 index.html에서 `<head>` 재구성 + `<script type="module" src="/src/main.jsx">`)
- `src/App.jsx` — 원본 JSX 2,599줄 이식
- `src/main.jsx` — 단순 `import './App.jsx'`
- `index.html.original` — 원본 백업 (건드리지 않음)

## 자동 블로그 봇 상태

- **Disabled** (GitHub Actions UI에서 수동 disable 완료)
- 파일 백업: `.github/workflows/auto_blog.yml.bak`
- Phase 7 완료 후 Enable 해야 함

## 다음 세션 시작 멘트

"wocs-website-production 레포에서 Vite 마이그레이션 이어서 하자.
위 핸드오프 파일 읽고, 이슈 2개 (로고 링크, 시그니처M 이미지)부터 수정 진행.
작업 브랜치는 vite-migration. main은 건드리지 말 것."
