const { chromium } = require('playwright');
const { expect } = require('@playwright/test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const out = path.resolve(__dirname, '../../.impeccable/review');
let browser;

(async () => {
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('http://127.0.0.1:4175/mockup#/providers');
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator('.mw-providers-page h1')).toBeInViewport();
  await page.locator('.mw-canvas').evaluate(el => { el.scrollTop = el.scrollHeight; });
  await page.getByRole('button', { name: 'Actividad', exact: true }).click();
  await expect(page.locator('.mw-usage-page h1')).toBeInViewport();
  await expect(page.locator('.mw-usage-overview')).toBeInViewport();
  await expect.poll(() => page.locator('.mw-canvas').evaluate(el => el.scrollTop)).toBe(0);
  await page.screenshot({ path: path.join(out, 'desktop-usage.png'), fullPage: true });
  await page.locator('.mw-canvas').evaluate(el => { el.scrollTop = el.scrollHeight; });
  await page.getByRole('button', { name: 'Proveedores y modelos', exact: true }).click();
  await expect(page.locator('.mw-providers-page h1')).toBeInViewport();
  await expect.poll(() => page.locator('.mw-canvas').evaluate(el => el.scrollTop)).toBe(0);
  await page.screenshot({ path: path.join(out, 'desktop-providers.png'), fullPage: true });
  await page.getByRole('button', { name: 'Tu perfil', exact: true }).click();
  await page.locator('.mw-canvas').evaluate(el => { el.scrollTop = el.scrollHeight; });
  await page.goBack();
  await expect(page.locator('.mw-providers-page h1')).toBeInViewport();
  await expect.poll(() => page.locator('.mw-canvas').evaluate(el => el.scrollTop)).toBe(0);
  await page.goForward();
  await expect(page.locator('.mw-profile-page h1')).toBeInViewport();
  await expect.poll(() => page.locator('.mw-canvas').evaluate(el => el.scrollTop)).toBe(0);

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  for (const view of ['login', 'register', 'google']) {
    await mobile.goto(`http://127.0.0.1:4175/mockup.html#/${view}`);
    await mobile.waitForLoadState('networkidle');
    await mobile.evaluate(() => document.fonts.ready);
    await expect(mobile.locator('.mw-auth-story h2')).toHaveText('La claridad empieza con una pregunta.');
    await mobile.screenshot({ path: path.join(out, `mobile-${view}.png`), fullPage: true });
  }
  assert.deepEqual(errors, []);
  const result = { passed: true, resolved: ['Semantic spaces in all three mobile access views', 'Top of new view visible after scroll in previous view', 'Scroll reset after browser back and forward', 'Standalone and integrated mockup entry routes'], errors };
  await fs.writeFile(path.join(out, 'review-fixes.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  await browser.close();
})().catch(async error => { console.error(error); if (browser) await browser.close(); process.exitCode = 1; });
