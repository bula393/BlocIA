# Quickstart: Modulo de Usuario

This guide documents validation scenarios for the user module after implementation. It does not
implement the feature.

## Prerequisites

- Backend service running at `http://localhost:8000`.
- Frontend PWA running at `http://localhost:5173`.
- Swagger/OpenAPI generated from [contracts/openapi.yaml](contracts/openapi.yaml).
- Test mail values that do not belong to real users.
- Google login configured in a test environment.

## Validation Order

Run validations in three lanes for each story: Back, Front, then Testing evidence.
Run visual validation after each frontend story using [visual-design.md](visual-design.md) and
`apartadoDIseñoGraficoBlocIA.md`.

## Story 1: Login de usuario

### Back

1. Create or seed a user with mail and contrasenia.
2. Verify mail-and-contrasenia login:

```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"mail":"usuario.demo@example.com","password":"ClaveSegura-123"}'
```

Expected outcome: response is successful, returns the authenticated user and an access token, and
does not expose password data.

3. Verify invalid credentials:

```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"mail":"usuario.demo@example.com","password":"incorrecta"}'
```

Expected outcome: response rejects the attempt with a generic message that does not reveal which
credential failed.

4. Repeat the invalid login request at least five times for the same account.

Expected outcome: every response keeps the same safe rejection behavior, and the account remains
able to log in successfully with valid credentials afterward.

### Front

1. Open `/login`.
2. Log in with mail and contrasenia.
3. Confirm the authenticated profile state is visible.
4. Start Google login from the same screen and confirm the flow reaches either authenticated state
   or a missing-fields completion screen.

### Testing

- Unit coverage for credential validation and login result states.
- Integration coverage for successful login, invalid login, repeated failed attempts without
  account lockout, and Google-linked login.
- Contract coverage for `/auth/login`, `/auth/google/start`, `/auth/google/callback`, and `/auth/google/session`.

## Story 2: Registro de cuenta

### Back

1. Register with valid data:

```bash
curl -i -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"mail":"nuevo.usuario@example.com","password":"ClaveSegura-123","age":28,"profession":"Estudiante"}'
```

Expected outcome: account is created and can be used for login.

2. Try duplicate mail:

```bash
curl -i -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"mail":"nuevo.usuario@example.com","password":"OtraClave-123","age":29,"profession":"Docente"}'
```

Expected outcome: duplicate registration is rejected.

3. Try weak contrasenia:

```bash
curl -i -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"mail":"debil@example.com","password":"123","age":20,"profession":"Estudiante"}'
```

Expected outcome: registration is rejected with clear field validation.

### Front

1. Open `/register`.
2. Complete the form with valid data and confirm the account can proceed.
3. Confirm weak contrasenia feedback appears before account creation.
4. Complete a Google registration with missing fields and verify only missing fields are requested.

### Testing

- Unit coverage for mail uniqueness response handling and contrasenia rules.
- Integration coverage for normal registration, duplicate mail, weak contrasenia, and Google
  registration completion.
- Contract coverage for `/auth/register` and `/auth/register/complete-google`.

## Story 3: Gestion de perfil

### Back

1. Fetch profile:

```bash
curl -i http://localhost:8000/profile \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Expected outcome: profile fields are returned for the authenticated user.

2. Update editable profile fields:

```bash
curl -i -X PATCH http://localhost:8000/profile \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"age":29,"profession":"Programador"}'
```

Expected outcome: profile updates are validated and returned.

### Front

1. Open `/perfil` after login.
2. Confirm all available profile fields are visible.
3. Edit allowed fields and confirm the screen shows the updated values.
4. Try invalid values and confirm validation appears without saving bad data.

### Testing

- Unit coverage for profile field validation and editable/protected field rules.
- Integration coverage for profile read and update.
- Contract coverage for `GET /profile` and `PATCH /profile`.

## Story 4: Perfil tecnico de IA

### Back

1. List providers and models:

```bash
curl -i http://localhost:8000/technical-profile/providers \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Expected outcome: providers, models, and token status are returned without full token values.

2. Save a provider token:

```bash
curl -i -X POST http://localhost:8000/technical-profile/tokens \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"providerId":"openai","token":"test-token-value"}'
```

Expected outcome: provider token status is returned with a masked label only.

3. Remove a provider token:

```bash
curl -i -X DELETE http://localhost:8000/technical-profile/tokens/openai \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Expected outcome: token is removed for the current user only.

### Front

1. Open `/perfil-tecnico` after login.
2. Confirm providers and models are visible.
3. Add or replace a token for a selected provider.
4. Confirm the full token is not displayed after saving.
5. Confirm provider state is clear: not configured, configured, invalid, or requires attention.

### Testing

- Unit coverage for token status display and masking behavior.
- Integration coverage for provider listing, token save, replacement, removal, and ownership.
- Contract coverage for `/technical-profile/providers`, `/technical-profile/tokens`, and
  `/technical-profile/tokens/{providerId}`.

## Final Gate Before Advancing

- Swagger/OpenAPI must include every endpoint in [contracts/openapi.yaml](contracts/openapi.yaml).
- Curl evidence must be captured for every endpoint added by the feature.
- Backend tests, frontend tests, contract tests, and end-to-end validations must pass before moving
  from one task group to the next.
- Visual QA evidence must confirm the user module follows [visual-design.md](visual-design.md):
  approved palette only, no pill radius, no gradients, no floating cards as primary layout, no
  diffuse shadows, responsive cuts checked, and text fitting verified.
- Any fix required to make the system work must be documented in the relevant task notes or project
  documentation.
