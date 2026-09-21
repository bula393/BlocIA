import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Register } from '../../src/pages/Register';

test('renders register form and password hint', () => {
  render(<QueryClientProvider client={new QueryClient()}><Register /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Crear cuenta' })).toBeInTheDocument();
  expect(screen.getByText(/Minimo 10 caracteres/)).toBeInTheDocument();
});
