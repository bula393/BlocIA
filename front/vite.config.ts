import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backend = process.env.BLOCIA_API_URL ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: backend,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/profile': backend,
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
