import { expect, test } from '@playwright/test';

test('Google callback is handled by the frontend instead of the API proxy', async ({ page }) => {
  await page.goto('/auth/google/callback?error=state');

  await expect(page.getByRole('heading', { name: 'No se pudo completar el acceso' })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveText('La solicitud de acceso con Google venció. Volvé al acceso e intentá nuevamente.');
  await expect(page.getByRole('link', { name: 'Volver al acceso' })).toHaveAttribute('href', '/login');
});
