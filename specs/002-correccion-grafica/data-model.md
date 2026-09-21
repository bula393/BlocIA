# Data Model: Correccion Grafica

## Public Start Page

Represents the unauthenticated first screen.

### Fields

- `route`: public start route; assumed to be root `/`.
- `temporaryLogo`: circular brand placeholder positioned at the top right.
- `mainPhrase`: phrase equivalent to "las decisiones las tomas vos".
- `loginAction`: clear action that moves users to login.

### Validation Rules

- The logo must remain a circle until a final brand asset is specified.
- The main phrase, logo, and login action must be visible without overlap on desktop, tablet, and mobile.
- The page must not require authentication.
- The page must comply with `apartadoDIseñoGraficoBlocIA.md`.

## Route Access Rule

Represents whether a route can be viewed by unauthenticated users.

### Fields

- `path`: route path.
- `accessLevel`: public or protected.
- `unauthenticatedOutcome`: page content for public routes or guard response for protected routes.

### Validation Rules

- Public routes are limited to start, login, and register.
- Every route outside start, login, and register must be protected.
- Protected route content must not render before JWT validity is established.

## Authenticated Session

Represents the user's current authentication state.

### Fields

- `jwtStatus`: missing, valid, invalid, or expired.
- `currentUser`: available only when JWT is valid.
- `source`: current auth/session source from existing frontend auth flow.

### Validation Rules

- Missing, invalid, or expired JWT must be treated as unauthenticated.
- JWT state must not be stored in localStorage or sessionStorage.
- Private data remains server-authoritative even when the frontend guard allows route access.

### State Transitions

- `missing` -> `valid`: user completes login/register and receives a valid token.
- `valid` -> `expired`: token validity period ends.
- `valid` -> `invalid`: token verification fails.
- `invalid` or `expired` -> `valid`: user authenticates again.

## Protected Route Guard

Represents the frontend guard that blocks private content.

### Fields

- `requestedPath`: route the user attempted to open.
- `jwtStatus`: current JWT state.
- `guardMessage`: user-facing message when access is denied.
- `loginAction`: clear action to open login.

### Validation Rules

- Guard must show a clear path to login.
- Guard must not show private page content or private user data.
- Guard visual state must follow `apartadoDIseñoGraficoBlocIA.md`.
