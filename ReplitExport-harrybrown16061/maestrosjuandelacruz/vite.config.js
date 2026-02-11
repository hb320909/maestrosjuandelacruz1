import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: '.',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      output: {
        manualChunks: {
          vendor: ['@supabase/supabase-js']
        }
      }
    }
  },
  server: {
    port: 5000,
    strictPort: true,
    host: '0.0.0.0',
    allowedHosts: true
  },
  base: './'
})
