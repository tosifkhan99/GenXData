import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Configure for GitHub Pages deployment
  base: '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Generate manifest for better caching
    manifest: true,
    // Optimize for production
    minify: 'terser',
    sourcemap: false,
  },
})
