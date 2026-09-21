import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Login } from '../../src/pages/Login';
import { Register } from '../../src/pages/Register';

test('login renders without jwt', () => {
  render(<QueryClientProvider client={new QueryClient()}><Login /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument();
});

test('register renders without jwt', () => {
  render(<QueryClientProvider client={new QueryClient()}><Register /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Crear cuenta' })).toBeInTheDocument();
});
