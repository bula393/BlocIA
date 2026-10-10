import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: ['mobile-responsive.spec.ts', 'personal-quota.spec.ts', 'google-callback.spec.ts', 'perfil-tecnico-visual.spec.ts'],
  timeout: 90000,
  expect: { timeout: 15000 },
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:4190', channel: 'msedge', serviceWorkers: 'block', screenshot: 'only-on-failure' },
  webServer: { command: 'npm run dev -- --host 127.0.0.1 --port 4190', url: 'http://127.0.0.1:4190', reuseExistingServer: true },
});
