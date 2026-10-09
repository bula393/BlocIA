import { expect, test } from '@playwright/test';

test.use({ serviceWorkers: 'block' });

test('personal response asks after classification and shows the final allowance on desktop and mobile', async ({ page }) => {
  await page.addInitScript(() => {
    const encode = (value: object) => btoa(JSON.stringify(value)).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${encode({ alg: 'none' })}.${encode({ sub: 'quota@example.com', exp: 4102444800 })}.signature`;
  });
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  const conversation = { id: '62f55b55-88d2-4bad-9c17-f87c9f095cac', title: 'Nuevo chat', createdAt: '2026-10-08T12:00:00Z', updatedAt: '2026-10-08T12:00:00Z' };
  const classification = { label: 'personal_informativa', group: 'personal', confidence: 0.95, status: 'aceptada', needs_human_review: false };
  let used = 2;
  const limits = () => ({ blocked: used === 3, reasonCodes: used === 3 ? ['personal_questions'] : [], lockUntil: used === 3 ? new Date(Date.now() + 15 * 60_000).toISOString() : null, lockDurationMinutes: 15, usageSeconds: 2, usageLimitSeconds: 10800, personalQuestions: used, personalQuestionLimit: 3, personalQuestionsRemaining: 3 - used });
  const posts: Array<{ prompt: string; requestId: string; acceptPersonalResponse: boolean }> = [];
  await page.route('**/api/chat/**', async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith('/status')) {
      await route.fulfill({ json: { ready: true, classifierReady: true, mode: 'classification', model: 'test', maxInputCharacters: 4000, usageLock: limits(), freeModels: [{ providerId: 'local', providerName: 'En tu equipo', modelId: 'qwen3-local', displayName: 'Qwen local' }], training: { examples: 1000, macroF1: 0.9, decisionRecall: 0.9 } } });
    } else if (url.pathname.endsWith('/progress')) {
      await route.fulfill({ json: { phase: 'classifying', state: 'pending' } });
    } else if (url.pathname.endsWith('/messages')) {
      const payload = route.request().postDataJSON();
      posts.push(payload);
      if (!payload.acceptPersonalResponse) {
        await route.fulfill({ status: 202, json: { conversation, messages: [], confirmationRequired: true, classification, usageLock: limits() } });
      } else {
        used = 3;
        await route.fulfill({ json: { conversation, messages: [
          { id: 'question', role: 'user', content: payload.prompt, requestId: payload.requestId, createdAt: conversation.createdAt, classification },
          { id: 'answer', role: 'assistant', content: 'Podés ordenar los factores y comparar tus opciones.', requestId: payload.requestId, createdAt: conversation.createdAt, classification, providerId: 'local', modelId: 'qwen3-local' },
        ], usageLock: limits() } });
      }
    } else if (url.pathname.endsWith('/conversations')) {
      await route.fulfill({ status: route.request().method() === 'POST' ? 201 : 200, json: route.request().method() === 'POST' ? conversation : { conversations: [] } });
    } else {
      await route.fulfill({ json: { conversation, messages: [] } });
    }
  });
  await page.route('**/usage/limits', (route) => route.fulfill({ json: limits() }));
  await page.route('**/technical-profile/providers', (route) => route.fulfill({ json: { providers: [] } }));

  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/nuevo-chat');
  await page.getByRole('combobox', { name: 'Modelo de respuesta', exact: true }).click();
  await page.getByRole('option', { name: /Qwen local/ }).click();
  const input = page.getByLabel('Mensaje para BloqIA');
  const send = page.getByRole('button', { name: 'Enviar mensaje', exact: true });
  await input.fill('¿Qué factores de mi carrera me ayudan a aprender?');
  await expect(send).toBeEnabled();
  await send.click();
  const confirm = page.getByRole('button', { name: 'Usar 1 respuesta', exact: true });
  await expect(confirm).toBeVisible();
  await expect(page.locator('.chat-composer .chat-personal-confirmation')).toBeVisible();
  await expect(page.locator('.chat-composer > .chat-personal-quota:last-child')).toBeVisible();
  expect(posts).toHaveLength(1);
  expect(posts[0].acceptPersonalResponse).toBe(false);
  expect(used).toBe(2);
  await expect(input).toBeDisabled();
  await expect(page.locator('.chat-composer > .chat-personal-quota:last-child')).toBeVisible();
  await page.screenshot({ path: 'test-results/personal-quota-desktop.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.setViewportSize({ width: 390, height: 844 });
  await expect.poll(() => page.locator('.bloq-rail').evaluate((rail) => rail.getBoundingClientRect().right)).toBeLessThanOrEqual(0.1);
  await expect(confirm).toBeVisible();
  await page.screenshot({ path: 'test-results/personal-quota-mobile.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.getByRole('button', { name: 'Cancelar', exact: true }).click();
  await expect(input).toBeEnabled();
  expect(posts).toHaveLength(1);
  expect(used).toBe(2);
  await send.click();
  await expect(confirm).toBeVisible();
  await confirm.click();
  await expect(page.getByRole('heading', { name: 'Bloqueo activo' })).toBeVisible();
  await expect(input).toBeDisabled();
  expect(posts).toHaveLength(3);
  expect(posts[2].requestId).toBe(posts[1].requestId);
  expect(posts[2].acceptPersonalResponse).toBe(true);
  await expect(page.getByRole('progressbar', { name: /respuestas personales/i })).toHaveAttribute('aria-valuenow', '3');
  await expect(page.getByText(/15 minutos/).first()).toBeVisible();
  await page.screenshot({ path: 'test-results/personal-quota-mobile-locked.png', fullPage: true });
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.screenshot({ path: 'test-results/personal-quota-desktop-locked.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
