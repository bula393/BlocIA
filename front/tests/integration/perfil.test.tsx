import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { Perfil } from '../../src/pages/Perfil';
import { updateProfile } from '../../src/api/profile';

vi.mock('../../src/api/profile', () => ({
  getProfile: vi.fn(async () => ({ mail: 'ana@example.com', age: 27, profession: 'Estudiante', displayName: 'Ana', loginProviderStatus: 'password', technicalProfileStatus: 'not-configured' })),
  updateProfile: vi.fn(async (changes) => ({ mail: 'ana@example.com', age: 27, profession: 'Estudiante', displayName: 'Ana', loginProviderStatus: 'password', technicalProfileStatus: 'not-configured', ...changes }))
}));

test('shows saved profile values and saves an edited or cleared name', async () => {
  const user = userEvent.setup();
  render(<QueryClientProvider client={new QueryClient()}><Perfil /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Perfil' })).toBeInTheDocument();
  expect(await screen.findByDisplayValue('Ana')).toBeInTheDocument();
  expect(screen.getByDisplayValue('27')).toBeInTheDocument();
  expect(screen.getByDisplayValue('Estudiante')).toBeInTheDocument();
  expect(screen.getByText('ana@example.com')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Guardar cambios' })).toBeDisabled();

  await user.clear(screen.getByRole('textbox', { name: 'Nombre visible' }));
  await user.click(screen.getByRole('button', { name: 'Guardar cambios' }));
  await waitFor(() => expect(vi.mocked(updateProfile).mock.calls[0]?.[0]).toEqual({ age: 27, profession: 'Estudiante', displayName: '' }));
  expect(await screen.findByText('Perfil actualizado.')).toBeInTheDocument();
});
