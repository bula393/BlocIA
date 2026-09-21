import { canAccessRoute, createSessionJwt, getJwtStatus, isProtectedRoute, isPublicRoute, setRouteJwt } from '../../src/app/routeGuard';

afterEach(() => setRouteJwt(null));

test('identifies public and protected routes', () => {
  expect(isPublicRoute('/')).toBe(true);
  expect(isPublicRoute('/login')).toBe(true);
  expect(isPublicRoute('/register')).toBe(true);
  expect(isProtectedRoute('/perfil')).toBe(true);
  expect(isProtectedRoute('/perfil-tecnico')).toBe(true);
});

test('handles missing invalid expired and valid jwt states', () => {
  expect(getJwtStatus(null)).toBe('missing');
  expect(getJwtStatus('not-a-jwt')).toBe('invalid');
  expect(getJwtStatus(createSessionJwt('user@example.com', -1))).toBe('expired');
  expect(getJwtStatus(createSessionJwt('user@example.com', 60))).toBe('valid');
});

test('allows protected routes only with valid jwt', () => {
  expect(canAccessRoute('/perfil', null)).toBe(false);
  expect(canAccessRoute('/perfil', 'bad')).toBe(false);
  expect(canAccessRoute('/perfil', createSessionJwt('user@example.com', 60))).toBe(true);
});
