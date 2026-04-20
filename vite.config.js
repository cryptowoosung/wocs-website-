import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import { resolve } from 'path'

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
    })
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
