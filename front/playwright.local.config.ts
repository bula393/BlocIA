import { defineConfig } from '@playwright/test';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';

const databaseDirectory = mkdtempSync(join(tmpdir(), 'blocia-e2e-'));

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/local-chat.spec.ts',
  timeout: 180_000,
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:4181', viewport: { width: 1440, height: 960 }, serviceWorkers: 'block', screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: [
    { command: '.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8181', cwd: resolve('../back'), url: 'http://127.0.0.1:8181/health', timeout: 60000, reuseExistingServer: false,
      env: { BLOCIA_DATABASE_PATH: join(databaseDirectory, 'test.sqlite3'), BLOCIA_DATA_PATH: join(databaseDirectory, 'no-legacy.json'), FRONTEND_URL: 'http://127.0.0.1:4181', HF_HUB_OFFLINE: '1', TRANSFORMERS_OFFLINE: '1' } },
    { command: 'npm.cmd run build && node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4181 --strictPort', url: 'http://127.0.0.1:4181', timeout: 120000, reuseExistingServer: false, env: { BLOCIA_API_URL: 'http://127.0.0.1:8181' } }
  ]
});
