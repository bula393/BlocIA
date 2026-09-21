import { expect, test } from '@playwright/test';

test('technical profile uses semantic status indicators', async ({ page }) => {
  await page.route('**/technical-profile/providers', async (route) => {
    await route.fulfill({
      json: {
        providers: [
          {
            providerId: 'openai',
            name: 'OpenAI',
            status: 'available',
            tokenStatus: { providerId: 'openai', status: 'configured', maskedTokenLabel: 'tok***123' },
            models: [{ modelId: 'gpt-4o-mini', displayName: 'GPT-4o mini', availabilityStatus: 'available', capabilities: ['chat'] }]
          }
        ]
      }
    });
  });
  await page.goto('/perfil-tecnico');
  await expect(page.locator('.bloq-shell')).toBeVisible();
  await expect(page.locator('.bloq-status-line').first()).toHaveCSS('border-left-width', '3px');
});
