# Tasks: Modulo de Usuario

**Input**: Design documents from `/specs/001-modulo-usuario/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, visual-design.md, contracts/openapi.yaml, quickstart.md

**Tests**: Required by project constitution for important business rules and by quickstart validation. Visual QA tasks are required because `apartadoDIseñoGraficoBlocIA.md` is normative.

**Organization**: Tasks are grouped by setup/foundation, user story, visual design phase, and polish so each story remains independently testable while the visual system is applied in controlled phases.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase when files do not overlap
- **[Story]**: User story label for story phases only
- Every task includes an exact target file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Re-establish project structure and baseline configuration for backend, frontend, tests, and visual-system work.

- [ ] T001 Create backend directory structure in back/app/domain/user, back/app/application/user, back/app/infrastructure/user, back/app/presentation/user, back/tests/unit, back/tests/integration, and back/tests/contract
- [ ] T002 Create frontend directory structure in front/src/app, front/src/pages, front/src/components/chasis, front/src/components/estado, front/src/components/overlay, front/src/features/usuario, front/src/api, front/src/sw, front/src/tokens, front/src/types, front/tests/integration, and front/tests/e2e
- [ ] T003 Create backend project configuration for FastAPI, PostgreSQL access, pytest, and OpenAPI generation in back/pyproject.toml
- [ ] T004 Create frontend React + Vite + TypeScript PWA project configuration with TanStack Query, Zustand, Vitest, and Playwright scripts in front/package.json
- [ ] T005 [P] Create backend application entrypoint and app factory in back/app/main.py
- [ ] T006 [P] Create frontend Vite entrypoint in front/src/main.tsx
- [ ] T007 [P] Create frontend providers shell with QueryClientProvider and visual token stylesheet loading in front/src/app/providers.tsx
- [ ] T008 [P] Create frontend router skeleton with routes /login, /register, /perfil, and /perfil-tecnico in front/src/app/router.tsx
- [ ] T009 Copy planned OpenAPI contract into backend implementation documentation at back/app/presentation/user/openapi-user-module.yaml from specs/001-modulo-usuario/contracts/openapi.yaml
- [ ] T010 [P] Create Playwright configuration for e2e tests and visual QA viewport checks in front/playwright.config.ts

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared backend rules, frontend state boundaries, API client, visual tokens, and test fixtures required by every story.

- [ ] T011 Create PostgreSQL connection and transaction configuration in back/app/infrastructure/database.py
- [ ] T012 Create user module persistence migration with users, password_credentials, external_login_links, ai_providers, ai_models, and provider_tokens tables in back/app/infrastructure/user/migrations/001_user_module.sql
- [ ] T013 Define domain enums for login provider status, technical profile status, provider status, model availability status, and provider token status in back/app/domain/user/enums.py
- [ ] T014 Define User entity with fields `mail`, `passwordStatus`, `age`, `profession`, `displayName`, `loginProviderStatus`, `technicalProfileStatus`, `createdAt`, and `updatedAt` in back/app/domain/user/user.py
- [ ] T015 Define User validation rules where `mail` must be present, valid, and unique; `age` must be present and positive; and `profession` must be present before registration completes in back/app/domain/user/user.py
- [ ] T016 Define repository interfaces for users, password credentials, external login links, AI providers, AI models, and provider tokens in back/app/domain/user/repositories.py
- [ ] T017 Create PostgreSQL repository implementations for user module entities in back/app/infrastructure/user/postgres_repositories.py
- [ ] T018 Create backend dependency wiring for repositories, transactions, and current user resolution in back/app/presentation/user/dependencies.py
- [ ] T019 Create shared API error and validation response helpers matching ErrorResponse and ValidationErrorResponse in back/app/presentation/user/errors.py
- [ ] T020 [P] Create frontend typed domain models for UserProfile, ProviderWithModels, AIModel, ProviderTokenStatus, and auth responses in front/src/types/dominio.ts
- [ ] T021 [P] Create frontend API client that keeps access token in memory and never uses localStorage or sessionStorage in front/src/api/client.ts
- [ ] T022 [P] Create frontend service worker registration that cache-firsts shell assets and never caches private user responses in front/src/sw/registerSW.ts
- [ ] T023 [P] Create CSS visual tokens from `apartadoDIseñoGraficoBlocIA.md` approved palette, opacity derivatives, spacing scale, and radius scale in front/src/tokens/visual.css
- [ ] T024 [P] Create typography token stylesheet for Archivo interface text and Source Serif 4 response text roles in front/src/tokens/typography.css
- [ ] T025 [P] Create backend test fixtures for database cleanup, seeded users, seeded providers, and access token helpers in back/tests/conftest.py
- [ ] T026 [P] Create frontend test setup for React components, router, TanStack Query, and mocked API calls in front/tests/setup.ts
- [ ] T027 Update Swagger/OpenAPI generation check so back/app/presentation/user/openapi-user-module.yaml is included in backend API docs in back/app/presentation/user/swagger.py

## Phase 3: User Story 1 - Login de usuario (Priority: P1)

**Goal**: Users can log in with mail/contrasenia or linked Google account, repeated failed attempts do not lock accounts, and errors do not reveal credential details.

**Independent Test**: Seed a valid user, verify successful mail login, invalid login, five repeated invalid attempts without lockout, valid login afterward, Google-linked login, and visual compliance of Login.

### Tests for User Story 1

- [ ] T028 [P] [US1] Add unit tests for Password Credential constraints: password verifier is non-displayable, full password values are never displayed after submission, and repeated failed login attempts must not create an account lockout state by themselves in back/tests/unit/test_password_credential.py
- [ ] T029 [P] [US1] Add unit tests for login service behavior: valid credentials authenticate, invalid credentials return the same safe rejection, and invalid login attempt has no credential state transition in back/tests/unit/test_login_service.py
- [ ] T030 [P] [US1] Add contract tests for POST /auth/login 200 and 401, GET /auth/google/start 302, and POST /auth/google/complete 200/202/409 in back/tests/contract/test_auth_contract.py
- [ ] T031 [P] [US1] Add frontend tests for Login page mail/contrasenia submit, Google action, safe error display, and authenticated state transition in front/tests/integration/login.test.tsx
- [ ] T032 [P] [US1] Add visual tests for Login page using approved palette, one primary blue action, no pill radius, no floating card primary layout, and text fitting in front/tests/e2e/login-visual.spec.ts
- [ ] T033 [P] [US1] Add end-to-end login validation covering five repeated invalid attempts and successful login afterward in front/tests/e2e/login.spec.ts

### Implementation for User Story 1

- [ ] T034 [US1] Define PasswordCredential domain object with fields `userMail`, `passwordHash`, `createdAt`, and `updatedAt` in back/app/domain/user/password_credential.py
- [ ] T035 [US1] Implement password policy and verifier rules: at least 10 characters, at least one letter, one number, one special character, and no obvious reuse of the user's mail in back/app/domain/user/password_policy.py
- [ ] T036 [US1] Implement login use case for mail/contrasenia authentication and safe invalid-credentials rejection in back/app/application/user/login_with_password.py
- [ ] T037 [US1] Implement no-lockout repeated failure behavior for login attempts in back/app/application/user/login_with_password.py
- [ ] T038 [US1] Define ExternalLoginLink domain object with provider, externalSubject, providedMail, providedDisplayName, createdAt, and lastUsedAt in back/app/domain/user/external_login_link.py
- [ ] T039 [US1] Implement Google auth start and completion use cases with linked-user lookup and duplicate-account protection in back/app/application/user/google_auth.py
- [ ] T040 [US1] Implement POST /auth/login, GET /auth/google/start, and POST /auth/google/complete route handlers in back/app/presentation/user/auth_routes.py
- [ ] T041 [US1] Implement AuthSessionResponse, LoginRequest, GoogleCompleteRequest, RegistrationCompletionRequiredResponse, and auth error DTOs in back/app/presentation/user/auth_schemas.py
- [ ] T042 [P] [US1] Implement frontend auth API functions for /auth/login, /auth/google/start, and /auth/google/complete in front/src/api/auth.ts
- [ ] T043 [P] [US1] Implement Login page with block chassis surface, mail/contrasenia form, Google action, safe error band, and one primary blue action in front/src/pages/Login.tsx
- [ ] T044 [US1] Connect Login page to TanStack Query mutation and in-memory access token handling in front/src/features/usuario/useLogin.ts
- [ ] T045 [US1] Record curl and visual evidence for Login in specs/001-modulo-usuario/evidence/us1-login-curls.md

## Phase 4: User Story 2 - Registro de cuenta (Priority: P1)

**Goal**: Visitors can register with unique mail, secure contrasenia, edad, profesion, or complete only missing fields after Google prefill.

**Independent Test**: Register a valid user, reject duplicate mail, reject weak contrasenia, complete Google registration with only missing fields requested, and validate Register visual states.

### Tests for User Story 2

- [ ] T046 [P] [US2] Add unit tests for registration validation where `mail` must be present, valid, and unique; `age` must be present and positive; and `profession` must be present before registration completes in back/tests/unit/test_registration_validation.py
- [ ] T047 [P] [US2] Add unit tests for password policy requiring at least 10 characters, at least one letter, one number, one special character, and no obvious reuse of the user's mail in back/tests/unit/test_password_policy.py
- [ ] T048 [P] [US2] Add integration tests for normal registration, duplicate mail rejection, weak contrasenia rejection, Google prefill, and Google missing-fields completion in back/tests/integration/test_registration_flow.py
- [ ] T049 [P] [US2] Add contract tests for POST /auth/register and POST /auth/register/complete-google in back/tests/contract/test_registration_contract.py
- [ ] T050 [P] [US2] Add frontend tests for Register page valid submit, duplicate mail error, weak contrasenia feedback, and Google missing-fields completion in front/tests/integration/register.test.tsx
- [ ] T051 [P] [US2] Add visual tests for Register page password feedback, validation states, approved palette, 4 px fields/buttons, and no card stacking in front/tests/e2e/register-visual.spec.ts

### Implementation for User Story 2

- [ ] T052 [US2] Implement registration use case that creates User and PasswordCredential only after all required fields pass validation in back/app/application/user/register_user.py
- [ ] T053 [US2] Implement mail uniqueness check and duplicate-mail failure path in back/app/application/user/register_user.py
- [ ] T054 [US2] Implement Google registration completion use case that asks only for missing required fields from mail, age, and profession in back/app/application/user/complete_google_registration.py
- [ ] T055 [US2] Implement POST /auth/register and POST /auth/register/complete-google route handlers in back/app/presentation/user/auth_routes.py
- [ ] T056 [US2] Implement RegisterRequest and GoogleRegistrationCompletionRequest DTOs with age minimum 1 and profession minLength 1 in back/app/presentation/user/auth_schemas.py
- [ ] T057 [P] [US2] Implement frontend register API functions for /auth/register and /auth/register/complete-google in front/src/api/auth.ts
- [ ] T058 [P] [US2] Implement Register page with block chassis surface, mail, contrasenia, edad, profesion, password feedback, duplicate-mail error, and Google missing-fields flow in front/src/pages/Register.tsx
- [ ] T059 [US2] Connect Register page to TanStack Query mutations and authenticated session handling in front/src/features/usuario/useRegister.ts
- [ ] T060 [US2] Record curl and visual evidence for Register in specs/001-modulo-usuario/evidence/us2-register-curls.md

## Phase 5: User Story 3 - Gestion de perfil (Priority: P2)

**Goal**: Authenticated users can view all available profile fields and update editable fields with validation.

**Independent Test**: Log in, fetch profile, update editable fields, reject invalid values, confirm updated values remain visible, and validate profile panel/drawer visual language.

### Tests for User Story 3

- [ ] T061 [P] [US3] Add unit tests for profile update rules where changed values must validate before saving and sensitive or protected fields require their own validation flow in back/tests/unit/test_profile_update.py
- [ ] T062 [P] [US3] Add integration tests for GET /profile and PATCH /profile success, invalid value rejection, protected field rejection, and visible persistence in back/tests/integration/test_profile_flow.py
- [ ] T063 [P] [US3] Add contract tests for GET /profile 200/401 and PATCH /profile 200/400/409 in back/tests/contract/test_profile_contract.py
- [ ] T064 [P] [US3] Add frontend tests for Perfil page field rendering, edit success, invalid value display, and no-save behavior on validation failure in front/tests/integration/perfil.test.tsx
- [ ] T065 [P] [US3] Add visual tests for Perfil page structural 0 px regions, 4 px fields/buttons, filete separators, and responsive profile drawer behavior in front/tests/e2e/perfil-visual.spec.ts

### Implementation for User Story 3

- [ ] T066 [US3] Implement get profile use case returning mail, age, profession, loginProviderStatus, technicalProfileStatus, and optional displayName in back/app/application/user/get_profile.py
- [ ] T067 [US3] Implement update profile use case validating editable fields and protecting non-editable or sensitive fields in back/app/application/user/update_profile.py
- [ ] T068 [US3] Implement GET /profile and PATCH /profile route handlers in back/app/presentation/user/profile_routes.py
- [ ] T069 [US3] Implement UserProfile and ProfileUpdateRequest DTOs with required mail, age, profession, loginProviderStatus, and technicalProfileStatus in back/app/presentation/user/profile_schemas.py
- [ ] T070 [P] [US3] Implement frontend profile API functions for GET /profile and PATCH /profile in front/src/api/profile.ts
- [ ] T071 [P] [US3] Implement Perfil page with all profile fields, editable controls, protected-field validation states, and visual-system panel language in front/src/pages/Perfil.tsx
- [ ] T072 [US3] Connect Perfil page to TanStack Query server cache and keep only form draft state local in front/src/features/usuario/usePerfil.ts
- [ ] T073 [US3] Record curl and visual evidence for Profile in specs/001-modulo-usuario/evidence/us3-profile-curls.md

## Phase 6: User Story 4 - Perfil tecnico de IA (Priority: P3)

**Goal**: Authenticated users can view AI providers/models and add, replace, or remove masked provider tokens scoped to their own account.

**Independent Test**: Log in, list providers/models, save a provider token, verify only masked status is shown, remove the token, verify ownership isolation, and validate technical status indicators.

### Tests for User Story 4

- [ ] T074 [P] [US4] Add unit tests for AI Provider rules where provider name must be visible and unavailable providers must not accept new token configuration unless explicitly re-enabled in back/tests/unit/test_ai_provider.py
- [ ] T075 [P] [US4] Add unit tests for AI Model rules where every model must belong to a provider and availabilityStatus is available, unavailable, or deprecated in back/tests/unit/test_ai_model.py
- [ ] T076 [P] [US4] Add unit tests for Provider Token rules: token belongs to exactly one User and one AI Provider, a User may have at most one active token per provider, full token values must never be returned, and status must be visible without exposing the token secret in back/tests/unit/test_provider_token.py
- [ ] T077 [P] [US4] Add integration tests for provider listing, token save, replacement, removal, invalid token status, and user ownership isolation in back/tests/integration/test_technical_profile_flow.py
- [ ] T078 [P] [US4] Add contract tests for GET /technical-profile/providers, POST /technical-profile/tokens, and DELETE /technical-profile/tokens/{providerId} in back/tests/contract/test_technical_profile_contract.py
- [ ] T079 [P] [US4] Add frontend tests for PerfilTecnico provider list, model list, token save/replace/remove, masked token display, and provider state labels in front/tests/integration/perfil_tecnico.test.tsx
- [ ] T080 [P] [US4] Add visual tests for PerfilTecnico provider/model listing, token state indicators, masked-token presentation, semantic colors, and no new shapes beyond visual-design.md in front/tests/e2e/perfil-tecnico-visual.spec.ts

### Implementation for User Story 4

- [ ] T081 [US4] Define AIProvider domain object with providerId, name, status, and description in back/app/domain/user/ai_provider.py
- [ ] T082 [US4] Define AIModel domain object with modelId, providerId, displayName, availabilityStatus, and capabilities in back/app/domain/user/ai_model.py
- [ ] T083 [US4] Define ProviderToken domain object with tokenId, userMail, providerId, maskedTokenLabel, status, createdAt, updatedAt, and lastValidatedAt in back/app/domain/user/provider_token.py
- [ ] T084 [US4] Implement list technical providers use case returning providers, models, and current user's token status without full token values in back/app/application/user/list_technical_providers.py
- [ ] T085 [US4] Implement save provider token use case enforcing one active token per user/provider and returning only masked token label/status in back/app/application/user/save_provider_token.py
- [ ] T086 [US4] Implement remove provider token use case scoped to the current authenticated user in back/app/application/user/remove_provider_token.py
- [ ] T087 [US4] Implement GET /technical-profile/providers, POST /technical-profile/tokens, and DELETE /technical-profile/tokens/{providerId} route handlers in back/app/presentation/user/technical_profile_routes.py
- [ ] T088 [US4] Implement ProviderWithModels, AIModel, ProviderTokenSaveRequest, and ProviderTokenStatus DTOs with documented enum values in back/app/presentation/user/technical_profile_schemas.py
- [ ] T089 [P] [US4] Implement frontend technical profile API functions for providers and tokens in front/src/api/technicalProfile.ts
- [ ] T090 [P] [US4] Implement PerfilTecnico page showing providers, models, token status, masked token label, and add/replace/remove controls using only approved visual-system shapes in front/src/pages/PerfilTecnico.tsx
- [ ] T091 [US4] Connect PerfilTecnico page to TanStack Query server cache and keep only unsaved token form state local in front/src/features/usuario/usePerfilTecnico.ts
- [ ] T092 [US4] Record curl and visual evidence for technical profile endpoints in specs/001-modulo-usuario/evidence/us4-technical-profile-curls.md

## Phase 7: Visual Design System Application

**Purpose**: Apply visual-design.md phases V1-V5 across the user module after functional story slices exist.

- [X] T093 [P] Implement approved palette CSS variables and opacity derivatives from visual-design.md Phase V1 in front/src/tokens/visual.css
- [X] T094 [P] Implement Archivo/Source Serif 4 typography roles and tabular numeric settings from visual-design.md Phase V1 in front/src/tokens/typography.css
- [X] T095 [P] Add visual prohibition checks for gradients, violet/indigo, diffuse shadows, pill radius, blobs, emoji, and chat-tail shapes in front/tests/e2e/visual-prohibitions.spec.ts
- [X] T096 Implement shared block chassis layout with left rail, paper work surface, filete separators, status panel slot, and meter slot in front/src/components/chasis/ChasisBloqIA.tsx
- [X] T097 Implement left rail active destination marker using 3 px blue bar and no rounded active background in front/src/components/chasis/RielLateral.tsx
- [X] T098 Implement status/meter components using 10 px desktop meter, 4 px mobile top meter, and discrete green/salmon/red status tramos in front/src/components/estado/MedidorTiempo.tsx
- [X] T099 Implement profile drawer/panel language with 0 px structural radius and 4 px controls in front/src/components/overlay/CajonPerfil.tsx
- [X] T100 Update Login, Register, Perfil, and PerfilTecnico pages to use ChasisBloqIA and remove centered card-like primary layouts in front/src/pages/Login.tsx
- [X] T101 Update Register, Perfil, and PerfilTecnico pages to use ChasisBloqIA and remove centered card-like primary layouts in front/src/pages/Register.tsx
- [X] T102 Update Perfil page to use profile panel/drawer language and approved field/button radii in front/src/pages/Perfil.tsx
- [X] T103 Update PerfilTecnico page to use semantic status indicators only and approved shapes for providers, models, and masked tokens in front/src/pages/PerfilTecnico.tsx
- [X] T104 Implement responsive CSS for >=1280, 1024-1279, 768-1023, and <=767 px visual cuts in front/src/tokens/visual.css
- [X] T105 [P] Add Playwright screenshot checks for desktop, tablet, and mobile user-module pages in front/tests/e2e/visual-responsive.spec.ts
- [X] T106 [P] Add text-fit checks for buttons, fields, panels, and responsive surfaces in front/tests/e2e/visual-text-fit.spec.ts
- [X] T107 Record visual QA results, screenshots, and any deviations in specs/001-modulo-usuario/evidence/visual-qa.md

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, verification, OpenAPI synchronization, visual QA, and project quality gates.

- [ ] T108 [P] Update Swagger/OpenAPI docs to include every implemented endpoint and schema from specs/001-modulo-usuario/contracts/openapi.yaml in back/app/presentation/user/openapi-user-module.yaml
- [ ] T109 [P] Add quickstart validation runner or checklist references for all curl and visual QA scenarios in specs/001-modulo-usuario/quickstart.md
- [ ] T110 [P] Document implementation fixes, blockers, visual deviations, and verification evidence in specs/001-modulo-usuario/implementation-notes.md
- [ ] T111 Run backend unit, integration, and contract tests and record command/output summary in specs/001-modulo-usuario/evidence/backend-tests.md
- [ ] T112 Run frontend unit, integration, build, and e2e tests and record command/output summary in specs/001-modulo-usuario/evidence/frontend-tests.md
- [ ] T113 Verify no frontend code stores access tokens in localStorage or sessionStorage and document result in specs/001-modulo-usuario/evidence/security-review.md
- [ ] T114 Verify service worker never caches private user responses and document result in specs/001-modulo-usuario/evidence/pwa-cache-review.md
- [ ] T115 Verify visual-design.md non-negotiable checks and update specs/001-modulo-usuario/evidence/visual-qa.md
- [ ] T116 Verify every story satisfies its independent test criteria from this file and update specs/001-modulo-usuario/evidence/story-acceptance.md

## Dependencies

### Phase Dependencies

- Phase 1 Setup must complete before Phase 2 Foundational.
- Phase 2 Foundational must complete before any user story phase.
- US1 and US2 are both P1; US1 is the suggested MVP because it proves authentication and session handling needed by later stories.
- US3 depends on authenticated access from US1.
- US4 depends on authenticated access from US1 and can run after or alongside US3 once shared auth is complete.
- Phase 7 visual system application depends on the story pages existing, but Phase 7 tests may be prepared earlier.
- Phase 8 Polish runs after selected user stories and visual phases are implemented.

### User Story Dependencies

```text
Setup -> Foundation -> US1 -> US3 -> Visual -> Polish
                    -> US2 -> Visual -> Polish
                    -> US4 -> Visual -> Polish
