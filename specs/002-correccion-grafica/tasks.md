# Tasks: Correccion Grafica

**Input**: Design documents from `/specs/002-correccion-grafica/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/route-access.md, quickstart.md

**Tests**: Required for route guard behavior, JWT access rules, and visual QA because this is a graphic/access correction.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase when files do not overlap
- **[Story]**: User story label for story phases only
- Every task includes an exact target file path

## Phase 1: Setup (Shared Frontend Infrastructure)

**Purpose**: Prepare existing frontend structure for public start, route guards, JWT checks, and visual QA.

- [X] T001 Verify public/protected route inventory against specs/002-correccion-grafica/contracts/route-access.md and document any existing route mismatch in specs/002-correccion-grafica/evidence/route-inventory.md
- [X] T002 [P] Create frontend route guard module scaffold in front/src/app/routeGuard.ts
- [X] T003 [P] Create start page file scaffold in front/src/pages/Inicio.tsx
- [X] T004 [P] Create route guard test scaffold in front/tests/integration/routeGuard.test.ts
- [X] T005 [P] Create public start visual e2e test scaffold in front/tests/e2e/inicio-visual.spec.ts
- [X] T006 [P] Create protected-route e2e test scaffold in front/tests/e2e/protected-routes.spec.ts

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared route/JWT behavior and visual constraints used by every story.

- [X] T007 Implement public route list for `/`, `/login`, and `/register` in front/src/app/routeGuard.ts
- [X] T008 Implement protected route detection where every route outside start, login, and register is protected in front/src/app/routeGuard.ts
- [X] T009 Implement JWT status helper with states missing, valid, invalid, and expired in front/src/app/routeGuard.ts
- [X] T010 Ensure access token remains in memory and is not stored in localStorage or sessionStorage in front/src/api/client.ts
- [X] T011 Add shared protected-route guard UI state with clear login action and no private content in front/src/app/router.tsx
- [X] T012 [P] Add integration tests for public route list and protected route detection in front/tests/integration/routeGuard.test.ts
- [X] T013 [P] Add integration tests for missing, invalid, expired, and valid JWT status handling in front/tests/integration/routeGuard.test.ts
- [X] T014 [P] Add visual-system route guard assertions for no gradients, no floating cards, no pill buttons, and one blue primary action in front/tests/e2e/protected-routes.spec.ts

## Phase 3: User Story 1 - Ver inicio publico (Priority: P1)

**Goal**: Visitors see a public start page with a temporary circular logo at top right, main phrase, and right-side login action.

**Independent Test**: Open `/` without any token and confirm start page content appears without redirect and without overlap on desktop/mobile.

### Tests for User Story 1

- [X] T015 [P] [US1] Add integration test that `/` renders Inicio without authentication in front/tests/integration/inicio.test.tsx
- [X] T016 [P] [US1] Add Playwright test for top-right circular logo, main phrase, and right-side login action on `/` in front/tests/e2e/inicio-visual.spec.ts
- [X] T017 [P] [US1] Add Playwright mobile viewport test confirming logo, phrase, and login action do not overlap in front/tests/e2e/inicio-visual.spec.ts

### Implementation for User Story 1

- [X] T018 [US1] Implement Inicio page with temporary circular logo, phrase equivalent to "las decisiones las tomas vos", and login action in front/src/pages/Inicio.tsx
- [X] T019 [US1] Wire root `/` route to Inicio page without authentication requirement in front/src/app/router.tsx
- [X] T020 [US1] Add Inicio page visual classes using only `apartadoDIseñoGraficoBlocIA.md` palette, 0/2/4 px radii, and block layout in front/src/tokens/visual.css
- [X] T021 [US1] Record public start route and visual evidence in specs/002-correccion-grafica/evidence/us1-inicio.md

## Phase 4: User Story 2 - Acceder a login y registro sin sesion (Priority: P1)

**Goal**: Visitors can access login and register without JWT, navigate between start/login/register, and use known auth patterns adapted to BloqIA.

**Independent Test**: Open `/login` and `/register` without token and confirm both are usable and link back to start.

### Tests for User Story 2

- [X] T022 [P] [US2] Add integration test that `/login` is public and renders without JWT in front/tests/integration/public-auth-routes.test.tsx
- [X] T023 [P] [US2] Add integration test that `/register` is public and renders without JWT in front/tests/integration/public-auth-routes.test.tsx
- [X] T024 [P] [US2] Add Playwright visual test for sparse login form, one primary action, and secondary register path in front/tests/e2e/login-register-visual.spec.ts
- [X] T025 [P] [US2] Add Playwright visual test for sparse register form, one primary action, and secondary login/start path in front/tests/e2e/login-register-visual.spec.ts

### Implementation for User Story 2

- [X] T026 [US2] Update Login page to include clear secondary navigation to start and register while remaining public in front/src/pages/Login.tsx
- [X] T027 [US2] Update Register page to include clear secondary navigation to start and login while remaining public in front/src/pages/Register.tsx
- [X] T028 [US2] Ensure login/register keep task-focused known-pattern structure without copying external site visuals in front/src/pages/Login.tsx
- [X] T029 [US2] Ensure register/login visual states use block surfaces, approved radii, one primary blue action, and no floating card primary layout in front/src/pages/Register.tsx
- [X] T030 [US2] Record public login/register evidence in specs/002-correccion-grafica/evidence/us2-public-auth.md

## Phase 5: User Story 3 - Proteger rutas privadas (Priority: P2)

**Goal**: Non-public routes require valid JWT before rendering protected content.

**Independent Test**: Open `/perfil` and `/perfil-tecnico` with missing, invalid, expired, and valid JWT states and confirm correct guard/access behavior.

### Tests for User Story 3

- [X] T031 [P] [US3] Add integration test that `/perfil` does not render protected content without valid JWT in front/tests/integration/protected-routes.test.tsx
- [X] T032 [P] [US3] Add integration test that `/perfil-tecnico` does not render protected content without valid JWT in front/tests/integration/protected-routes.test.tsx
- [X] T033 [P] [US3] Add integration test that valid JWT allows protected route rendering in front/tests/integration/protected-routes.test.tsx
- [X] T034 [P] [US3] Add Playwright test for missing, invalid, expired, and valid JWT guard states in front/tests/e2e/protected-routes.spec.ts

### Implementation for User Story 3

- [X] T035 [US3] Implement route guard application in front/src/app/router.tsx before rendering Perfil and PerfilTecnico content
- [X] T036 [US3] Implement protected-route guard screen with clear login action, no private content, and visual-system-compliant layout in front/src/app/router.tsx
- [X] T037 [US3] Implement JWT validation semantics for missing, invalid, expired, and valid token states in front/src/app/routeGuard.ts
- [X] T038 [US3] Ensure authenticated users with valid JWT can access Perfil and PerfilTecnico without redirect to login in front/src/app/router.tsx
- [X] T039 [US3] Record protected route guard evidence in specs/002-correccion-grafica/evidence/us3-protected-routes.md

## Phase 6: User Story 4 - Mantener coherencia visual normativa (Priority: P2)

**Goal**: Start, login, register, and protected-route guard states comply with `apartadoDIseñoGraficoBlocIA.md`.

**Independent Test**: Run visual QA across desktop, tablet, and mobile and confirm zero prohibited visual elements.

### Tests for User Story 4

- [X] T040 [P] [US4] Add Playwright visual prohibition checks for gradients, floating cards, pill buttons, diffuse shadows, emoji, and prohibited iconography in front/tests/e2e/correccion-grafica-visual.spec.ts
- [X] T041 [P] [US4] Add Playwright responsive checks for `/`, `/login`, `/register`, and protected-route guard state across desktop, tablet, and mobile in front/tests/e2e/correccion-grafica-responsive.spec.ts
- [X] T042 [P] [US4] Add Playwright text-overlap checks for logo, phrase, login action, auth forms, and guard state in front/tests/e2e/correccion-grafica-text-fit.spec.ts

### Implementation for User Story 4

- [X] T043 [US4] Update visual CSS for start/auth/guard states to use only approved palette and admitted opacity derivatives in front/src/tokens/visual.css
- [X] T044 [US4] Update visual CSS so start/auth/guard states use only 0 px, 2 px, and 4 px radii where permitted in front/src/tokens/visual.css
- [X] T045 [US4] Ensure temporary logo is a plain circle and no other new circular shapes are introduced in front/src/pages/Inicio.tsx
- [X] T046 [US4] Ensure public start, login, register, and guard states avoid prohibited visual elements from `apartadoDIseñoGraficoBlocIA.md` in front/src/tokens/visual.css
- [X] T047 [US4] Record visual QA evidence for start/auth/guard states in specs/002-correccion-grafica/evidence/us4-visual-qa.md

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete validation evidence and regression checks.

- [X] T048 [P] Run frontend unit/integration tests and record command/output summary in specs/002-correccion-grafica/evidence/frontend-tests.md
- [X] T049 [P] Run frontend build and record command/output summary in specs/002-correccion-grafica/evidence/frontend-build.md
- [X] T050 [P] Run Playwright visual and route tests and record command/output summary in specs/002-correccion-grafica/evidence/playwright-tests.md
- [X] T051 [P] Verify frontend source contains no localStorage or sessionStorage token persistence and document result in specs/002-correccion-grafica/evidence/security-review.md
- [X] T052 [P] Verify service worker does not cache protected/private route responses and document result in specs/002-correccion-grafica/evidence/pwa-cache-review.md
- [X] T053 Update quickstart validation notes with final public route, protected route, JWT, and visual QA commands in specs/002-correccion-grafica/quickstart.md
- [X] T054 Document any implementation fixes, scope deviations, and known limitations in specs/002-correccion-grafica/implementation-notes.md
- [X] T055 Verify every story satisfies its independent test criteria and update specs/002-correccion-grafica/evidence/story-acceptance.md

## Dependencies

### Phase Dependencies

- Phase 1 Setup must complete before Phase 2 Foundational.
- Phase 2 Foundational blocks all user stories.
- US1 and US2 are both P1 and can be delivered as the MVP together: public start plus public auth routes.
- US3 depends on route guard/JWT helpers from Phase 2 and can be implemented after public routes exist.
- US4 depends on public/auth/guard screens existing so visual QA can inspect them.
- Polish runs after selected stories are implemented.

### User Story Dependencies

```text
Setup -> Foundation -> US1 + US2 -> US3 -> US4 -> Polish
```

## Parallel Execution Examples

### US1 Ver inicio publico

```text
Parallel after foundation:
- T015 integration test in front/tests/integration/inicio.test.tsx
- T016 visual test in front/tests/e2e/inicio-visual.spec.ts
- T018 page implementation in front/src/pages/Inicio.tsx
```

### US2 Login/Register publicos

```text
Parallel after foundation:
- T022 public login test in front/tests/integration/public-auth-routes.test.tsx
- T024 login/register visual test in front/tests/e2e/login-register-visual.spec.ts
- T026 Login page update in front/src/pages/Login.tsx
- T027 Register page update in front/src/pages/Register.tsx
```

### US3 Rutas privadas protegidas

```text
Parallel after foundation:
- T031 protected route integration test in front/tests/integration/protected-routes.test.tsx
- T034 route guard e2e test in front/tests/e2e/protected-routes.spec.ts
- T037 JWT semantics in front/src/app/routeGuard.ts
```

### US4 Coherencia visual normativa

```text
Parallel after public/auth/guard screens exist:
- T040 visual prohibition checks in front/tests/e2e/correccion-grafica-visual.spec.ts
- T041 responsive checks in front/tests/e2e/correccion-grafica-responsive.spec.ts
- T042 text-fit checks in front/tests/e2e/correccion-grafica-text-fit.spec.ts
- T043 visual CSS updates in front/src/tokens/visual.css
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete US1 public start and US2 public login/register routes.
4. Validate public route behavior and visual layout.

### Incremental Delivery

1. Add US3 protected route guard and JWT handling.
2. Add US4 visual compliance checks and refinements.
3. Run Phase 7 polish and evidence tasks.

### Constitution Gates

- Do not implement code before tasks are approved.
- Every protected route behavior must be traceable to FR-006 through FR-010.
- Every visual correction must respect `apartadoDIseñoGraficoBlocIA.md`.
- JWT must not be persisted in localStorage or sessionStorage.
- Any fix needed to make the feature work must be documented in implementation notes or evidence files.
