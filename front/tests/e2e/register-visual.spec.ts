import { expect, test } from '@playwright/test';

test('register uses visual-system form controls', async ({ page }) => {
  await page.goto('/register');
  await expect(page.locator('button[data-primary="true"]')).toHaveCount(1);
  await expect(page.locator('input').first()).toHaveCSS('border-radius', '4px');
});
