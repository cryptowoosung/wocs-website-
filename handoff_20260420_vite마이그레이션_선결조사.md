# Vite 마이그레이션 선결 조사 — 2026-04-20

> 대상: `cryptowoosung/wocs-website-` (진짜 프로덕션 레포)
> 로컬 경로: `C:/Users/user/OneDrive/Desktop/wocs-website-production`
> 조사 성격: read-only. 수정/커밋/푸시 없음.

---

## 수집 데이터 10개 항목 표

| # | 항목 | 값 | 난이도 영향 |
|---|------|-----|------------|
| 1 | index.html 총 줄수 | **2,811줄** | 단일 파일 거대 → 컴포넌트 분할 필요 |
| 2 | text/babel 블록 줄수 | **2,599줄** (92%) | JSX 분리 작업량 매우 큼 |
| 3 | 전체 HTML 페이지 수 | **151개** (OneDrive 중첩 포함, 실제 고유는 ~130개) | Vite는 index.html만 빌드, 나머지 정적 유지 → 경로 처리 필요 |
| 4 | 서브페이지 Babel 의존 여부 | **No** (products/about/contact 모두 babel 0건) | ✅ 서브페이지는 건드릴 필요 없음 (크게 완화) |
| 5 | className 사용 개수 | **29개** | CSS 연결 작업 적음 (good) |
| 6 | inline gridTemplateColumns 개수 | **18개** | 🔴 모바일 반응형 작업량 많음 (CSS 오버라이드 충돌 전례) |
| 7 | 번역 시스템 위치 | `assets/js/wocs-i18n.js` (client-side JS) | 런타임 처리 → Vite 번들링에 특별 대응 불필요 |
| 8 | 자동 블로그 봇 위치 | **GitHub Actions** (`.github/workflows/auto_blog.yml` + `auto_writer.py`) | 매일 04:55 UTC push. 마이그레이션과 경쟁 가능 |
| 9 | 자동 봇이 수정하는 파일 | `assets/js/blog-data.js`, `content/auto_post_*.html`, `cta_counter.json`, `sitemap.xml` | ✅ **`index.html` 미수정** — 충돌 위험 낮음 |
| 10 | package.json scripts 필드 | **package.json 자체 없음** | Vite를 net-new로 추가 가능 (제약 없음) |

---

## 추가 수집 사실 (raw evidence)

### A. JSX 블록 내부 — 모바일 햄버거 실패 재발 지점
```
1707:  <nav className={`nav-list ${mobileOpen ? "mobile-open" : ""}`}>
1739:    position: mobileOpen ? "static" : "absolute",
1740:    top: mobileOpen ? "auto" : "100%",
1741:    left: mobileOpen ? "auto" : "50%",
1742:    transform: mobileOpen ? "none" : "translateX(-50%)",
```
→ React inline style이 `.nav-list.mobile-open` CSS 룰을 오버라이드. **"지난 실패 원인"** 구조 그대로 남아있음.

### B. wocs-common.css (814줄) 관련 룰 이미 작성돼 있음
```
63:  .nav-list { display: flex; gap: 0; align-items: center; list-style: none; }
171: @media { .nav-list { display: none; } }
185: #mobile-hamburger { display: none !important; }
187: @media { #mobile-hamburger { display: block !important; } }
525: .nav-list { display: none !important; }
526: .nav-list.mobile-open { ... }
541-547: .nav-list.mobile-open > div, > li, button, a { ... }
```
→ CSS 쪽은 **이미 설계됨**. JSX inline style이 우회하는 게 문제.

### C. 서브페이지 공통 구조
`products/index.html`, `about/index.html`, `contact/index.html` 모두 동일 패턴:
```html
<script>var WOCS_BASE="../";</script>
<script src="../assets/js/wocs-i18n.js"></script>
<script src="../assets/js/wocs-header.js"></script>   ← 헤더 inject 전담
<script src="../assets/js/wocs-footer.js"></script>
<script src="../assets/js/wocs-leads.js"></script>
<script src="../assets/js/wocs-lead-popup.js"></script>
```
- JSX 없음, Babel 없음, React 없음
- **순수 정적 HTML + bare JS 인젝션** 구조
- Vite 마이그레이션은 **index.html 한 파일만** 대상으로 좁혀짐

### D. 자동 봇 패턴 (최근 5개 커밋)
```
3c204c5  2026-04-20  assets/js/blog-data.js | content/auto_post_2026-04-20.html | cta_counter.json | sitemap.xml
20e5599  2026-04-19  동일 4개 파일
2b270e8  2026-04-18  동일 4개 파일
6556818  2026-04-17  동일 4개 파일
ddda241  2026-04-16  동일 4개 파일
```
→ 봇은 **index.html을 전혀 건드리지 않음**. 마이그레이션 중 bot push → index.html merge 충돌 **발생 안 함**.

### E. GHA workflows 4개
```
.github/workflows/auto_blog.yml          (매일 04:55 UTC 블로그 생성)
.github/workflows/emoticon.yml           (이모티콘 생성)
.github/workflows/indexnow.yml           (SEO ping)
.github/workflows/wordpress-auto-post.yml (워드프레스 크로스포스트)
```

### F. 빌드 설정 상태
- `package.json`: 존재하지 않음
- `vercel.json`: 존재하지 않음
- Vercel은 **repo 파일을 그대로 정적 서빙** 중
- → Vite 도입 시 `vercel.json`에 `buildCommand` 명시하면 빌드 모드 전환 가능

