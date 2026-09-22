import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PerfilTecnico } from '../../src/pages/PerfilTecnico';

test('renders technical profile title', () => {
  render(<QueryClientProvider client={new QueryClient()}><PerfilTecnico /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Proveedores y modelos' })).toBeInTheDocument();
});
