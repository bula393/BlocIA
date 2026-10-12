import { apiRequest, setAccessToken } from './client';
import { setRouteJwt } from '../app/routeGuard';
import type { AuthSessionResponse } from '../types/dominio';
import { queryClient } from '../app/queryClient';

const ACCOUNT_CHANGE_KEY = 'blocia:account-change';
const accountChannel = typeof window === 'undefined' || typeof window.BroadcastChannel === 'undefined'
  ? null
  : new window.BroadcastChannel('blocia-account-session');

function notifyAccountChange() {
  accountChannel?.postMessage({ type: 'account-changed' });
  try {
    localStorage.setItem(ACCOUNT_CHANGE_KEY, `${Date.now()}:${Math.random()}`);
  } catch {
    // BroadcastChannel still covers browsers where local storage is unavailable.
  }
}

export function subscribeToAccountChanges(onChange: () => void) {
  let reloadQueued = false;
  const notify = () => {
    if (reloadQueued) return;
    reloadQueued = true;
    onChange();
  };
  const onStorage = (event: StorageEvent) => {
    if (event.key === ACCOUNT_CHANGE_KEY) notify();
  };
  const onMessage = (event: MessageEvent) => {
    if (event.data?.type === 'account-changed') notify();
  };
  window.addEventListener('storage', onStorage);
  accountChannel?.addEventListener('message', onMessage);
  return () => {
    window.removeEventListener('storage', onStorage);
    accountChannel?.removeEventListener('message', onMessage);
  };
}

export function rememberSession(session: AuthSessionResponse, notifyOtherTabs = true) {
  queryClient.removeQueries();
  setAccessToken(session.accessToken);
  setRouteJwt(session.accessToken);
  if (notifyOtherTabs) notifyAccountChange();
}

export function forgetSession() {
  queryClient.removeQueries();
  setAccessToken(null);
  setRouteJwt(null);
}

/** Restore the HttpOnly browser-session cookie after a page reload. */
export async function restoreSession(signal?: AbortSignal) {
  const session = await apiRequest<AuthSessionResponse>('/api/auth/session', { signal });
  rememberSession(session, false);
  return session;
}

export async function logout() {
  let completed = false;
  try {
    await apiRequest<void>('/api/auth/logout', { method: 'POST' });
    completed = true;
  } finally {
    forgetSession();
    if (completed) notifyAccountChange();
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
