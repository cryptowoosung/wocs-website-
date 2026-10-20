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
    adsensePlugin(),
    ga4Plugin(),
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
