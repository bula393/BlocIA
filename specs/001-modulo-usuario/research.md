# Research: Modulo de Usuario

## Decision: Backend as source of truth for user identity and technical credentials

**Rationale**: Login, registration, profile ownership, Google linking, provider token ownership,
and token state are business and security decisions. They must be enforced by the backend so the
frontend can only reflect accepted state and cannot create authority by changing client state.

**Alternatives considered**:

- Client-managed authentication state: rejected because browser state can be modified and cannot
  enforce account ownership.
- Duplicating token status in local store: rejected because it risks showing stale or unauthorized
  information.

## Decision: React + Vite + TypeScript PWA for the frontend

**Rationale**: The user supplied this as the normative frontend architecture. It supports the four
main user-module sections as pages while keeping the application installable and fast to open.

**Alternatives considered**:

- Server-rendered frontend: rejected because it does not match the supplied frontend architecture.
- Plain JavaScript frontend: rejected because the requested architecture requires TypeScript.

## Decision: Visual work is governed by `apartadoDIseñoGraficoBlocIA.md`

**Rationale**: The visual system is normative and explicitly says that if a visual choice is not
listed there, it must not be used. Planning must therefore add visual phases for tokens,
structural layout, component application, responsive adaptation, and visual QA before further UI
work.

**Alternatives considered**:

- Keep the current generic form layout: rejected because the visual system bans floating card-like
  layouts as primary structure and requires a block chassis.
- Treat the visual system as optional styling guidance: rejected because the constitution requires
  respecting `apartadoDIseñoGraficoBlocIA.md` for web design.
- Add decorative gradients or new colors to modernize the UI: rejected because the palette is
  closed and gradients are prohibited.

## Decision: TanStack Query for server cache and Zustand for local-only UI state

**Rationale**: Profile data, authentication status, AI providers, AI models, and token status are
server-authoritative data and belong in server cache. Local UI state such as open panels, active
tabs, and unsaved form drafts can use Zustand because the backend does not authorize those values.

**Alternatives considered**:

- Zustand for all state: rejected because it would mix server-authoritative data with local UI
  state.
- Component-only state for all screens: rejected because shared user/profile state must stay
  coherent across pages.

## Decision: Token session handling uses access token in memory and refresh via httpOnly cookie

**Rationale**: Keeping the access token in memory avoids exposing the complete session through
browser storage. Refresh through an httpOnly cookie keeps renewal outside direct JavaScript access.

**Alternatives considered**:

- localStorage or sessionStorage: rejected because injected scripts could read long-lived tokens.
- Plain cookie-only access without a memory token: rejected because the supplied architecture names
  the access-token-in-memory pattern.

## Decision: PostgreSQL for persistence

**Rationale**: The feature requires unique mail identity, relational ownership between users,
Google identities, providers, models, and provider tokens, plus transactional updates. PostgreSQL
fits these constraints and supports indexes for uniqueness and lookup without relying on in-memory
scans.

**Alternatives considered**:

- In-memory storage: rejected because user identity and token state must persist and remain unique.
- Document-only storage: rejected because uniqueness, ownership, and relational constraints are
  central to the feature.

## Decision: Provider tokens are masked after save and represented by status

**Rationale**: The spec requires that saved provider tokens never be fully displayed. Users need to
know whether a provider is configured, invalid, or requires attention without seeing the secret.

**Alternatives considered**:

- Display token after save for convenience: rejected because it violates the specification and
  increases secret exposure.
- Store provider configuration without status: rejected because users could not quickly identify
  which providers need action.

## Decision: Repeated failed login attempts do not block the account

**Rationale**: The clarification session selected the behavior that invalid login attempts keep
returning the same safe rejection message without locking the account. This keeps acceptance tests
simple and avoids introducing a recovery or support flow that the specification does not request.

**Alternatives considered**:

- Temporary lockout after repeated failures: rejected by clarification answer.
- Additional verification after repeated failures: rejected by clarification answer.
- Manual password recovery lockout: rejected because it would expand the feature scope.

## Decision: HTTP contracts are documented as OpenAPI

**Rationale**: The constitution requires Swagger/OpenAPI synchronization for every added endpoint.
Planning the contract now gives `/speckit-tasks` a concrete API surface to turn into backend,
frontend, and testing tasks.

**Alternatives considered**:

- Informal endpoint list: rejected because it is not enough to satisfy the constitution's API
  documentation requirement.
- UI-only contract: rejected because the feature includes backend-authenticated user and token
  operations.

## Decision: Story work is grouped into Back, Front, and Testing lanes

**Rationale**: The user explicitly requested that every story be separated into back, front, and
testing phases. The plan preserves each user story while mapping it to those lanes for the later
`/speckit-tasks` phase.

**Alternatives considered**:

- One phase per user story: rejected because it would not satisfy the requested phase split.
- One phase per layer only: rejected because traceability to each story would become weaker.
