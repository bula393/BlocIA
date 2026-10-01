import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/auth/session', (route) => route.fulfill({ status: 401, json: { detail: 'Sin sesión' } }));
});

test('start page shows the product statement and access action', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.bloq-brand')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Tu espacio para pensar con criterio.' })).toBeVisible();
  await expect(page.locator('.inicio-actions').getByRole('link', { name: 'Iniciar sesión' })).toBeVisible();
});

for (const width of [320, 390, 768, 1024, 1440]) {
  test(`home preserves palette and reading layout at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 960 });
    await page.goto('/');
    const primary = page.locator('.inicio-actions [data-primary="true"]');
    await expect(primary).toHaveCount(1);
    await expect(primary).toHaveCSS('background-color', 'rgb(28, 72, 155)');
    await expect(page.locator('.bloq-work')).toHaveCSS('background-color', 'rgb(255, 246, 219)');
    await expect(page.getByRole('link', { name: 'Inicio', exact: true })).toHaveAttribute('aria-current', 'page');
    await expect(page.getByRole('complementary', { name: 'Ejemplo ilustrativo de una conversación' })).toContainText('Ejemplo');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    const copy = await page.locator('.inicio-copy').boundingBox();
    const example = await page.locator('.inicio-example').boundingBox();
    expect(copy).not.toBeNull();
    expect(example).not.toBeNull();
    if (width < 768) expect(example!.y).toBeGreaterThanOrEqual(copy!.y + copy!.height);
    else expect(example!.x).toBeGreaterThanOrEqual(copy!.x + copy!.width);
    const action = await primary.boundingBox();
    expect(action!.height).toBeGreaterThanOrEqual(44);
    await page.getByRole('link', { name: 'Inicio', exact: true }).focus();
    await expect(page.getByRole('link', { name: 'Inicio', exact: true })).toHaveCSS('outline-color', 'rgb(255, 246, 219)');
  });
}

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
