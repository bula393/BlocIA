import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { PerfilTecnico } from '../../src/pages/PerfilTecnico';
import { ApiRequestError } from '../../src/api/client';
import { listAvailableModels, listTechnicalProviders, saveProviderToken } from '../../src/api/technicalProfile';

vi.mock('../../src/api/technicalProfile', () => ({
  listTechnicalProviders: vi.fn(async () => ({ providers: [{ providerId: 'openrouter', name: 'OpenRouter', status: 'available', tokenStatus: { providerId: 'openrouter', status: 'not-configured' }, models: [] }] })),
  listAvailableModels: vi.fn(async () => ({ providerId: 'openrouter', source: 'catalog', message: 'Conectá una clave.', models: [] })),
  saveProviderToken: vi.fn(async () => ({ providerId: 'openrouter', status: 'configured', maskedTokenLabel: '***123' })),
  removeProviderToken: vi.fn(async () => undefined)
}));

test('renders technical profile title', () => {
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Proveedores y modelos' })).toBeInTheDocument();
});

test('offers free model setup and clears an entered API key after saving', async () => {
  const user = userEvent.setup();
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);
  expect(await screen.findByRole('heading', { name: 'OpenRouter' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /Abrir consola de claves/ })).toHaveAttribute('href', 'https://openrouter.ai/settings/keys');
  const field = screen.getByLabelText('Clave API OpenRouter');
  await user.type(field, 'sk-personal');
  await user.click(screen.getByRole('button', { name: 'Conectar clave' }));
  await waitFor(() => expect(saveProviderToken).toHaveBeenCalledWith('openrouter', 'sk-personal'));
  await waitFor(() => expect(field).toHaveValue(''));
});

test('shows when a project default token is available', async () => {
  vi.mocked(listTechnicalProviders).mockResolvedValueOnce({ providers: [{
    providerId: 'openrouter',
    name: 'OpenRouter',
    status: 'available',
    tokenStatus: { providerId: 'openrouter', status: 'not-configured' },
    defaultTokenAvailable: true,
    models: []
  }] });
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  expect(await screen.findByText('Token predeterminado del proyecto')).toBeInTheDocument();
});

test('shows the provider catalog network error returned by the backend', async () => {
  const message = 'El entorno del servidor bloqueó la conexión saliente con Google AI.';
  vi.mocked(listTechnicalProviders).mockResolvedValueOnce({ providers: [{
    providerId: 'google',
    name: 'Google AI',
    status: 'available',
    tokenStatus: { providerId: 'google', status: 'not-configured' },
    defaultTokenAvailable: true,
    models: []
  }] });
  vi.mocked(listAvailableModels).mockRejectedValueOnce(new ApiRequestError(message, 502));
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  expect(await screen.findByText(message)).toBeInTheDocument();
});
