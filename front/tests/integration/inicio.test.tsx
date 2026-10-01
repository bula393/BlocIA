import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Inicio } from '../../src/pages/Inicio';
import { createSessionJwt, setRouteJwt } from '../../src/app/routeGuard';

afterEach(() => setRouteJwt(null));

test('renders public start page without authentication', () => {
  render(<QueryClientProvider client={new QueryClient()}><Inicio /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Tu espacio para pensar con criterio.' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'BloqIA, inicio' })).toBeInTheDocument();
  expect(screen.getByText('Iniciar sesión').closest('a')).toHaveAttribute('href', '/login');
  expect(screen.getByRole('link', { name: 'Inicio', exact: true })).toHaveAttribute('aria-current', 'page');
  expect(screen.getByRole('complementary', { name: 'Ejemplo ilustrativo de una conversación' })).toHaveTextContent('Ejemplo');
  expect(screen.getByRole('region', { name: 'Un espacio simple, a tu manera.' })).toBeInTheDocument();
});

test('replaces public actions with chat and technical setup for an authenticated user', () => {
  setRouteJwt(createSessionJwt('usuario@example.com'));
  render(<QueryClientProvider client={new QueryClient()}><Inicio /></QueryClientProvider>);

  expect(screen.getByRole('link', { name: 'Nuevo chat' })).toHaveAttribute('href', '/nuevo-chat');
  expect(screen.getByRole('link', { name: 'Configurar técnico' })).toHaveAttribute('href', '/perfil-tecnico');
  expect(screen.queryByRole('link', { name: 'Iniciar sesión' })).not.toBeInTheDocument();
});
