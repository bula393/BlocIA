# Quickstart: Correccion Grafica

This guide validates the public start page, public auth routes, protected route guard, JWT behavior,
and visual compliance after implementation.

## Prerequisites

- Frontend running at `http://localhost:5173`.
- Existing backend/auth flow available when JWT-positive scenarios are tested.
- Test user that can obtain a valid JWT through login or registration.

## Validation Order

1. Validate public start route.
2. Validate public login/register access.
3. Validate protected route guard without JWT.
4. Validate protected route access with valid JWT.
5. Validate visual system compliance across desktop, tablet, and mobile.

## Story 1: Ver inicio publico

### Front

1. Open `http://localhost:5173/` without any token.
2. Confirm the page does not redirect to a protected page.
3. Confirm a circular logo appears at the top right.
4. Confirm the page displays a phrase equivalent to `las decisiones las tomas vos`.
5. Confirm a login action appears toward the right side of the page.

### Expected Outcome

The start page is public, visually aligned with BloqIA, and gives a direct path to login.

## Story 2: Acceder a login y registro sin sesion

### Front

1. Open `/login` without token.
2. Confirm the login form is usable.
3. Open `/register` without token.
4. Confirm the register form is usable.
5. Navigate back to `/` from login/register.

### Expected Outcome

Login and register are public and do not require JWT.

## Story 3: Proteger rutas privadas

### Without JWT

1. Open `/perfil` without token.
2. Confirm private profile content is not visible.
3. Confirm a clear login action is visible.
4. Repeat for `/perfil-tecnico`.

### With invalid/expired JWT

1. Simulate an invalid or expired token state.
2. Open `/perfil` and `/perfil-tecnico`.
3. Confirm both are treated as unauthenticated.

### With valid JWT

1. Log in or register and obtain a valid JWT.
2. Open `/perfil`.
3. Confirm profile content is visible.
4. Open `/perfil-tecnico`.
5. Confirm technical profile content is visible.

## Story 4: Mantener coherencia visual normativa

### Visual QA

1. Capture or inspect desktop, tablet, and mobile views for `/`, `/login`, `/register`, and a
   protected-route guard state.
2. Confirm approved palette only.
3. Confirm no pill radius, decorative gradients, diffuse shadows, floating card primary layouts,
   emoji, or prohibited AI iconography.
4. Confirm logo, phrase, and login action do not overlap on mobile.
5. Confirm focus rings use the BloqIA blue action color.

## Final Gate Before Advancing

- Public route checks pass.
- Protected route checks pass for missing, invalid, expired, and valid JWT states.
- Frontend tests and Playwright visual checks pass.
- Visual QA records zero prohibited visual elements from `apartadoDIseñoGraficoBlocIA.md`.
- Any fix needed to make the system work is documented in task notes or implementation evidence.

## Validation Commands

```powershell
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm test
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm run build
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npx playwright test
```

Expected results:

- Vitest integration tests pass.
- TypeScript and Vite build passes.
- Playwright route, JWT, responsive, and visual QA tests pass.
