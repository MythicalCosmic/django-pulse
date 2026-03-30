import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  root: '.',
  base: '/static/telescope/',
  build: {
    outDir: resolve(__dirname, '../src/telescope/static/telescope'),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'index.html'),
      output: {
        entryFileNames: 'assets/main.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
  server: {
    proxy: {
      '/telescope/api': 'http://127.0.0.1:8000',
      '/ws/telescope': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      },
    },
  },
})
