import { expect, test } from '@playwright/test';

test('profile keeps its account panel readable on desktop and mobile', async ({ page }) => {
  await page.addInitScript(() => {
    const encode = (value: string) => btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const header = encode(JSON.stringify({ alg: 'none', typ: 'JWT' }));
    const payload = encode(JSON.stringify({ sub: 'usuario.demo@example.com', exp: 4102444800 }));
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${header}.${payload}.signature`;
  });
  await page.route('**/profile', (route) => route.fulfill({ json: {
    mail: 'usuario.demo@example.com', age: 28, profession: 'Estudiante', displayName: 'Ana',
    loginProviderStatus: 'password', technicalProfileStatus: 'not-configured'
  } }));
  await page.route('**/usage/today', (route) => route.fulfill({ json: { chatMessages: 0, modelCatalogRequests: 0, configuredProviders: 0, lastActivityAt: null } }));
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/perfil');
  await expect(page.getByRole('textbox', { name: 'Nombre visible' })).toHaveValue('Ana');
  await expect(page.getByRole('complementary', { name: 'Datos de tu cuenta' })).toContainText('usuario.demo@example.com');
  await expect(page.locator('.bloq-work')).toHaveCSS('border-radius', '0px');
  await expect(page.locator('button[data-primary="true"]')).toHaveCSS('border-radius', '4px');
  const desktopEdit = await page.locator('.profile-edit').boundingBox();
  const desktopSummary = await page.locator('.profile-summary').boundingBox();
  expect(desktopSummary!.x).toBeGreaterThan(desktopEdit!.x);
  await page.screenshot({ path: 'test-results/profile-desktop.png', fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  const mobileEdit = await page.locator('.profile-edit').boundingBox();
  const mobileSummary = await page.locator('.profile-summary').boundingBox();
  expect(mobileSummary!.y).toBeGreaterThan(mobileEdit!.y);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: 'test-results/profile-mobile.png', fullPage: true });
  const saveButton = page.getByRole('button', { name: 'Guardar cambios' });
  await saveButton.evaluate((button) => button.scrollIntoView({ block: 'center' }));
  const buttonPosition = await saveButton.boundingBox();
  expect(buttonPosition!.y + buttonPosition!.height).toBeLessThan(844 - 56);
  await page.screenshot({ path: 'test-results/profile-mobile-action.png' });
});
