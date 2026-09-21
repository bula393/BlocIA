import { expect, test } from '@playwright/test';

const routes = ['/', '/login', '/register', '/perfil'];
const viewports = [
  { width: 1366, height: 900 },
  { width: 900, height: 900 },
  { width: 390, height: 844 }
];

for (const route of routes) {
  for (const viewport of viewports) {
    test(`responsive render ${route} at ${viewport.width}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(route);
      await expect(page.locator('.bloq-shell')).toBeVisible();
      await expect(page.locator('.bloq-meter')).toBeVisible();
    });
  }
}
