# US2 Public Auth Evidence

Implemented:

- `/login` remains public and includes secondary links to `/` and `/register`.
- `/register` remains public and includes secondary links to `/` and `/login`.
- Login/register preserve sparse, task-focused form structure inside the BloqIA block chassis.

Validated by:

- `front/tests/integration/public-auth-routes.test.tsx`
- `front/tests/e2e/login-register-visual.spec.ts`
