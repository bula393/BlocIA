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
