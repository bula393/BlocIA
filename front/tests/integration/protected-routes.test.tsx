import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Router } from '../../src/app/router';
import { createSessionJwt, setRouteJwt } from '../../src/app/routeGuard';

function renderAt(path: string) {
  window.history.pushState({}, '', path);
  render(<QueryClientProvider client={new QueryClient()}><Router /></QueryClientProvider>);
}

afterEach(() => setRouteJwt(null));

test('profile route does not render protected content without valid jwt', () => {
  renderAt('/perfil');
  expect(screen.getByRole('heading', { name: 'Iniciá sesión para seguir' })).toBeInTheDocument();
  expect(screen.queryByText('Cargando perfil...')).not.toBeInTheDocument();
});

test('technical profile route does not render protected content without valid jwt', () => {
  renderAt('/perfil-tecnico');
  expect(screen.getByRole('heading', { name: 'Iniciá sesión para seguir' })).toBeInTheDocument();
  expect(screen.queryByText('Cargando proveedores...')).not.toBeInTheDocument();
});

test('valid jwt allows protected route rendering', () => {
  setRouteJwt(createSessionJwt('usuario.demo@example.com', 60));
  renderAt('/perfil');
  expect(screen.getByRole('heading', { name: 'Perfil' })).toBeInTheDocument();
});
