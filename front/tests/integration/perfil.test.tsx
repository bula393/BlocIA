import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Perfil } from '../../src/pages/Perfil';

test('renders profile edit controls', () => {
  render(<QueryClientProvider client={new QueryClient()}><Perfil /></QueryClientProvider>);
  expect(screen.getByRole('heading', { name: 'Perfil' })).toBeInTheDocument();
  expect(screen.getByText('Guardar cambios')).toBeInTheDocument();
});
