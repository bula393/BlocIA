import { expect, test } from '@playwright/test';

test('login uses one primary blue action and block chassis', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('.bloq-shell')).toBeVisible();
  await expect(page.locator('button[data-primary="true"]')).toHaveCount(1);
  await expect(page.locator('.bloq-work')).toHaveCSS('border-radius', '0px');
});
