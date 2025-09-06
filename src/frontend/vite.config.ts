import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001, 
    host: '0.0.0.0', 
    open: true 
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['flowbite', 'flowbite-react']
        }
      }
    }
  },
  define: {
    // Environment variables will be available via import.meta.env
  }
})
