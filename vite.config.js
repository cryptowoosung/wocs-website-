import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import { resolve } from 'path'
import fs from 'node:fs'

// Inject LCP preload hint AFTER Vite's default HTML processing.
// Placed in source HTML, Vite would resolve/rewrite the href to a hashed
// bundle path that doesn't match the runtime <img src> from App.jsx.
// Using `order: 'post'` keeps the URL verbatim so preload matches the
// actual image request served by viteStaticCopy at /assets/images/.
function injectLcpPreloadPlugin() {
  return {
    name: 'inject-lcp-preload',
    transformIndexHtml: {
      order: 'post',
      handler(html) {
        const tag = '  <link rel="preload" as="image" href="/assets/images/17-d600-ext.webp" fetchpriority="high">\n'
        if (html.includes('href="/assets/images/17-d600-ext.webp"') && html.includes('rel="preload"')) {
          return html
        }
        return html.replace('</head>', tag + '</head>')
      },
    },
  }
}

// After Vite bundles CSS into /assets-built/main-*.css, it emits a
// render-blocking <link rel="stylesheet" crossorigin href="...">. Rewrite
// that to the preload+onload async pattern so the initial paint is not
// blocked waiting for CSS. The above-the-fold look is covered by the
// Critical CSS inlined in vite-index.html's <head>.
function asyncCssPlugin() {
  return {
    name: 'async-bundled-css',
    transformIndexHtml: {
      order: 'post',
      handler(html) {
        return html.replace(
          /<link\s+rel="stylesheet"(\s+crossorigin)?\s+href="([^"]+\.css)"\s*\/?>/g,
          (match, crossorigin, href) => {
            const co = crossorigin ? ' crossorigin' : ''
            return (
              `<link rel="preload"${co} href="${href}" as="style" ` +
              `onload="this.onload=null;this.rel='stylesheet'">` +
              `<noscript><link rel="stylesheet"${co} href="${href}"></noscript>`
            )
          },
        )
      },
    },
  }
}

// Vercel/정적 호스팅은 루트 요청 시 dist/index.html을 찾음.
// Vite 빌드 input이 vite-index.html이라 기본값으로 dist/vite-index.html만 생성됨.
// closeBundle 훅에서 rename하여 `/` 경로 404 방지.
function renameViteIndexPlugin() {
  return {
    name: 'rename-vite-index-to-index',
    closeBundle() {
      const from = resolve(__dirname, 'dist/vite-index.html')
      const to = resolve(__dirname, 'dist/index.html')
      if (fs.existsSync(from)) {
        if (fs.existsSync(to)) fs.unlinkSync(to)
        fs.renameSync(from, to)
        console.log('✓ dist/vite-index.html → dist/index.html')
      }
    },
  }
}

// 애드센스 삽입 자리: 빌드 환경변수 ADSENSE_CLIENT_ID(ca-pub-… 또는 pub-…)가 있을 때만
// dist 의 모든 HTML <head> 에 adsbygoogle 스크립트를 넣고 dist/ads.txt 를 만든다. 비어 있으면 아무것도 안 함.
function adsensePlugin() {
  return {
    name: 'adsense-head-and-ads-txt',
    closeBundle() {
      const raw = String(process.env.ADSENSE_CLIENT_ID || '').trim()
      const m = raw.match(/^(?:ca-)?(pub-\d{10,20})$/)
      if (!m) {
        console.log(raw ? '⚠ ADSENSE_CLIENT_ID 형식 오류 — 삽입 생략' : '· ADSENSE_CLIENT_ID 없음 — 애드센스 삽입 생략')
        return
      }
      const pub = m[1]
      const tag = `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-${pub}" crossorigin="anonymous"></script>\n`
      const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
        d.isDirectory() ? walk(resolve(dir, d.name)) : d.name.endsWith('.html') ? [resolve(dir, d.name)] : [])
      let n = 0
      for (const file of walk(resolve(__dirname, 'dist'))) {
        const html = fs.readFileSync(file, 'utf8')
        if (html.includes('adsbygoogle.js') || !html.includes('</head>')) continue
        fs.writeFileSync(file, html.replace('</head>', tag + '</head>'))
        n++
      }
      fs.writeFileSync(resolve(__dirname, 'dist/ads.txt'), `google.com, ${pub}, DIRECT, f08c47fec0942fa0\n`)
      console.log(`✓ 애드센스 스크립트 ${n}개 HTML 삽입 + dist/ads.txt 생성`)
    },
  }
}

