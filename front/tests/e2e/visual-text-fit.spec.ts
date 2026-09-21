import { expect, test } from '@playwright/test';

test('visible controls keep text inside their boxes', async ({ page }) => {
  await page.goto('/perfil-tecnico');
  const overflow = await page.locator('button, input, .bloq-chip').evaluateAll((nodes) =>
    nodes.some((node) => node.scrollWidth > node.clientWidth || node.scrollHeight > node.clientHeight)
  );
  expect(overflow).toBe(false);
});
