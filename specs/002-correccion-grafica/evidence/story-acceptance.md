# Story Acceptance Evidence

## US1 Ver inicio publico

- `/` renders the public start page without authentication.
- Circular logo, main phrase, and login action are visible and validated by integration and Playwright tests.

## US2 Acceder a login y registro sin sesion

- `/login` and `/register` render without JWT.
- Both pages include clear secondary navigation to public routes.

## US3 Proteger rutas privadas

- `/perfil` and `/perfil-tecnico` show guard state for missing, invalid, and expired JWT.
- Valid JWT allows protected route rendering.

## US4 Mantener coherencia visual normativa

- Visual QA checks pass for prohibited CSS patterns, responsive layout, and text fitting.
- Public/auth/guard states use the BloqIA block chassis and approved visual rules.
