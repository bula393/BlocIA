import { expect, test } from '@playwright/test';

test('profile uses drawer and structural zero-radius regions', async ({ page }) => {
  await page.addInitScript(() => {
    const encode = (value: string) => btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const header = encode(JSON.stringify({ alg: 'none', typ: 'JWT' }));
    const payload = encode(JSON.stringify({ sub: 'usuario.demo@example.com', exp: 4102444800 }));
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${header}.${payload}.signature`;
  });
  await page.goto('/perfil');
  await expect(page.locator('.bloq-work')).toHaveCSS('border-radius', '0px');
  await expect(page.locator('button[data-primary="true"]')).toHaveCSS('border-radius', '4px');
});
