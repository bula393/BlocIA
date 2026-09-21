# US3 Protected Routes Evidence

Implemented:

- `front/src/app/routeGuard.ts` defines public routes, protected route detection, and JWT status.
- `front/src/app/router.tsx` blocks `/perfil`, `/perfil-tecnico`, and unknown private routes before rendering protected content.
- Missing, invalid, and expired JWT states show a guard screen with login action.
- Valid JWT state permits protected route rendering.

Validated by:

- `front/tests/integration/routeGuard.test.ts`
- `front/tests/integration/protected-routes.test.tsx`
- `front/tests/e2e/protected-routes.spec.ts`
