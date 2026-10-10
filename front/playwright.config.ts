import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: { timeout: 15000 },
  testDir: './tests/e2e',
  testIgnore: '**/local-chat.spec.ts',
  use: {
    baseURL: 'http://127.0.0.1:4173'
  },
  webServer: {
    command: 'npm run build && npx vite preview --host 127.0.0.1 --port 4173',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: true,
    timeout: 120000
  }
});
