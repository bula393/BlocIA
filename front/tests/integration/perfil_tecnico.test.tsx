import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, vi } from 'vitest';
import { PerfilTecnico } from '../../src/pages/PerfilTecnico';
import { ApiRequestError } from '../../src/api/client';
import { confirmEmailVerification, getEmailVerification, listAvailableModels, listTechnicalProviders, removeProviderToken, requestEmailVerification, saveProviderToken } from '../../src/api/technicalProfile';

vi.mock('../../src/api/technicalProfile', () => ({
  listTechnicalProviders: vi.fn(async () => ({ providers: [{ providerId: 'openrouter', name: 'OpenRouter', status: 'available', tokenStatus: { providerId: 'openrouter', status: 'not-configured' }, models: [] }] })),
  listAvailableModels: vi.fn(async () => ({ providerId: 'openrouter', source: 'catalog', message: 'Conectá una clave.', models: [] })),
  saveProviderToken: vi.fn(async () => ({ providerId: 'openrouter', status: 'configured', maskedTokenLabel: '***123' })),
  removeProviderToken: vi.fn(async () => undefined),
  getEmailVerification: vi.fn(async () => ({ verified: true, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 })),
  requestEmailVerification: vi.fn(async () => ({ verified: false, email: 'persona@example.com', expiresInSeconds: 600, resendInSeconds: 60 })),
  confirmEmailVerification: vi.fn(async () => ({ verified: true, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 }))
}));

beforeEach(() => vi.clearAllMocks());

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

test('requires an email code before saving a personal key and preserves the draft after an incorrect code', async () => {
  const user = userEvent.setup();
  vi.mocked(getEmailVerification)
    .mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 })
    .mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: 600, resendInSeconds: 60 });
  vi.mocked(confirmEmailVerification).mockRejectedValueOnce(new ApiRequestError('El código no es correcto. Revisalo e intentá nuevamente.', 400));
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  const token = await screen.findByLabelText('Clave API OpenRouter');
  await user.type(token, 'sk-personal');
  const save = screen.getByRole('button', { name: 'Conectar clave' });
  expect(save).toBeDisabled();
  expect(saveProviderToken).not.toHaveBeenCalled();
  await user.click(screen.getByRole('button', { name: 'Enviar código', exact: true }));
  await waitFor(() => expect(requestEmailVerification).toHaveBeenCalledTimes(1));
  expect(screen.getByRole('button', { name: 'Reenviar código', exact: true })).toBeDisabled();
  const code = await screen.findByLabelText('Código de 6 dígitos');
  await waitFor(() => expect(code).toHaveFocus());
  await user.type(code, '123456');
  await user.click(screen.getByRole('button', { name: 'Verificar correo', exact: true }));
  expect(await screen.findByRole('alert')).toHaveTextContent('El código no es correcto');
  expect(code).toHaveValue('123456');
  expect(token).toHaveValue('sk-personal');
  expect(save).toBeDisabled();
  await user.clear(code);
  await user.type(code, '654321');
  await user.click(screen.getByRole('button', { name: 'Verificar correo', exact: true }));
  expect(await screen.findByRole('heading', { name: 'Correo verificado' })).toBeInTheDocument();
  await waitFor(() => expect(save).toBeEnabled());
  await user.click(save);
  await waitFor(() => expect(saveProviderToken).toHaveBeenCalledWith('openrouter', 'sk-personal'));
  expect(vi.mocked(confirmEmailVerification).mock.calls.at(-1)?.[0]).toBe('654321');
  await waitFor(() => expect(token).toHaveValue(''));
});

test('allows removing an existing key while the email is unverified', async () => {
  const user = userEvent.setup();
  vi.mocked(getEmailVerification).mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 });
  vi.mocked(listTechnicalProviders).mockResolvedValueOnce({ providers: [{ providerId: 'openrouter', name: 'OpenRouter', status: 'available', tokenStatus: { providerId: 'openrouter', status: 'configured', maskedTokenLabel: '***123' }, models: [] }] });
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  const remove = await screen.findByRole('button', { name: 'Quitar clave' });
  expect(remove).toBeEnabled();
  await user.click(remove);
  await waitFor(() => expect(vi.mocked(removeProviderToken).mock.calls[0]?.[0]).toBe('openrouter'));
});

test('requires a new code when the previous one expired', async () => {
  vi.mocked(getEmailVerification).mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: 0, resendInSeconds: 0 });
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  expect(await screen.findByText('El código venció. Pedí uno nuevo para continuar.')).toBeInTheDocument();
  expect(screen.getByLabelText('Código de 6 dígitos')).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Verificar correo', exact: true })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Reenviar código', exact: true })).toBeEnabled();
  expect(screen.getByRole('button', { name: 'Conectar clave' })).toBeDisabled();
});

test('keeps saving locked when verification cannot load and lets the user retry', async () => {
  const user = userEvent.setup();
  vi.mocked(getEmailVerification).mockRejectedValueOnce(new ApiRequestError('No pudimos comprobar tu correo. Volvé a intentarlo.', 503));
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  expect(await screen.findByRole('alert')).toHaveTextContent('No pudimos comprobar tu correo');
  await user.type(screen.getByLabelText('Clave API OpenRouter'), 'sk-personal');
  const save = screen.getByRole('button', { name: 'Conectar clave' });
  expect(save).toBeDisabled();
  await user.click(screen.getByRole('button', { name: 'Volver a comprobar' }));
  await waitFor(() => expect(save).toBeEnabled());
  expect(saveProviderToken).not.toHaveBeenCalled();
});

test('shows a mail delivery failure without clearing a personal key draft', async () => {
  const user = userEvent.setup();
  const unverified = { verified: false, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 };
  vi.mocked(getEmailVerification).mockResolvedValueOnce(unverified).mockResolvedValueOnce(unverified);
  vi.mocked(requestEmailVerification).mockRejectedValueOnce(new ApiRequestError('El envío de correos no está configurado. Contactá al administrador.', 503));
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  const token = await screen.findByLabelText('Clave API OpenRouter');
  await user.type(token, 'sk-personal');
  await user.click(screen.getByRole('button', { name: 'Enviar código', exact: true }));
  expect(await screen.findByRole('alert')).toHaveTextContent('El envío de correos no está configurado. Contactá al administrador.');
  expect(token).toHaveValue('sk-personal');
  expect(screen.getByRole('button', { name: 'Conectar clave' })).toBeDisabled();
  expect(saveProviderToken).not.toHaveBeenCalled();
});

test('keeps the error visible and offers a fresh code when confirmation exhausts the challenge', async () => {
  const user = userEvent.setup();
  vi.mocked(getEmailVerification)
    .mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: 600, resendInSeconds: 0 })
    .mockResolvedValueOnce({ verified: false, email: 'persona@example.com', expiresInSeconds: null, resendInSeconds: 0 });
  vi.mocked(confirmEmailVerification).mockRejectedValueOnce(new ApiRequestError('Alcanzaste el límite de intentos. Pedí otro código.', 400));
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);

  await user.type(await screen.findByLabelText('Código de 6 dígitos'), '111111');
  await user.click(screen.getByRole('button', { name: 'Verificar correo', exact: true }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Alcanzaste el límite de intentos');
  await waitFor(() => expect(screen.queryByLabelText('Código de 6 dígitos')).not.toBeInTheDocument());
  expect(screen.getByRole('button', { name: 'Enviar código', exact: true })).toBeEnabled();
  expect(screen.getByRole('alert')).toHaveTextContent('Alcanzaste el límite de intentos');
});
