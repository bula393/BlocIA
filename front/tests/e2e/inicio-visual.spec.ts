import { expect, test } from '@playwright/test';

test('start page shows the product statement and access action', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.bloq-brand')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Tu espacio para pensar con criterio.' })).toBeVisible();
  await expect(page.locator('.inicio-actions').getByRole('link', { name: 'Iniciar sesión' })).toBeVisible();
});

test('start page keeps its reading order on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  const boxes = await Promise.all([
    page.getByRole('heading', { name: 'Tu espacio para pensar con criterio.' }).boundingBox(),
    page.locator('.inicio-actions').getByRole('link', { name: 'Iniciar sesión' }).boundingBox()
  ]);
  for (const box of boxes) expect(box).not.toBeNull();
  const [heading, action] = boxes as NonNullable<(typeof boxes)[number]>[];
  expect(action.y).toBeGreaterThan(heading.y);
});
