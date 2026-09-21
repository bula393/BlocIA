import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Login } from '../../src/pages/Login';

test('renders login form and Google action', () => {
  render(<QueryClientProvider client={new QueryClient()}><Login /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument();
  expect(screen.getByText('Continuar con Google')).toBeInTheDocument();
});
