import { expect, test } from '@playwright/test';

const routes = ['/', '/login', '/register', '/perfil'];
const forbidden = ['gradient', 'border-radius: 999', '#4f46e5', '#6366f1', 'box-shadow: rgba'];

for (const route of routes) {
  test(`visual prohibitions on ${route}`, async ({ page }) => {
    await page.goto(route);
    const cssText = await page.locator('style, link[rel="stylesheet"]').evaluateAll(async (nodes) => {
      const texts: string[] = [];
      for (const node of nodes) {
        if (node instanceof HTMLStyleElement) texts.push(node.textContent ?? '');
        if (node instanceof HTMLLinkElement && node.href) {
          const response = await fetch(node.href);
          texts.push(await response.text());
        }
      }
      return texts.join('\n').toLowerCase();
    });
    for (const pattern of forbidden) expect(cssText).not.toContain(pattern);
    await expect(page.locator('.bloq-shell')).toBeVisible();
  });
}
