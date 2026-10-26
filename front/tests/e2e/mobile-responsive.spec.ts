import { test, expect, type Page } from '@playwright/test';

test.use({ serviceWorkers: 'block' });

const id = '11111111-1111-4111-8111-111111111111';
const time = '2026-10-09T12:00:00Z';
const conversation = { id, title: '¿Qué es una API?', createdAt: time, updatedAt: time };
const profile = { mail: 'qa@example.com', displayName: 'Usuario de prueba', age: 25, profession: 'Estudiante', loginProviderStatus: 'password', technicalProfileStatus: 'partially-configured' };
const classification = { label: 'no_personal', group: 'general', confidence: .98, status: 'aceptada', needs_human_review: false };
const messages = [
  { id: 'u1', role: 'user', content: conversation.title, createdAt: time, requestId: 'r1', classification: null },
  { id: 'a1', role: 'assistant', content: 'Una **API** permite que dos aplicaciones se comuniquen entre sí.', createdAt: time, requestId: 'r1', classification, providerId: 'groq', modelId: 'openai/gpt-oss-20b' },
];
const model = { modelId: 'openai/gpt-oss-20b', displayName: 'GPT OSS 20B', availabilityStatus: 'available', capabilities: ['text'] };
const limits = { blocked: false, reasonCodes: [], lockUntil: null, usageSeconds: 180, usageLimitSeconds: 10800, personalQuestions: 1, personalQuestionLimit: 3, personalQuestionsRemaining: 2, lockDurationMinutes: 1440 };

async function fixtures(page: Page, { authenticated = true, blocked = false } = {}) {
  let items = [conversation];
  let stored = [...messages];
  const lock = blocked ? { ...limits, blocked: true, reasonCodes: ['personal_questions'], lockUntil: '2026-10-10T12:00:00Z', personalQuestions: 3, personalQuestionsRemaining: 0 } : limits;
  const token = `${Buffer.from('{"alg":"none"}').toString('base64url')}.${Buffer.from(JSON.stringify({ sub: profile.mail, exp: Math.floor(Date.now() / 1000) + 3600 })).toString('base64url')}.signature`;
  await page.route(/^https?:\/\/[^/]+\/(?:api\/|technical-profile\/|usage\/|profile(?:$|\?))/, async route => {
    const path = new URL(route.request().url()).pathname;
    const method = route.request().method();
    let data: unknown;
    if (path === '/api/auth/session') {
      if (!authenticated) return route.fulfill({ status: 401, json: { message: 'Sin sesión' } });
      data = { user: profile, accessToken: token, expiresInSeconds: 3600 };
    } else if (path === '/profile') data = { ...profile, ...(method === 'PATCH' ? route.request().postDataJSON() : {}) };
    else if (path === '/usage/limits') data = lock;
    else if (path === '/api/chat/status') data = { ready: true, classifierReady: true, mode: 'classification', model: 'classifier', maxInputCharacters: 4000, usageLock: lock, training: {}, freeModels: [{ providerId: 'local', providerName: 'Local', modelId: 'Qwen/Qwen3-0.6B', displayName: 'Qwen3 0.6B' }] };
    else if (path === '/technical-profile/providers') data = { providers: ['google', 'groq', 'openrouter', 'openai', 'anthropic'].map(providerId => ({ providerId, name: providerId, status: 'available', defaultTokenAvailable: providerId === 'groq', tokenStatus: { providerId, status: 'not-configured' }, models: providerId === 'groq' ? [model] : [] })) };
    else if (path.endsWith('/models')) data = { providerId: path.split('/')[3], source: path.includes('/groq/') ? 'default' : 'catalog', message: 'Catálogo de prueba', models: path.includes('/groq/') ? [model] : [] };
    else if (path === '/technical-profile/email-verification') data = { verified: true, email: profile.mail, expiresInSeconds: null, resendInSeconds: 0 };
    else if (path === '/usage/dashboard') data = { limits: lock, summary: { totalQueries: 1, personalQueries: 0, classifiedQueries: 1, categoryCounts: { no_personal: 1 }, providerCounts: [{ providerId: 'groq', count: 1 }], lastSevenDays: [{ date: '2026-10-09', count: 1, personal: 0 }] }, activity: { items: [{ prompt: conversation.title, createdAt: time, classification, providerId: 'groq', modelId: model.modelId, durationSeconds: 4, conversationId: id, conversationTitle: conversation.title }], total: 1, offset: 0, limit: 40, hasMore: false } };
    else if (path === '/api/chat/conversations') data = method === 'POST' ? conversation : { conversations: items };
    else if (path.endsWith('/progress')) data = { phase: 'classifying', state: 'pending' };
    else if (path.endsWith('/messages')) {
      const body = route.request().postDataJSON();
      if (body.prompt.includes('personal') && !body.acceptPersonalResponse) data = { conversation, messages: [], confirmationRequired: true, classification: { ...classification, label: 'personal_informativa' }, usageLock: lock };
      else {
        stored = [{ ...messages[0], content: body.prompt }, messages[1]];
        data = { conversation, messages: stored, usageLock: lock };
      }
    } else if (path === `/api/chat/conversations/${id}`) {
      if (method === 'DELETE') { items = []; return route.fulfill({ status: 204 }); }
      data = { conversation, messages: stored, usageLock: lock };
    } else return route.fulfill({ status: 404, json: { message: `Sin fixture: ${path}` } });
    return route.fulfill({ json: data });
  });
}