```

## Parallel Execution Examples

### US1 Login de usuario

```text
Parallel after foundation:
- T028 tests password credential in back/tests/unit/test_password_credential.py
- T030 contract tests auth endpoints in back/tests/contract/test_auth_contract.py
- T031 frontend Login tests in front/tests/integration/login.test.tsx
- T032 visual Login tests in front/tests/e2e/login-visual.spec.ts
- T042 frontend auth API in front/src/api/auth.ts
- T043 Login page in front/src/pages/Login.tsx
```

### US2 Registro de cuenta

```text
Parallel after US1 auth schemas/routes are in place:
- T046 registration validation tests in back/tests/unit/test_registration_validation.py
- T049 registration contract tests in back/tests/contract/test_registration_contract.py
- T050 frontend Register tests in front/tests/integration/register.test.tsx
- T051 visual Register tests in front/tests/e2e/register-visual.spec.ts
- T057 frontend register API in front/src/api/auth.ts
- T058 Register page in front/src/pages/Register.tsx
```

### US3 Gestion de perfil

```text
Parallel after foundation and US1 auth:
- T061 profile unit tests in back/tests/unit/test_profile_update.py
- T063 profile contract tests in back/tests/contract/test_profile_contract.py
- T064 frontend Perfil tests in front/tests/integration/perfil.test.tsx
- T065 visual Perfil tests in front/tests/e2e/perfil-visual.spec.ts
- T070 frontend profile API in front/src/api/profile.ts
- T071 Perfil page in front/src/pages/Perfil.tsx
```

### US4 Perfil tecnico de IA

```text
Parallel after foundation and US1 auth:
- T074 provider unit tests in back/tests/unit/test_ai_provider.py
- T076 provider token unit tests in back/tests/unit/test_provider_token.py
- T078 technical profile contract tests in back/tests/contract/test_technical_profile_contract.py
- T079 frontend PerfilTecnico tests in front/tests/integration/perfil_tecnico.test.tsx
- T080 visual PerfilTecnico tests in front/tests/e2e/perfil-tecnico-visual.spec.ts
- T089 frontend technical profile API in front/src/api/technicalProfile.ts
- T090 PerfilTecnico page in front/src/pages/PerfilTecnico.tsx
```

### Visual Design System

```text
Parallel after story pages exist:
- T093 visual variables in front/src/tokens/visual.css
- T094 typography variables in front/src/tokens/typography.css
- T095 prohibition checks in front/tests/e2e/visual-prohibitions.spec.ts
- T105 responsive screenshot checks in front/tests/e2e/visual-responsive.spec.ts
- T106 text-fit checks in front/tests/e2e/visual-text-fit.spec.ts
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1 Login de usuario.
4. Validate US1 independently with unit, integration, contract, frontend, e2e, Swagger/OpenAPI, curl evidence, and Login visual evidence.

### Incremental Delivery

1. Add US2 Registro de cuenta and validate registration independently.
2. Add US3 Gestion de perfil and validate profile read/update independently.
3. Add US4 Perfil tecnico de IA and validate provider/model/token behavior independently.
4. Apply Phase 7 visual system tasks across all user-module pages.
5. Run Phase 8 cross-cutting checks before advancing beyond implementation.

### Constitution Gates

- Do not implement code before tasks are approved.
- Every important business rule has a test task before implementation tasks in its story phase.
- Every endpoint has Swagger/OpenAPI and curl evidence tasks.
- Every visual change must respect `apartadoDIseñoGraficoBlocIA.md` and record visual QA evidence.
- Every fix needed to make the system work must be documented in implementation notes or evidence files.