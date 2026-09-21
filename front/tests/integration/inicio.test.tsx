import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Inicio } from '../../src/pages/Inicio';

test('renders public start page without authentication', () => {
  render(<QueryClientProvider client={new QueryClient()}><Inicio /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Tu espacio para pensar con criterio.' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'BloqIA, inicio' })).toBeInTheDocument();
  expect(screen.getByText('Iniciar sesión').closest('a')).toHaveAttribute('href', '/login');
});
