import { apiRequest, setAccessToken } from './client';
import { setRouteJwt } from '../app/routeGuard';
import type { AuthSessionResponse } from '../types/dominio';
import { queryClient } from '../app/queryClient';

export function rememberSession(session: AuthSessionResponse) {
  queryClient.removeQueries();
  setAccessToken(session.accessToken);
  setRouteJwt(session.accessToken);
}

export function forgetSession() {
  queryClient.removeQueries();
  setAccessToken(null);
  setRouteJwt(null);
}

/** Restore the HttpOnly browser-session cookie after a page reload. */
export async function restoreSession(signal?: AbortSignal) {
  const session = await apiRequest<AuthSessionResponse>('/api/auth/session', { signal });
  rememberSession(session);
  return session;
}

export async function logout() {
  try {
    await apiRequest<void>('/api/auth/logout', { method: 'POST' });
  } finally {
    forgetSession();
  }
}

export async function login(mail: string, password: string) {
  const session = await apiRequest<AuthSessionResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ mail, password })
  });
  rememberSession(session);
  return session;
}

export function startGoogleLogin() {
  window.location.assign('/api/auth/google/start');
}

export async function consumeGoogleSession() {
  const result = await apiRequest<AuthSessionResponse | { registrationToken: string; missingFields: string[]; prefilledFields: Record<string, unknown> }>('/api/auth/google/session');
  if ('accessToken' in result) {
    rememberSession(result);
  }
  return result;
}

export async function register(mail: string, password: string, age: number, profession: string) {
  const session = await apiRequest<AuthSessionResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ mail, password, age, profession })
  });
  rememberSession(session);
  return session;
}

export async function completeGoogleRegistration(registrationToken: string, age: number, profession: string) {
  const session = await apiRequest<AuthSessionResponse>('/api/auth/register/complete-google', {
    method: 'POST',
    body: JSON.stringify({ registrationToken, age, profession })
  });
  rememberSession(session);
  return session;
}