async function capture(page: Page, name: string) {
  await page.evaluate(() => document.fonts.ready);
  if (await page.getByRole('dialog').count()) {
    await expect.poll(() => page.getByRole('dialog').evaluate(element => new DOMMatrix(getComputedStyle(element).transform).m42)).toBeLessThan(.5);
  }
  await page.evaluate(() => Promise.all(document.getAnimations()
    .filter(animation => animation.effect?.getTiming().iterations !== Infinity)
    .map(animation => animation.finished.catch(() => undefined))));
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  if (process.env.MOBILE_SCREENSHOTS) await page.screenshot({ path: `${process.env.MOBILE_SCREENSHOTS}/${name}.png`, fullPage: true });
}

test('internal sections keep the same document, announce their heading and support back navigation', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await fixtures(page);
  await page.goto('/cuenta');
  await page.evaluate(() => { document.documentElement.dataset.navigationMarker = 'same-document'; });
  const rail = page.locator('.bloq-rail');
  await rail.getByRole('link', { name: 'Perfil', exact: true }).click();
  await expect(page).toHaveURL(/\/perfil$/);
  await expect(page.getByLabel('Nombre')).toHaveValue(profile.displayName);
  await expect(page.locator('h1')).toBeFocused();
  await rail.getByRole('link', { name: 'Proveedores y modelos', exact: true }).click();
  await expect(page.locator('.technical-intro')).toBeVisible();
  await rail.getByRole('link', { name: 'Actividad', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Actividad y límites' })).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-navigation-marker', 'same-document');
  await page.goBack();
  await expect(page).toHaveURL(/\/perfil-tecnico$/);
  await expect(page.locator('.technical-intro')).toBeVisible();
  await page.goForward();
  await expect(page.getByRole('heading', { name: 'Actividad y límites' })).toBeVisible();
  // Two destinations requested before the first snapshot commits must end on the last request.
  await page.evaluate(() => {
    document.querySelector<HTMLAnchorElement>('.bloq-nav a[href="/perfil"]')!.click();
    document.querySelector<HTMLAnchorElement>('.bloq-nav a[href="/perfil-tecnico"]')!.click();
  });
  await expect(page).toHaveURL(/\/perfil-tecnico$/);
  await expect(page.locator('.technical-intro')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-navigation-marker', 'same-document');
});

test('keyboard and reduced-motion navigation skip snapshots, while pointer navigation uses them', async ({ page }) => {
  await page.addInitScript(() => {
    const doc = document as Document & { startViewTransition?: (callback: () => void) => unknown };
    const start = doc.startViewTransition?.bind(document);
    if (start) doc.startViewTransition = (callback) => {
      document.documentElement.dataset.snapshotCount = String(Number(document.documentElement.dataset.snapshotCount ?? 0) + 1);
      return start(callback);
    };
  });
  await fixtures(page, { authenticated: false });
  await page.goto('/login');
  const supported = await page.evaluate(() => 'startViewTransition' in document);
  await page.getByRole('link', { name: 'Crear cuenta', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Crear cuenta' })).toBeVisible();
  const beforeKeyboard = await page.locator('html').getAttribute('data-snapshot-count');
  if (supported) expect(beforeKeyboard).toBe('1');
  await page.getByRole('link', { name: 'Iniciar sesión', exact: true }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  expect(await page.locator('html').getAttribute('data-snapshot-count')).toBe(beforeKeyboard);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.getByRole('link', { name: 'Crear cuenta', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Crear cuenta' })).toBeVisible();
  expect(await page.locator('html').getAttribute('data-snapshot-count')).toBe(beforeKeyboard);
});

test('older-browser fallback keeps navigation and modified links usable', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(document, 'startViewTransition', { configurable: true, value: undefined });
  });
  await fixtures(page, { authenticated: false });
  await page.goto('/login');
  await page.evaluate(() => { document.documentElement.dataset.navigationMarker = 'fallback'; });
  await page.getByRole('link', { name: 'Crear cuenta', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Crear cuenta' })).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-navigation-marker', 'fallback');
  const intercepted = await page.getByRole('link', { name: 'Iniciar sesión', exact: true }).evaluate(link => {
    const event = new MouseEvent('click', { bubbles: true, cancelable: true, ctrlKey: true });
    // Check after the router, then suppress the browser's real new-tab action in this test.
    let handled = false;
    document.addEventListener('click', () => { handled = event.defaultPrevented; event.preventDefault(); }, { once: true });
    link.dispatchEvent(event);
    return handled;
  });
  expect(intercepted).toBe(false);
  await expect(page).toHaveURL(/\/register$/);
  await page.getByRole('link', { name: 'Iniciar sesión', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
});

test('FAQ reversals settle to the requested answer and anchors remain in the same page', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await fixtures(page, { authenticated: false });
  await page.goto('/');
  const question = page.getByRole('button', { name: '¿Puedo elegir el modelo que responde?' });
  await question.click();
  await expect(question).toHaveAttribute('aria-expanded', 'true');
  await question.click();
  await question.click();
  const answer = page.locator('#mk-faq-1');
  await expect(answer).toBeVisible();
  await expect.poll(() => answer.evaluate(element => element.style.height)).toBe('');
  expect(await answer.evaluate(element => element.getBoundingClientRect().height)).toBeGreaterThan(20);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await question.click();
  await expect(answer).toBeHidden();
  await question.focus();
  await page.keyboard.press('Enter');
  await expect(answer).toBeVisible();
  expect(await answer.evaluate(element => element.getAnimations().length)).toBe(0);
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.getByRole('navigation', { name: 'Navegación del sitio' }).getByRole('link', { name: 'El espacio' }).click();
  await expect(page).toHaveURL(/\/#espacio$/);
  await expect.poll(() => page.locator('#espacio').evaluate(element => Math.abs(element.getBoundingClientRect().top - 24))).toBeLessThan(3);
});

test('sheet follows a drag, cancels a short pull and restores focus after dismissal', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await fixtures(page, { authenticated: false });
  await page.goto('/');
  const trigger = page.getByRole('button', { name: 'Abrir menú' });
  await trigger.click();
  const dialog = page.getByRole('dialog');
  const offset = () => dialog.evaluate(element => new DOMMatrix(getComputedStyle(element).transform).m42);
  await expect.poll(offset).toBeLessThan(.5);
  const grip = await page.locator('.mobile-sheet-grab').boundingBox();
  const x = grip!.x + grip!.width / 2;
  const y = grip!.y + grip!.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x, y + 60, { steps: 4 });
  expect(await offset()).toBeCloseTo(60, 0);
  // A pause removes release momentum: this pull should settle back, not dismiss.
  await page.waitForTimeout(150);
  await page.mouse.up();
  await expect.poll(offset).toBeLessThan(.5);
  await expect(dialog).toBeVisible();
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x, y + 300, { steps: 4 });
  await page.waitForTimeout(150);
  await page.mouse.up();
  await expect(dialog).toHaveCount(0);
  await expect(trigger).toBeFocused();
  expect(await page.evaluate(() => document.body.style.overflow)).not.toBe('hidden');
});

test('a brief flick dismisses the sheet and Escape works with reduced motion', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await fixtures(page, { authenticated: false });
  await page.goto('/');
  const trigger = page.getByRole('button', { name: 'Abrir menú' });
  await trigger.click();
  const dialog = page.getByRole('dialog');
  await expect.poll(() => dialog.evaluate(element => new DOMMatrix(getComputedStyle(element).transform).m42)).toBeLessThan(.5);
  const grip = await page.locator('.mobile-sheet-grab').boundingBox();
  const x = grip!.x + grip!.width / 2;
  const y = grip!.y + grip!.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x, y + 20);
  await page.waitForTimeout(16);
  await page.mouse.move(x, y + 60);
  await page.mouse.up();
  await expect(dialog).toHaveCount(0);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await trigger.click();
  expect(await dialog.evaluate(element => new DOMMatrix(getComputedStyle(element).transform).m42)).toBe(0);
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
  await expect(trigger).toBeFocused();
});

test('password visibility is available on desktop and mobile model selection does not summon the keyboard', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await fixtures(page, { authenticated: false });
  await page.goto('/login');
  const password = page.getByLabel('Contraseña', { exact: true });
  await password.fill('Clave123');
  await page.getByRole('button', { name: 'Mostrar contraseña' }).click();
  await expect(password).toHaveAttribute('type', 'text');
  await page.getByRole('button', { name: 'Ocultar contraseña' }).click();
  await expect(password).toHaveAttribute('type', 'password');
  await page.unrouteAll({ behavior: 'wait' });
  await fixtures(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/nuevo-chat');
  await page.getByRole('combobox', { name: 'Modelo de respuesta' }).click();
  await expect(page.getByRole('dialog', { name: 'Elegí un modelo' })).toBeVisible();
  await expect(page.getByRole('searchbox', { name: 'Buscar un modelo' })).not.toBeFocused();
  await page.getByRole('searchbox', { name: 'Buscar un modelo' }).click();
  await expect(page.getByRole('searchbox', { name: 'Buscar un modelo' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByRole('combobox', { name: 'Modelo de respuesta' })).toBeFocused();
});

for (const width of [320, 390]) {
  test(`public landing and authentication at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await fixtures(page, { authenticated: false });
    await page.goto('/');
    await expect(page.locator('.mk-mobile-dock')).toBeVisible();
    await capture(page, `landing-${width}`);
    await page.getByRole('button', { name: 'Abrir menú' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: 'Cerrar panel' }).click();
    await page.locator('.mk-mobile-stage-tabs button').nth(1).click();
    await expect(page.locator('.mk-chapter--active')).toHaveAttribute('data-stage', '1');
    await capture(page, `landing-method-${width}`);
    await page.locator('.mk-mobile-dock button').click();
    await expect(page).toHaveURL(/\/login$/);
    await page.getByLabel('Contraseña', { exact: true }).fill('Clave123');
    await page.getByRole('button', { name: 'Mostrar contraseña' }).click();
    await expect(page.getByLabel('Contraseña', { exact: true })).toHaveAttribute('type', 'text');
    await capture(page, `login-${width}`);
    await page.goto('/register');
    await capture(page, `register-${width}`);
  });

  test(`mobile navigation, real chat controls and account at ${width}px`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setViewportSize({ width, height: 844 });
    await fixtures(page);
    await page.goto('/nuevo-chat');
    await expect(page.locator('.chat-mobile-welcome')).toBeVisible();
    await expect(page.getByRole('combobox', { name: 'Modelo de respuesta' })).toBeEnabled();
    await expect(page.locator('.chat-model-trigger-copy')).toBeHidden();
    await expect(page.locator('.chat-footnote')).toBeHidden();
    const composer = await page.locator('.chat-composer').boundingBox();
    expect(composer!.height).toBeLessThan(180);
    await capture(page, `chat-${width}`);
    await page.getByRole('button', { name: 'Información del chat' }).click();
    await expect(page.getByRole('dialog', { name: 'Información del chat' })).toContainText('GPT OSS 20B');
    await expect(page.getByRole('dialog')).toContainText('antes de enviarla al modelo');
    await page.getByRole('button', { name: 'Cerrar panel' }).click();
    await page.getByRole('combobox', { name: 'Modelo de respuesta' }).click();
    await expect(page.getByRole('dialog', { name: 'Elegí un modelo' })).toBeVisible();
    await page.getByRole('searchbox', { name: 'Buscar un modelo' }).fill('Qwen');
    await capture(page, `models-${width}`);
    await page.getByRole('option').click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await page.getByLabel('Mensaje para BloqIA').fill('¿Qué es una API?');
    await page.getByRole('button', { name: 'Enviar mensaje' }).click();
    await expect(page.getByRole('article', { name: 'Respuesta de BloqIA' })).toBeVisible();
    await capture(page, `response-${width}`);
    await page.getByRole('button', { name: /Ver clasificación/ }).click();
    await expect(page.getByRole('dialog')).toContainText('98 %');
    await capture(page, `classification-${width}`);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await page.getByRole('navigation', { name: 'Navegación móvil' }).getByRole('link', { name: 'Chats' }).click();
    await expect(page.getByRole('searchbox', { name: 'Buscar conversaciones' })).toBeVisible();
    await page.reload();
    await expect(page.getByRole('searchbox', { name: 'Buscar conversaciones' })).toBeVisible();
    await capture(page, `history-${width}`);
    await page.getByRole('searchbox', { name: 'Buscar conversaciones' }).fill('inexistente');
    await expect(page.getByText('No encontramos ese chat. Probá con otra palabra.')).toBeVisible();
    await page.getByRole('searchbox', { name: 'Buscar conversaciones' }).fill('');
    await page.getByRole('button', { name: `Eliminar ${conversation.title}` }).click();
    await expect(page.getByRole('dialog', { name: '¿Eliminar este chat?' })).toBeVisible();
    await page.getByRole('button', { name: 'Conservar chat' }).click();
    await expect(page.getByRole('button', { name: conversation.title, exact: false }).first()).toBeVisible();
    await page.getByRole('button', { name: `Eliminar ${conversation.title}` }).click();
    await page.getByRole('button', { name: 'Eliminar conversación', exact: true }).click();
    await expect(page.locator('.chat-mobile-welcome')).toBeVisible();
    await page.getByRole('navigation', { name: 'Navegación móvil' }).getByRole('link', { name: 'Cuenta' }).click();
    await expect(page.getByText(profile.mail, { exact: true })).toBeVisible();
    await capture(page, `account-${width}`);
    await page.goto('/perfil');
    await expect(page.getByLabel('Nombre')).toHaveValue(profile.displayName);
    await capture(page, `profile-${width}`);
    await page.goto('/perfil-tecnico');
    await expect(page.locator('.provider-mobile-trigger')).toHaveCount(5);
    await capture(page, `providers-${width}`);
    await page.locator('.provider-mobile-trigger').filter({ hasText: 'Groq' }).click();
    await expect(page.getByRole('dialog', { name: 'Groq' })).toBeVisible();
    await capture(page, `provider-sheet-${width}`);
    await page.getByRole('button', { name: 'Cerrar panel' }).click();
    await page.goto('/actividad');
    await expect(page.getByRole('heading', { name: 'Actividad y límites' })).toBeVisible();
    await expect(page.locator('.usage-metrics')).toBeVisible();
    await capture(page, `activity-${width}`);
    expect(errors).toEqual([]);
  });
}

test('mobile confirmation, cancellation and usage lock remain actionable', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 667 });
  await fixtures(page);
  await page.goto('/nuevo-chat');
  await expect(page.getByRole('combobox', { name: 'Modelo de respuesta' })).toBeEnabled();
  await page.getByLabel('Mensaje para BloqIA').fill('Consulta personal informativa');
  await page.getByRole('button', { name: 'Enviar mensaje' }).click();
  await expect(page.getByRole('button', { name: 'Usar 1 respuesta' })).toBeVisible();
  await capture(page, 'confirmation');
  await page.getByRole('button', { name: 'Cancelar', exact: true }).click();
  await expect(page.getByLabel('Mensaje para BloqIA')).toHaveValue('Consulta personal informativa');
  await page.getByLabel('Mensaje para BloqIA').focus();
  await page.evaluate(() => {
    Object.defineProperty(window.visualViewport, 'height', { configurable: true, value: 390 });
    window.visualViewport?.dispatchEvent(new Event('resize'));
  });
  await expect(page.locator('.bloq-bottom-nav')).toBeHidden();
  const send = await page.getByRole('button', { name: 'Enviar mensaje' }).boundingBox();
  expect(send!.y + send!.height).toBeLessThanOrEqual(390);
  await capture(page, 'keyboard-viewport');
  await page.unrouteAll({ behavior: 'wait' });
  await fixtures(page, { blocked: true });
  await page.reload();
  await expect(page.locator('.chat-lock-panel')).toBeVisible();
  await expect(page.getByLabel('Mensaje para BloqIA')).toBeHidden();
  await capture(page, 'blocked');
});

test('desktop keeps its sidebar and inline controls', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await fixtures(page);
  await page.goto('/nuevo-chat');
  await expect(page.locator('.bloq-rail')).toBeVisible();
  await expect(page.locator('.bloq-bottom-nav')).toBeHidden();
  await expect(page.getByRole('heading', { name: 'Clasificá tu consulta.' })).toBeVisible();
  await page.getByRole('combobox', { name: 'Modelo de respuesta' }).click();
  await expect(page.getByRole('listbox')).toBeVisible();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await capture(page, 'desktop-chat');
  await page.goto('/');
  await capture(page, 'desktop-landing');
});

test('chat errors can be dismissed and reappear after another failed attempt', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await fixtures(page);
  await page.route('**/api/chat/conversations/*/messages', route => route.fulfill({ status: 503, json: { message: 'No pudimos generar la respuesta. Intentá nuevamente.' } }));
  await page.goto('/nuevo-chat');
  await expect(page.getByRole('combobox', { name: 'Modelo de respuesta' })).toBeEnabled();
  await page.getByLabel('Mensaje para BloqIA').fill('¿Qué es una API?');
  for (let attempt = 0; attempt < 2; attempt++) {
    await page.getByRole('button', { name: 'Enviar mensaje' }).click();
    const notice = page.getByRole('alert').filter({ hasText: 'No pudimos generar' });
    await expect(notice).toBeVisible();
    await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1');
    await capture(page, `dismissible-error-${attempt}`);
    await notice.getByRole('button', { name: 'Cerrar aviso' }).click();
    await expect(notice).toHaveCount(0);
    await expect(page.getByLabel('Mensaje para BloqIA')).toHaveValue('¿Qué es una API?');
  }
});
