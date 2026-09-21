import { expect, test } from '@playwright/test';

test('login is public sparse and has one primary action', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  await expect(page.locator('button[data-primary="true"]')).toHaveCount(1);
  await expect(page.getByRole('link', { name: 'Crear cuenta' })).toBeVisible();
  await expect(page.getByRole('link', { name: /^Inicio$/ })).toBeVisible();
});

test('register is public sparse and has one primary action', async ({ page }) => {
  await page.goto('/register');
  await expect(page.getByRole('heading', { name: 'Crear cuenta' })).toBeVisible();
  await expect(page.locator('button[data-primary="true"]')).toHaveCount(1);
  await expect(page.locator('.auth-secondary').getByRole('link', { name: 'Iniciar sesión' })).toBeVisible();
  await expect(page.getByRole('link', { name: /^Inicio$/ })).toBeVisible();
});
