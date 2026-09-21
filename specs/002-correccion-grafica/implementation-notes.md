# Implementation Notes

- Added `front/src/pages/Inicio.tsx` as the public root page.
- Added `front/src/app/routeGuard.ts` with public route detection and JWT state handling.
- Updated `front/src/app/router.tsx` so `/`, `/login`, and `/register` are public and protected routes render a guard unless JWT status is valid.
- Added a non-persistent in-memory test JWT hook via `globalThis.__BLOQIA_TEST_JWT__` for Playwright validation. This does not use browser storage.
- Updated login and register pages with secondary navigation back to start/auth pages.
- Extended visual CSS for start and guard states while preserving the BloqIA visual system.
- No backend route changes were needed.
