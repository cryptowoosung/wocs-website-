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
        // 루트 정적 파일들 (존재하는 것만 복사)
        {
          src: ['sitemap.xml', 'robots.txt', 'favicon.ico', 'favicon.svg', 'manifest.json', 'site.webmanifest', 'blog-data.js', 'cta_counter.json'],
          dest: '.'
        }
      ]
    }),
    injectLcpPreloadPlugin(),
    renameViteIndexPlugin(),
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