### G. 번역 빌드 도구
`./OneDrive/Desktop/wocs-site/translate_all.py` — 이 경로는 repo에 사용자 OneDrive 경로가 **실수로 중첩 커밋**된 것. canonical 위치에는 없음. 실제 i18n은 client-side `wocs-i18n.js`만으로 동작하는 것으로 보임.

---

## 최종 판단 (사실 기반)

### 예상 작업 시간: **8-12시간**

세부 내역:
| 단계 | 시간 |
|------|------|
| Vite 설정 + package.json 생성 | 1h |
| JSX 2,599줄을 컴포넌트 파일로 분리 (Header, Nav, MobileMenu, HeroSection, ProductGrid, Footer 등) | 4-6h |
| 18개 inline gridTemplateColumns + 4개 nav inline position/top/left/transform → CSS 클래스로 이전 | 2h |
| mobile hamburger CSS/JS 재정합 + 테스트 | 1h |
| Vercel `buildCommand` 설정 + preview deploy 검증 | 0.5h |
| 151개 서브페이지 경로(`../assets/...`) 이상무 확인 | 1h |
| GHA 봇 경로 충돌 확인 (blog-data.js가 Vite bundle에 편입되면 문제) | 0.5h |

**단축 가능 조건**: JSX 구조가 상대적으로 단순(className 29개)하면 6-8h.
**연장 리스크**: CSS override 충돌 수습 지연 시 +4h.

### 난이도: **어려움**

근거 3가지:
1. **2,599줄 JSX를 단일 block으로 유지 중** — 모듈화 자체가 거대 작업
2. **18개 inline gridTemplateColumns** — 모바일 반응형에서 CSS와 경쟁. 지난 햄버거 실패의 직접 원인
3. **151개 서브페이지와 혼합 배포** — Vite는 index.html만, 나머지는 정적. 자산 경로 이중 구조 관리 필요

### 주요 리스크 3가지

1. **[🔴 HIGH] Inline style vs CSS 충돌 재발**
   - 현재 `position/top/left/transform`에 JSX inline style이 남아있음 (1739-1742줄)
   - 이미 wocs-common.css에 대응 룰 작성돼 있으나 inline이 우선순위 더 높음
   - 마이그레이션 중 inline 제거 + CSS class 적용을 정확히 하지 못하면 햄버거/메가메뉴 다시 깨짐

2. **[🟡 MID] 서브페이지 자산 경로 이중 관리**
   - index.html 을 Vite 빌드 시 자산이 `/assets/-hash/...` 등으로 이동
   - 151개 서브페이지는 여전히 `../assets/js/wocs-header.js` 하드코딩 참조
   - Vite의 output 구조에서 `assets/js/wocs-header.js`를 정확히 같은 경로로 유지하려면 `build.rollupOptions.output`을 명시 설정 필요. 실수 시 **서브페이지 전체가 헤더 잃어버림**

3. **[🟡 MID] 자동 봇 파일 경로 변경 리스크**
   - GHA `auto_blog.yml`이 `assets/js/blog-data.js`를 직접 수정
   - Vite가 이 파일을 번들에 포함시키거나 hash 접미사를 붙이면 봇이 잘못된 경로에 write
   - → `assets/js/blog-data.js`를 `publicDir`로 빼서 **Vite가 건드리지 않게** 설정 필요

### 피크시즌 중 진행 권장 여부: **조건부**

글램핑 업은 4-5월 성수기 준비 + 6-9월 피크. 현재 4월 20일 → **프리피크 램프업 구간**.

**권장 조건**:
- ✅ **Vercel preview deploy 필수** (feature branch → preview URL 생성 → 실기기 테스트 → 이상무 확인 후 merge)
- ✅ **롤백 플랜 준비**: 기존 main 브랜치의 마지막 stable 커밋 SHA 기록 (현재 `c53a07b` on wocs-site- / wocs-website-는 `3c204c5`)
- ✅ **봇 일시 정지**: 마이그레이션 PR 병합 직전 `.github/workflows/auto_blog.yml` disable, 병합 후 경로 호환성 재검증 후 enable
- ✅ **주중 오전 진행**: 실패 시 당일 내 복구 가능한 시간대
- ❌ **주말 금요일 저녁/공휴일 직전 절대 금지**

조건 만족 시 진행 가능. 조건 하나라도 미충족 시 **6월 이후 비수기까지 연기** 권장.

---

## 부록 — Vite 도입 방안 (참고용)

**최소침습 방안 (recommended)**:
```json
// package.json (신규)
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```
```js
// vite.config.js
export default {
  root: '.',
  publicDir: 'assets',  // ← 봇 건드리는 blog-data.js 보호
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: { main: 'index.html' },  // ← 서브페이지는 제외
      output: {
        entryFileNames: 'assets/js/[name].js',  // ← hash 억제
        assetFileNames: 'assets/[ext]/[name].[ext]'
      }
    }
  }
}
```
```json
// vercel.json (신규)
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [ ... subpage 경로 유지 ... ]
}
```

※ 위는 조사 결과로부터 도출한 설계 힌트이며, 실제 적용 전 dry-run 필수.

---

*조사 끝. 수정/커밋/푸시 없음.*
