# Visual Design Plan: Modulo de Usuario

## Source of Truth

The visual source of truth is `apartadoDIseñoGraficoBlocIA.md`. If a visual choice is not allowed
there, it must not be introduced in the user module.

## Visual Design Phases

### Phase V1: Visual Tokens and Prohibitions

- Define CSS variables only from the approved palette: `#17212B`, `#FFF6DB`, `#FFFFFF`,
  `#1C489B`, `#3F8585`, `#E98973`, `#D95C5C`, and `#66727A`.
- Use only admitted opacity derivatives from the visual system.
- Use Archivo for interface, titles, buttons, and numeric readings; use Source Serif 4 only for
  BloqIA long-form responses.
- Ban gradients, violet/indigo, diffuse shadows, pill buttons, decorative blobs, chat tails,
  emoji, and generic AI icons.

### Phase V2: Structural Layout

- Replace any centered card-like auth/profile layout with a block chassis.
- Desktop layout must reserve structural regions: left rail, paper reading area, right status
  panel, and edge meter where applicable.
- User-module pages must reuse the same chassis logic even when they do not show conversation
  content: dark rigid frame, clear paper/white work surface, filete separators, and no floating
  cards.
- Profile-related surfaces use the drawer or panel language: 0 px radius for structural regions,
  4 px radius only for fields/buttons/dialogs.

### Phase V3: Components for User Module

- Login and Register use one primary blue action per screen and concrete verbs.
- Error states use `#D95C5C` as fill/band indicator only, with grafito text where text appears on
  red or salmon surfaces.
- Profile and Technical Profile state indicators use semantic colors only for status, never for
  decoration.
- Provider/token states must be readable without exposing full tokens and without introducing new
  shapes beyond rectangles, 1 px filetes, 3 px bars, and allowed pips.

### Phase V4: Responsive Adaptation

- At 1024-1279 px, collapse status density and reduce reading width as specified by the visual
  system.
- At 768-1023 px, move status information into the header.
- At 767 px and below, use bottom rail, top 4 px meter, full-width content with 16 px margins, and
  no card stacking.

### Phase V5: Visual QA Gates

- Verify desktop, tablet, and mobile screenshots against the visual system.
- Verify no prohibited colors, gradients, pill radii, diffuse shadows, blobs, emoji, or chat-tail
  shapes appear in the user module.
- Verify text fits inside buttons, fields, panels, and responsive surfaces.
- Verify focus states use blue action/focus semantics and do not use state colors decoratively.
- Verify service and auth behavior remains unchanged after visual work.

## Story Mapping

| Story | Visual Work |
|-------|-------------|
| US1 Login de usuario | Login surface, primary action, Google action, safe error state, status-preserving shell |
| US2 Registro de cuenta | Register surface, password feedback, missing-fields completion, validation states |
| US3 Gestion de perfil | Profile panel/drawer language, editable fields, protected-field errors |
| US4 Perfil tecnico de IA | Provider/model listing, token state indicators, masked-token presentation |

## Non-Negotiable Acceptance Checks

- No page may use floating rounded cards as the primary layout structure.
- No UI element may use pill radius.
- No page may introduce colors outside the approved palette or admitted opacity derivatives.
- No token, credential, or auth state may be represented as frontend-authoritative state.
- Every visual change must keep the backend as source of truth for identity and technical
  credentials.
