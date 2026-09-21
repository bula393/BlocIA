import { expect, test } from '@playwright/test';

const viewports = [
  { name: 'desktop', width: 1366, height: 900 },
  { name: 'compact-desktop', width: 1100, height: 800 },
  { name: 'tablet', width: 900, height: 900 },
  { name: 'mobile', width: 390, height: 844 }
];

for (const viewport of viewports) {
  test(`visual chassis renders on ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto('/login');
    await expect(page.locator('.bloq-shell')).toBeVisible();
    await expect(page.locator('.bloq-meter')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  });
}
