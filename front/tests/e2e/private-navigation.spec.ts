import { expect, test, type Page } from '@playwright/test';

async function injectValidJwt(page: Page) {
  await page.addInitScript(() => {
    const encode = (value: string) => btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const header = encode(JSON.stringify({ alg: 'none', typ: 'JWT' }));
    const payload = encode(JSON.stringify({ sub: 'usuario.demo@example.com', exp: 4102444800 }));
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${header}.${payload}.signature`;
  });
}

test('private navigation and usage stay hidden before login', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByLabel('Ver perfil')).toHaveCount(0);
  await expect(page.getByLabel('Ver estadísticas de uso')).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Configuración técnica' })).toHaveCount(0);
  await expect(page.locator('.bloq-panel')).toHaveCount(0);
});

test('authenticated users open statistics from the usage control', async ({ page }) => {
  await injectValidJwt(page);
  await page.goto('/perfil');
  await expect(page.getByLabel('Ver perfil')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Configuración técnica' })).toBeVisible();
  await page.getByLabel('Ver estadísticas de uso').click();
  await expect(page.getByRole('complementary', { name: 'Estadísticas de uso' })).toBeVisible();
  await expect(page.getByText('Tiempo usado')).toBeVisible();
});
