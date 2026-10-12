import { expect, test } from '@playwright/test';

test.use({ serviceWorkers: 'block' });

test('technical profile verifies email before connecting a personal key on desktop and mobile', async ({ page }) => {
  await page.addInitScript(() => {
    const encode = (value: object) => btoa(JSON.stringify(value)).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${encode({ alg: 'none' })}.${encode({ sub: 'persona@example.com', exp: 4102444800 })}.signature`;
  });
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  let verified = false;
  let sent = false;
  let saves = 0;
  const status = () => ({ verified, email: 'una.persona.con.un.correo.largo@example.com', expiresInSeconds: sent && !verified ? 600 : null, resendInSeconds: sent && !verified ? 60 : 0 });
  await page.route('**/technical-profile/**', async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith('/email-verification/request')) {
      sent = true;
      await route.fulfill({ json: status() });
    } else if (path.endsWith('/email-verification/confirm')) {
      if (route.request().postDataJSON().code !== '123456') {
        await route.fulfill({ status: 400, json: { message: 'El código no es correcto. Revisalo e intentá nuevamente.' } });
      } else {
        verified = true;
        await route.fulfill({ json: status() });
      }
    } else if (path.endsWith('/email-verification')) {
      await route.fulfill({ json: status() });
    } else if (path.endsWith('/models')) {
      await route.fulfill({ json: { providerId: 'groq', source: 'default', message: 'Usando la clave del proyecto.', models: [] } });
    } else if (path.endsWith('/tokens')) {
      expect(verified).toBe(true);
      expect(route.request().postDataJSON()).toEqual({ providerId: 'groq', token: 'clave-de-prueba' });
      saves += 1;
      await route.fulfill({ json: { providerId: 'groq', status: 'configured', maskedTokenLabel: '***ueba' } });
    } else if (path.endsWith('/providers')) {
      await route.fulfill({ json: { providers: [{ providerId: 'groq', name: 'Groq', status: 'available', defaultTokenAvailable: true, tokenStatus: { providerId: 'groq', status: saves ? 'configured' : 'not-configured' }, models: [] }] } });
    } else {
      await route.fulfill({ status: 404, json: { message: 'Ruta no esperada' } });
    }
  });
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/perfil-tecnico');
  const token = page.getByLabel('Clave API Groq');
  await token.fill('clave-de-prueba');
  const save = page.getByRole('button', { name: 'Conectar clave', exact: true });
  await expect(save).toBeDisabled();
  await page.getByRole('button', { name: 'Enviar código', exact: true }).click();
  const code = page.getByLabel('Código de 6 dígitos');
  await expect(code).toBeFocused();
  await expect(page.getByRole('button', { name: 'Reenviar código', exact: true })).toBeDisabled();
  await page.screenshot({ path: 'test-results/technical-email-desktop.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#verificacion-correo').scrollIntoViewIfNeeded();
  await page.screenshot({ path: 'test-results/technical-email-mobile.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await code.fill('111111');
  await page.getByRole('button', { name: 'Verificar correo', exact: true }).click();
  await expect(page.getByRole('alert')).toHaveText(/El código no es correcto/);
  await page.getByRole('button', { name: /Groq.*Conexión del proyecto disponible/ }).click();
  await expect(token).toHaveValue('clave-de-prueba');
  await expect(save).toBeDisabled();
  expect(saves).toBe(0);
  await page.getByRole('button', { name: 'Cerrar panel', exact: true }).click();
  await code.fill('123456');
  await page.getByRole('button', { name: 'Verificar correo', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Correo verificado', exact: true })).toBeVisible();
  await page.getByRole('button', { name: /Groq.*Conexión del proyecto disponible/ }).click();
  await expect(token).toHaveValue('clave-de-prueba');
  await expect(save).toBeEnabled();
  await save.click();
  await expect(token).toHaveValue('');
  expect(saves).toBe(1);
  expect(errors).toEqual([]);
});

for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
  test(`Google account connects, handles quota errors, and disconnects at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.addInitScript(() => {
      const encode = (value: object) => btoa(JSON.stringify(value)).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
      (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ = `${encode({ alg: 'none' })}.${encode({ sub: 'persona@example.com', exp: 4102444800 })}.signature`;
    });
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    let connected = false;
    let ready = false;
    let probes = 0;
    let starts = 0;
    const account = () => ({ available: true, connected, ready, needsReconnect: false, email: connected ? 'mi.cuenta.personal.con.un.nombre.largo@gmail.com' : null, projectId: ready ? 'my-google-project' : null, projectName: ready ? 'Mi proyecto personal' : null });
    await page.route('**/technical-profile/**', async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path.endsWith('/email-verification')) return route.fulfill({ json: { verified: true, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 } });
      if (path.endsWith('/google/start')) {
        starts += 1;
        return route.fulfill({ json: { authorizationUrl: 'http://127.0.0.1:4190/simulated-google-consent' } });
      }
      if (path.endsWith('/google/projects')) return route.fulfill({ json: { projects: [{ projectId: 'my-google-project', name: 'Mi proyecto personal' }] } });
      if (path.endsWith('/google/project')) {
        expect(route.request().postDataJSON()).toEqual({ projectId: 'my-google-project' });
        probes += 1;
        if (probes === 1) return route.fulfill({ status: 409, json: { message: 'Google no tiene cupo disponible para esta prueba. Intentá más tarde.' } });
        ready = true;
        return route.fulfill({ json: account() });
      }
      if (path.endsWith('/google')) {
        if (route.request().method() === 'DELETE') {
          connected = false;
          ready = false;
          return route.fulfill({ json: { disconnected: true, revoked: true } });
        }
        return route.fulfill({ json: account() });
      }
      if (path.endsWith('/providers')) return route.fulfill({ json: { providers: [{ providerId: 'google', name: 'Google AI', status: 'available', defaultTokenAvailable: true, tokenStatus: { providerId: 'google', status: 'not-configured' }, models: [], oauthConnection: account() }] } });
      if (path.endsWith('/models')) return route.fulfill({ json: { providerId: 'google', source: connected ? 'oauth' : 'default', models: ready ? [{ modelId: 'gemini-test-flash', displayName: 'Gemini Flash', availabilityStatus: 'available', capabilities: ['chat'] }] : [], message: ready ? 'Cuenta Google conectada.' : 'Elegí una conexión para usar Gemini.' } });
      return route.fulfill({ status: 404, json: { message: 'Ruta no esperada' } });
    });
    await page.route('**/simulated-google-consent', (route) => route.fulfill({ contentType: 'text/html', body: '<h1>Autorización de Google simulada para la prueba</h1>' }));
    await page.goto('/perfil-tecnico');
    if (viewport.width < 760) await page.getByRole('button', { name: /Google AI.*Conexión del proyecto disponible/ }).click();
    const connect = page.getByRole('button', { name: 'Conectar con Google', exact: true });
    await expect(connect).toBeEnabled();
    await expect(page.getByLabel('Clave API Google AI')).not.toBeVisible();
    await connect.click();
    await expect(page).toHaveURL(/simulated-google-consent/);
    expect(starts).toBe(1);
    connected = true;
    await page.goto('/perfil-tecnico?google=connected#provider-google');
    await expect(page.getByLabel('Dónde usar Gemini')).toHaveValue('my-google-project');
    expect(probes).toBe(0);
    await expect(page.getByText(/La comprobación envía una consulta breve/)).toBeVisible();
    await page.locator('.provider-account').screenshot({ path: `test-results/google-connect-${viewport.width}.png` });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.getByRole('button', { name: 'Comprobar y usar Gemini' }).click();
    const error = page.getByRole('alert');
    await expect(error).toHaveText(/Google no tiene cupo/);
    await error.getByRole('button', { name: 'Cerrar aviso' }).click();
    await expect(error).not.toBeVisible();
    await page.getByRole('button', { name: 'Comprobar y usar Gemini' }).click();
    await expect(page.getByRole('heading', { name: 'Tu cuenta está lista' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Ir al chat' })).toBeVisible();
    await expect(page.getByLabel('Dónde usar Gemini')).not.toBeVisible();
    await page.locator('.provider-account').screenshot({ path: `test-results/google-ready-${viewport.width}.png` });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(probes).toBe(2);
    await page.getByText('Usar una clave API · avanzado', { exact: true }).click();
    await expect(page.getByLabel('Clave API Google AI')).toBeDisabled();
    await page.getByRole('button', { name: 'Desconectar cuenta Google' }).click();
    await expect(connect).toBeEnabled();
    await expect(page.getByLabel('Clave API Google AI')).toBeEnabled();
    expect(errors).toEqual([]);
  });
}
