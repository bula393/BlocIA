import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

const backend = process.env.BLOCIA_API_URL ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        app: fileURLToPath(new URL('./index.html', import.meta.url)),
        mockup: fileURLToPath(new URL('./mockup.html', import.meta.url))
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: backend,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/profile': backend,
      '/usage': backend,
      '/technical-profile': backend
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/integration/**/*.test.tsx', 'tests/integration/**/*.test.ts', 'tests/unit/**/*.test.ts']
  }
});
