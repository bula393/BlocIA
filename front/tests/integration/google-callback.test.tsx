import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, vi } from 'vitest';
import { GoogleCallback } from '../../src/pages/GoogleCallback';
import { completeGoogleRegistration, consumeGoogleSession } from '../../src/api/auth';
import { navigateTo } from '../../src/app/navigation';

vi.mock('../../src/api/auth', () => ({ consumeGoogleSession: vi.fn(), completeGoogleRegistration: vi.fn() }));
vi.mock('../../src/app/navigation', () => ({ navigateTo: vi.fn() }));

const registration = { registrationToken: 'registration-token', missingFields: ['age', 'profession'], prefilledFields: { mail: 'persona@example.com' } };
const session = { user: { mail: 'persona@example.com', age: 24, profession: 'Docente', loginProviderStatus: 'google' as const, technicalProfileStatus: 'not-configured' as const }, accessToken: 'access-token', expiresInSeconds: 3600 };

beforeEach(() => {
  vi.resetAllMocks();
  window.history.replaceState({}, '', '/auth/google/callback');
  vi.mocked(consumeGoogleSession).mockResolvedValue(registration);
  vi.mocked(completeGoogleRegistration).mockResolvedValue(session);
});

test.each([
  ['configuration', 'El acceso con Google todavía no está configurado. Ingresá con tu correo y contraseña o consultá al administrador.'],
  ['state', 'La solicitud de acceso con Google venció. Volvé al acceso e intentá nuevamente.'],
  ['denied', 'Google no pudo completar el acceso. Intentá nuevamente.']
])('explains the Google callback error %s and offers a fresh login', (code, message) => {
  window.history.replaceState({}, '', `/auth/google/callback?error=${code}`);
  render(<GoogleCallback />);

  expect(screen.getByRole('heading', { name: 'No se pudo completar el acceso' })).toBeInTheDocument();
  expect(screen.getByRole('alert')).toHaveTextContent(message);
  expect(screen.getByRole('link', { name: 'Volver al acceso' })).toHaveAttribute('href', '/login');
  expect(consumeGoogleSession).not.toHaveBeenCalled();
});

test('keeps the profile and entered data after a recoverable error and allows correcting and retrying', async () => {
  const user = userEvent.setup();
  vi.mocked(completeGoogleRegistration).mockRejectedValueOnce(new Error('Validation failed'));
  render(<GoogleCallback />);

  const age = await screen.findByLabelText('Edad');
  const profession = screen.getByLabelText('Profesión');
  await user.clear(age);
  await user.type(age, '24');
  await user.type(profession, 'Estudiante');
  await user.click(screen.getByRole('button', { name: 'Completar perfil' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('No se pudieron completar tus datos. Revisalos e intentá de nuevo.');
  expect(screen.getByRole('heading', { name: 'Completá tu perfil' })).toBeInTheDocument();
  expect(age).toHaveValue(24);
  expect(profession).toHaveValue('Estudiante');
  expect(screen.getByRole('button', { name: 'Completar perfil' })).toBeEnabled();
  expect(navigateTo).not.toHaveBeenCalled();
  await user.clear(profession);
  await user.type(profession, 'Docente');
  await user.click(screen.getByRole('button', { name: 'Completar perfil' }));
  await waitFor(() => expect(completeGoogleRegistration).toHaveBeenLastCalledWith('registration-token', 24, 'Docente'));
  await waitFor(() => expect(navigateTo).toHaveBeenCalledWith('/', true));
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

test('prevents duplicate profile completion while a request is pending', async () => {
  const user = userEvent.setup();
  let finish: (value: typeof session) => void = () => {};
  vi.mocked(completeGoogleRegistration).mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
  render(<GoogleCallback />);

  await user.type(await screen.findByLabelText('Profesión'), 'Docente');
  const form = screen.getByRole('button', { name: 'Completar perfil' }).closest('form')!;
  fireEvent.submit(form);
  fireEvent.submit(form);
  expect(completeGoogleRegistration).toHaveBeenCalledTimes(1);
  expect(screen.getByRole('button', { name: 'Completando perfil…' })).toBeDisabled();
  finish(session);
  await waitFor(() => expect(navigateTo).toHaveBeenCalledWith('/', true));
});
