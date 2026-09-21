import { expect, test } from '@playwright/test';

test('Google callback is handled by the frontend instead of the API proxy', async ({ page }) => {
  await page.goto('/auth/google/callback?error=state');

  await expect(page.getByRole('heading', { name: 'Conectando con Google' })).toBeVisible();
  await expect(page.getByText('Google no pudo completar el acceso. Intentá nuevamente.')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Volver al acceso' })).toHaveAttribute('href', '/login');
});
