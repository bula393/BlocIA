import { describe, expect, test } from 'vitest';
import { ApiRequestError } from '../../src/api/client';
import { authErrorMessage } from '../../src/components/auth/authErrorMessage';

describe('auth error messages', () => {
  test('explains when a registration email already has an account', () => {
    expect(authErrorMessage(new ApiRequestError('Mail already registered', 409), 'register'))
      .toContain('Iniciá sesión');
    expect(authErrorMessage(new Error('Mail already registered'), 'register'))
      .toContain('Iniciá sesión');
  });

  test('distinguishes rejected login credentials from server failures', () => {
    expect(authErrorMessage(new ApiRequestError('Invalid credentials', 401), 'login'))
      .toContain('no coinciden');
    expect(authErrorMessage(new ApiRequestError('Internal server error', 500), 'login'))
      .toContain('servicio no está disponible');
  });

  test('explains connection failures while preserving a path to retry', () => {
    expect(authErrorMessage(new TypeError('Failed to fetch'), 'register'))
      .toContain('Conservamos tus datos');
  });
});
