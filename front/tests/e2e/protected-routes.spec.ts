import { expect, type Page, test } from '@playwright/test';

async function injectValidJwt(page: Page) {
  await page.addInitScript(() => {
    const encode = (value: string) => btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const header = encode(JSON.stringify({ alg: 'none', typ: 'JWT' }));
    const payload = encode(JSON.stringify({ sub: 'usuario.demo@example.com', exp: 4102444800 }));
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${header}.${payload}.signature`;
  });
}

test('missing jwt shows guard on profile', async ({ page }) => {
  await page.goto('/perfil');
  await expect(page.getByRole('heading', { name: 'Iniciá sesión para seguir' })).toBeVisible();
  await expect(page.locator('.guard-surface').getByRole('link', { name: 'Iniciar sesión' })).toBeVisible();
  await expect(page.getByText('Cargando perfil...')).toHaveCount(0);
});

test('invalid jwt shows guard on technical profile', async ({ page }) => {
  await page.addInitScript(() => {
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = 'invalid';
  });
  await page.goto('/perfil-tecnico');
  await expect(page.getByRole('heading', { name: 'Iniciá sesión para seguir' })).toBeVisible();
  await expect(page.getByText('Cargando proveedores...')).toHaveCount(0);
});

test('expired jwt shows guard on profile', async ({ page }) => {
  await page.addInitScript(() => {
    const encode = (value: string) => btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${encode(JSON.stringify({ alg: 'none', typ: 'JWT' }))}.${encode(JSON.stringify({ sub: 'user', exp: 1 }))}.signature`;
  });
  await page.goto('/perfil');
  await expect(page.getByRole('heading', { name: 'Iniciá sesión para seguir' })).toBeVisible();
});

test('valid jwt allows protected profile shell', async ({ page }) => {
  await injectValidJwt(page);
  await page.goto('/perfil');
  await expect(page.getByRole('heading', { name: 'Perfil' })).toBeVisible();
});
