# Research: Correccion Grafica

## Decision: Use known login/register patterns only at interaction-pattern level

**Rationale**: Known products converge on simple access patterns: clear first action, minimal form
fields, obvious path between login and account creation, visible brand mark, and direct recovery from
unauthenticated states. These patterns reduce user confusion without requiring copying another
site's visual design.

**Alternatives considered**:

- Copy a recognizable login/register layout from a known site: rejected because the BloqIA visual
  system is normative and prohibits generic card-heavy or decorative layouts.
- Invent a fully custom access flow: rejected because login/register should remain predictable and
  easy to test.

## Decision: Public start page follows a top-right identity/action pattern

**Rationale**: Many known product landing pages place brand or session affordances near the top
edge and expose a clear sign-in path without forcing users to search. For BloqIA, the requested
circle logo at top right and login action toward the right side fit that pattern while preserving the
block-based visual language.

**Alternatives considered**:

- Centered logo and centered CTA: rejected because the user explicitly requested top-right logo and
  right-side login action.
- Marketing-style hero with large illustration: rejected because the visual system prohibits generic
  illustration patterns and decorative hero treatments.

## Decision: Login/Register forms stay sparse and task-focused

**Rationale**: Common login/register pages from products such as GitHub, Google, Slack, Notion,
Stripe, and Linear generally minimize required decisions, keep one primary action, and provide a
secondary path to account creation or sign-in. BloqIA should keep that usability pattern while using
rectangular block surfaces, approved radii, and no floating primary cards.

**Alternatives considered**:

- Multi-panel auth marketing page: rejected because it adds visual noise and risks card-like layout.
- Dense registration form with optional fields: rejected because registration already has required
  fields from the user module and should stay focused.

## Decision: Public routes are start, login, and register only

**Rationale**: The spec explicitly states that every section beyond start, login, and register
requires authentication. This keeps route behavior testable and avoids accidental private-content
exposure.

**Alternatives considered**:

- Make profile visible with empty state: rejected because protected content must not render without
  valid JWT.
- Allow technical profile shell without data: rejected because it could imply access to private
  configuration.

## Decision: Route guard checks JWT before rendering private content

**Rationale**: The route guard must prevent private UI from flashing before authentication is
known. The frontend must treat missing, invalid, or expired JWT as unauthenticated and show a clear
login path. Backend APIs remain the final authority for private data.

**Alternatives considered**:

- Check token after page render: rejected because private content could appear briefly.
- Store JWT in localStorage/sessionStorage for persistence: rejected by project architecture and
  security constraints.

## Decision: JWT work is limited to frontend contract unless backend incompatibility is found

**Rationale**: The user requested "solo cambia el front" except for JWT. Planning therefore assumes
existing auth can provide or be adapted to a JWT-like access token contract without new product
features. Backend changes are deferred unless implementation discovers token incompatibility.

**Alternatives considered**:

- Redesign backend authentication now: rejected because it exceeds the requested scope.
- Ignore JWT and reuse any opaque token without validation semantics: rejected because the spec
  explicitly requires valid JWT before protected routes.

## Decision: Visual compliance is a release gate

**Rationale**: `apartadoDIseñoGraficoBlocIA.md` is normative. The start, login, register, and guard
states must pass checks for palette, radii, layout, prohibited visual elements, responsive behavior,
and text fit.

**Alternatives considered**:

- Treat visual compliance as post-polish: rejected because this feature is explicitly a graphic
  correction.
- Allow one-off exceptions for public start page: rejected because the visual system says no
  exceptions for a single place.
