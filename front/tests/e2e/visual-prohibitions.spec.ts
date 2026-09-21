import { expect, test } from '@playwright/test';

const forbiddenCss = ['gradient', 'box-shadow: rgba', 'border-radius: 999', '#4f46e5', '#6366f1'];

test('visual system avoids prohibited CSS patterns', async ({ page }) => {
  await page.goto('/login');
  const cssTexts = await page.locator('style, link[rel="stylesheet"]').evaluateAll(async (nodes) => {
    const texts: string[] = [];
    for (const node of nodes) {
      if (node instanceof HTMLStyleElement) {
        texts.push(node.textContent ?? '');
      }
      if (node instanceof HTMLLinkElement && node.href) {
        const response = await fetch(node.href);
        texts.push(await response.text());
      }
    }
    return texts.join('\n').toLowerCase();
  });

  for (const pattern of forbiddenCss) {
    expect(cssTexts).not.toContain(pattern);
  }
});

test('primary controls do not use pill radius', async ({ page }) => {
  await page.goto('/login');
  const radii = await page.locator('button, input').evaluateAll((nodes) =>
    nodes.map((node) => getComputedStyle(node).borderRadius)
  );
  expect(radii.every((radius) => radius !== '999px')).toBe(true);
});
