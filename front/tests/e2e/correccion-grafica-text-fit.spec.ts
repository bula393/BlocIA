import { expect, test } from '@playwright/test';

for (const route of ['/', '/login', '/register', '/perfil']) {
  test(`text fits key controls on ${route}`, async ({ page }) => {
    await page.goto(route);
    const overflow = await page.locator('button, a, input, .bloq-chip, .bloq-status-line').evaluateAll((nodes) =>
      nodes.some((node) => node.scrollWidth > node.clientWidth || node.scrollHeight > node.clientHeight)
    );
    expect(overflow).toBe(false);
  });
}
