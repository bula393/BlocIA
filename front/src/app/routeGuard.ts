import { getAccessToken } from '../api/client';

export type JwtStatus = 'missing' | 'valid' | 'invalid' | 'expired';

export const publicRoutes = ['/', '/login', '/register', '/auth/google/callback'];

let routeJwt: string | null = null;

function getInjectedJwt() {
  return (globalThis as { __BLOQIA_TEST_JWT__?: string }).__BLOQIA_TEST_JWT__ ?? null;
}

function base64UrlEncode(value: string) {
  return btoa(value).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}

function base64UrlDecode(value: string) {
  const padded = value.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '=');
  return atob(padded);
}

export function createSessionJwt(subject: string, expiresInSeconds = 3600) {
  const header = base64UrlEncode(JSON.stringify({ alg: 'none', typ: 'JWT' }));
  const payload = base64UrlEncode(JSON.stringify({ sub: subject, exp: Math.floor(Date.now() / 1000) + expiresInSeconds }));
  return `${header}.${payload}.signature`;
}

export function setRouteJwt(token: string | null) {
  routeJwt = token;
}

export function getRouteJwt() {
  return routeJwt;
}

export function normalizePath(path: string) {
  const [pathname] = path.split('?');
  return pathname || '/';
}

export function isPublicRoute(path: string) {
  return publicRoutes.includes(normalizePath(path));
}

export function isProtectedRoute(path: string) {
  return !isPublicRoute(path);
}

export function getJwtStatus(token: string | null | undefined): JwtStatus {
  if (!token) return 'missing';
  const parts = token.split('.');
  if (parts.length !== 3) return 'invalid';
  try {
    const payload = JSON.parse(base64UrlDecode(parts[1])) as { exp?: number };
    if (!payload.exp || typeof payload.exp !== 'number') return 'invalid';
    if (payload.exp <= Math.floor(Date.now() / 1000)) return 'expired';
    return 'valid';
  } catch {
    return 'invalid';
  }
}

export function getCurrentJwtStatus() {
  return getJwtStatus(routeJwt ?? getInjectedJwt() ?? getAccessToken());
}

export function canAccessRoute(path: string, token: string | null | undefined = routeJwt ?? getInjectedJwt() ?? getAccessToken()) {
  if (isPublicRoute(path)) return true;
  return getJwtStatus(token) === 'valid';
}
