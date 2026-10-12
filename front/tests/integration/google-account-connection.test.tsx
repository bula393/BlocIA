import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { GoogleAccountConnection } from '../../src/features/usuario/components/GoogleAccountConnection';
import { disconnectGoogle, getGoogleConnection, getGoogleProjects, selectGoogleProject, startGoogleConnection } from '../../src/api/providerAccounts';

vi.mock('../../src/api/providerAccounts', () => ({ getGoogleConnection: vi.fn(), getGoogleProjects: vi.fn(), selectGoogleProject: vi.fn(), disconnectGoogle: vi.fn(), startGoogleConnection: vi.fn() }));

const pending = { available: true, connected: true, ready: false, needsReconnect: false, email: 'personal@gmail.com', projectId: null, projectName: null };

beforeEach(() => {
  vi.resetAllMocks();
  window.history.replaceState({}, '', '/perfil-tecnico');
  vi.mocked(getGoogleConnection).mockResolvedValue(pending);
  vi.mocked(getGoogleProjects).mockResolvedValue({ projects: [{ projectId: 'my-project', name: 'Mi proyecto' }] });
});

function show(verified = true) {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })}><GoogleAccountConnection emailVerified={verified} /></QueryClientProvider>);
}

test('preselects a single project but only probes after the user explicitly requests it', async () => {
  const user = userEvent.setup();
  const ready = { ...pending, ready: true, projectId: 'my-project', projectName: 'Mi proyecto' };
  vi.mocked(selectGoogleProject).mockImplementation(async () => { vi.mocked(getGoogleConnection).mockResolvedValue(ready); return ready; });
  show();
  expect(await screen.findByLabelText('Dónde usar Gemini')).toHaveValue('my-project');
  expect(selectGoogleProject).not.toHaveBeenCalled();
  expect(screen.getByText(/La comprobación envía una consulta breve/)).toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Comprobar y usar Gemini' }));
  await waitFor(() => expect(vi.mocked(selectGoogleProject).mock.calls[0][0]).toBe('my-project'));
  expect(await screen.findByRole('heading', { name: 'Tu cuenta está lista' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Ir al chat' })).toHaveAttribute('href', '/nuevo-chat');
  expect(screen.queryByLabelText('Dónde usar Gemini')).not.toBeInTheDocument();
});

test('locks personal authorization and project checking until the BloqIA email is verified', async () => {
  vi.mocked(getGoogleConnection).mockResolvedValue({ ...pending, connected: false, email: null });
  const unverified = show(false);
  expect(await screen.findByRole('button', { name: 'Conectar con Google' })).toBeDisabled();
  expect(startGoogleConnection).not.toHaveBeenCalled();
  unverified.unmount();
  vi.mocked(getGoogleConnection).mockResolvedValue(pending);
  show(false);
  expect(await screen.findByRole('button', { name: 'Comprobar y usar Gemini' })).toBeDisabled();
  expect(selectGoogleProject).not.toHaveBeenCalled();
});

test('keeps the chosen project after a failure and allows dismissing the error and retrying', async () => {
  const user = userEvent.setup();
  vi.mocked(selectGoogleProject).mockRejectedValueOnce(new Error('Google no tiene cupo disponible. Intentá más tarde.'));
  show();
  await user.click(await screen.findByRole('button', { name: 'Comprobar y usar Gemini' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Google no tiene cupo');
  expect(screen.getByLabelText('Dónde usar Gemini')).toHaveValue('my-project');
  await user.click(screen.getByRole('button', { name: 'Cerrar aviso' }));
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Comprobar y usar Gemini' })).toBeEnabled();
});

test('handles an empty project list without offering a broken check', async () => {
  vi.mocked(getGoogleProjects).mockResolvedValue({ projects: [] });
  show();
  expect(await screen.findByText(/Tu cuenta todavía no tiene proyectos disponibles/)).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Comprobar y usar Gemini' })).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: /Preparar Gemini/ })).toHaveAttribute('href', 'https://aistudio.google.com/');
});

test('disconnects locally and offers manual revocation when Google could not confirm it', async () => {
  const user = userEvent.setup();
  vi.mocked(disconnectGoogle).mockImplementation(async () => {
    vi.mocked(getGoogleConnection).mockResolvedValue({ ...pending, connected: false, email: null });
    return { disconnected: true, revoked: false };
  });
  show();
  await user.click(await screen.findByRole('button', { name: 'Desconectar cuenta Google' }));
  expect(await screen.findByRole('link', { name: 'Retirá el acceso en Google' })).toHaveAttribute('href', 'https://myaccount.google.com/connections');
  expect(await screen.findByRole('button', { name: 'Conectar con Google' })).toBeEnabled();
  expect(screen.queryByText('personal@gmail.com')).not.toBeInTheDocument();
});
