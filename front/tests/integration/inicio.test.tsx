import { fireEvent, render, screen, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { Inicio } from '../../src/pages/Inicio';
import { createSessionJwt, setRouteJwt } from '../../src/app/routeGuard';
import { navigateTo } from '../../src/app/navigation';

vi.mock('../../src/app/navigation', () => ({ navigateTo: vi.fn() }));

afterEach(() => {
  setRouteJwt(null);
  vi.clearAllMocks();
});

test('renders public start page without authentication', () => {
  const { container } = render(<QueryClientProvider client={new QueryClient()}><Inicio /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Pensá con más perspectiva.' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'BloqIA, inicio' })).toBeInTheDocument();
  expect(screen.getByLabelText('Ejemplo de conversación según el recorrido')).toHaveTextContent('Ejemplo');
  expect(screen.getByRole('region', { name: 'Menos ruido. Más espacio para pensar.' })).toBeInTheDocument();
  const header = within(container.querySelector('.mk-header') as HTMLElement);
  fireEvent.click(header.getByRole('button', { name: 'Iniciar sesión', exact: true }));
  expect(navigateTo).toHaveBeenLastCalledWith('/login');
  fireEvent.click(header.getByRole('button', { name: 'Crear cuenta', exact: true }));
  expect(navigateTo).toHaveBeenLastCalledWith('/register');
  fireEvent.click(screen.getByRole('button', { name: 'Abrí tu espacio' }));
  expect(navigateTo).toHaveBeenLastCalledWith('/login');
});

test('replaces public actions with chat and technical setup for an authenticated user', () => {
  setRouteJwt(createSessionJwt('usuario@example.com'));
  const { container } = render(<QueryClientProvider client={new QueryClient()}><Inicio /></QueryClientProvider>);

  const header = within(container.querySelector('.mk-header') as HTMLElement);
  expect(header.queryByRole('button', { name: 'Iniciar sesión', exact: true })).not.toBeInTheDocument();
  expect(header.queryByRole('button', { name: 'Crear cuenta', exact: true })).not.toBeInTheDocument();
  fireEvent.click(header.getByRole('button', { name: 'Abrir el chat' }));
  expect(navigateTo).toHaveBeenLastCalledWith('/nuevo-chat');
  fireEvent.click(header.getByRole('button', { name: 'Mi perfil' }));
  expect(navigateTo).toHaveBeenLastCalledWith('/perfil');
  fireEvent.click(screen.getByRole('button', { name: /El modelo lo elegís vos/ }));
  expect(navigateTo).toHaveBeenLastCalledWith('/perfil-tecnico');
});