// GA4: 빌드 환경변수 VITE_GA_ID(G-XXXXXXX)가 있을 때만 dist 의 모든 HTML </head> 앞에 gtag 를 넣는다.
// 비어 있거나 형식이 다르면 아무것도 안 함.
function ga4Plugin() {
  return {
    name: 'ga4-gtag-head',
    closeBundle() {
      const id = String(process.env.VITE_GA_ID || '').trim()
      if (!/^G-[A-Z0-9]{4,20}$/.test(id)) {
        console.log(id ? '⚠ VITE_GA_ID 형식 오류 — GA4 삽입 생략' : '· VITE_GA_ID 없음 — GA4 삽입 생략')
        return
      }
      const tag = `<script async src="https://www.googletagmanager.com/gtag/js?id=${id}"></script>\n` +
        `<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${id}');</script>\n`
      const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
        d.isDirectory() ? walk(resolve(dir, d.name)) : d.name.endsWith('.html') ? [resolve(dir, d.name)] : [])
      let n = 0
      for (const file of walk(resolve(__dirname, 'dist'))) {
        const html = fs.readFileSync(file, 'utf8')
        if (html.includes('googletagmanager.com/gtag/js') || !html.includes('</head>')) continue
        fs.writeFileSync(file, html.replace('</head>', tag + '</head>'))
        n++
      }
      console.log(`✓ GA4 gtag ${n}개 HTML 삽입`)
    },
  }
}

// sitemap 의 디렉터리 URL(/about/)을 그 페이지의 canonical(/about/index.html)에 맞춘다.
// 저장소 sitemap.xml 은 auto_blog 워크플로의 update_sitemap.py 가 발행 때마다 다시 만들기 때문에
// 원본이 아니라 빌드 산출물 dist/sitemap.xml 에서 맞춰야 유지된다.
function sitemapCanonicalPlugin() {
  return {
    name: 'sitemap-match-canonical',
    closeBundle() {
      const file = resolve(__dirname, 'dist/sitemap.xml')
      if (!fs.existsSync(file)) return
      let n = 0
      const xml = fs.readFileSync(file, 'utf8').replace(/<loc>(https:\/\/wocs\.kr\/[^<]*\/)<\/loc>/g, (tag, url) => {
        const page = resolve(__dirname, 'dist', new URL(url).pathname.slice(1), 'index.html')
        if (!fs.existsSync(page)) return tag
        const canonical = fs.readFileSync(page, 'utf8').match(/<link\s+rel="canonical"\s+href="([^"]+)"/)?.[1]
        if (!canonical || canonical === url) return tag
        n++
        return `<loc>${canonical}</loc>`
      })
      fs.writeFileSync(file, xml)
      console.log(`✓ sitemap loc ${n}개를 canonical 에 맞춤`)
    },
  }
}

// noindex 블로그 글(dist/content)에서는 애드센스 스크립트를 뺀다.
// adsensePlugin 은 dist 전체에 넣으므로, 그 뒤에 실행되도록 plugins 에서 adsensePlugin 다음에 둔다.
function adsenseSkipNoindexPlugin() {
  return {
    name: 'adsense-skip-noindex-posts',
    closeBundle() {
      const dir = resolve(__dirname, 'dist/content')
      if (!fs.existsSync(dir)) return
      const noindex = /<meta\s+name=["']robots["'][^>]*content=["'][^"']*noindex/i
      const adsTag = /<script[^>]*adsbygoogle\.js[^>]*><\/script>\n?/g
      let n = 0
      for (const name of fs.readdirSync(dir).filter((f) => f.endsWith('.html'))) {
        const file = resolve(dir, name)
        const html = fs.readFileSync(file, 'utf8')
        if (!noindex.test(html) || !html.includes('adsbygoogle.js')) continue
        fs.writeFileSync(file, html.replace(adsTag, ''))
        n++
      }
      console.log(`✓ noindex 글 ${n}편 애드센스 스크립트 제외`)
    },
  }
}

// 홈 본문이 <noscript> 안에만 있어, 그것을 읽지 않는 크롤러에게 홈이 빈 페이지로 보인다.
// 빌드 때 noscript 내용을 #root 안으로 옮겨 JS 실행 전에도 본문과 <h1> 1개가 HTML 에 있게 한다.
// React 의 createRoot().render() 가 첫 렌더 때 #root 안을 비우므로 React 가 뜬 뒤 화면은 그대로다.
// noscript 를 남겨 두면 <h1> 이 2개가 되므로 복사가 아니라 이동이다.
function staticHomePlugin() {
  const WRAPPER_STYLE = 'max-width:1200px;margin:0 auto;padding:120px 20px 40px;line-height:1.7'
  return {
    name: 'static-home-body',
    closeBundle() {
      const file = resolve(__dirname, 'dist/index.html')
      const html = fs.readFileSync(file, 'utf8')
      const block = /<noscript>\s*(<div>\s*<header>[\s\S]*?)<\/noscript>\s*<div id="root"><\/div>/
      const found = html.match(block)
      if (!found) {
        console.log('⚠ 홈 noscript 본문을 찾지 못함 — 정적 본문 삽입 생략')
        return
      }
      // 이제 사람에게도 보이는 내용이므로 크롤러 전용 안내문과 색인 대상이 아닌 껍데기 페이지 링크는 뺀다.
      const body = found[1]
        .replace(/<p>JavaScript 미실행 환경[\s\S]*?<\/p>/, '<p><a href="/sitemap.html">사이트맵 전체 보기</a></p>')
        .replace(/\s*<li><a href="\/(?:products\/product-template|portfolio\/case-detail|resources\/blog-post)\.html">[^<]*<\/a><\/li>/g, '')
      fs.writeFileSync(file, html.replace(block, () => `<div id="root"><div style="${WRAPPER_STYLE}">${body}</div></div>`))
      console.log('✓ 홈 정적 본문을 #root 안에 삽입')
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    viteStaticCopy({
      targets: [
        // 기존 디렉토리를 통째로 복사: src='dir', dest='.' → dist/dir/
        { src: 'assets', dest: '.' },
        { src: 'products', dest: '.' },
        { src: 'occasions', dest: '.' },
        { src: 'project', dest: '.' },
        { src: 'resources', dest: '.' },
        { src: 'gallery', dest: '.' },
        { src: 'portfolio', dest: '.' },
        { src: 'about', dest: '.' },
        { src: 'contact', dest: '.' },
        { src: 'legal', dest: '.' },
        { src: 'content', dest: '.' },
        // 루트 정적 파일들 (존재하는 것만 복사)
        {
          src: ['sitemap.xml', 'sitemap.html', 'robots.txt', 'favicon.ico', 'favicon.svg', 'manifest.json', 'site.webmanifest', 'blog-data.js', 'cta_counter.json', 'privacy.html', 'bc5ada97a10c8516596ea24189a7452a.txt', 'feed.xml', 'llms.txt'],
          dest: '.'
        }
      ]
    }),
    injectLcpPreloadPlugin(),
    asyncCssPlugin(),
    renameViteIndexPlugin(),
    staticHomePlugin(),
    adsensePlugin(),
    adsenseSkipNoindexPlugin(),
    ga4Plugin(),
    sitemapCanonicalPlugin(),
  ],
  publicDir: false,
  build: {
    outDir: 'dist',
    assetsDir: 'assets-built',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'vite-index.html'),
      }
    }
  },
  server: {
    port: 5173,
    open: false,
  }
})
