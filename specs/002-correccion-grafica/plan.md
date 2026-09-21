# Implementation Plan: Correccion Grafica

**Branch**: `002-correccion-grafica` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-correccion-grafica/spec.md`

## Summary

Crear una pagina publica de inicio para visitantes, mantener login y register como rutas publicas,
y proteger el resto de las rutas con un token JWT valido. El alcance de implementacion sera
principalmente frontend: rutas, guardas visuales, composicion de inicio/login/register y QA visual.
La unica excepcion funcional es asegurar que el frontend use y valide el contrato de JWT antes de
mostrar contenido privado; no se planifican nuevos endpoints backend para esta correccion.

El diseno debe inspirarse en patrones reconocibles de productos conocidos sin copiarlos: entrada
clara, identidad visible, una accion primaria evidente, formularios simples, opcion secundaria para
registro/login y errores concretos. Todo debe reinterpretarse dentro del sistema visual de BloqIA:
bloques macizos, paleta cerrada, radios permitidos, sin tarjetas flotantes, sin gradientes y sin
botones pildora.

## Technical Context

**Language/Version**: Frontend TypeScript with React + Vite. Existing backend remains FastAPI for
current authentication/profile endpoints.

**Primary Dependencies**: React, Vite, TypeScript, TanStack Query for server state, Zustand only for
local UI state, Playwright/Vitest for visual and route behavior checks.

**Storage**: No new persistent storage. The frontend must not use `localStorage` or `sessionStorage`
for access tokens. JWT state is treated as in-memory/session-auth state supplied by existing auth
flow.

**Testing**: Vitest for route guard and component behavior; Playwright for public landing, login,
register, protected-route guard, responsive visual QA, and prohibited visual elements.

**Target Platform**: Web PWA frontend.

**Project Type**: Frontend correction over an existing full-stack web app.

**Performance Goals**: Public start, login, and register screens render visibly in under 2 seconds
on normal local/dev conditions. Route guard decisions should be visible before protected content is
shown.

**Constraints**: Preserve `apartadoDIseñoGraficoBlocIA.md` as normative visual source. Public routes
are start, login, and register only. All other routes require valid JWT before protected content is
shown. Do not introduce new backend routes unless later tasks explicitly require JWT compatibility.

**Scale/Scope**: Four user-facing flows: public start page, public login/register access,
protected-route guard, and visual consistency across public/protected guard states.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification traceability**: PASS. Plan maps to FR-001 through FR-014 and all four user
  stories in [spec.md](spec.md).
- **Layered responsibility boundaries**: PASS. This correction is frontend-focused; JWT remains an
  authentication contract and protected data must still come from server-authoritative APIs.
- **Testing, verification, documentation**: PASS. Route behavior, visual QA, and JWT guard behavior
  have planned automated checks.
- **Usable discovery/interface**: PASS. Public start and auth screens follow the visual system and
  provide one clear login path.
- **Visual system compliance**: PASS. `apartadoDIseñoGraficoBlocIA.md` is explicitly governing
  layout, color, radius, typography, motion, and prohibitions.
- **Phase discipline**: PASS. This command creates planning/design documents only.

## Project Structure

### Documentation (this feature)

```text
specs/002-correccion-grafica/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── route-access.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
front/
├── src/
│   ├── app/
│   │   ├── router.tsx
│   │   └── routeGuard.ts
│   ├── pages/
│   │   ├── Inicio.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Perfil.tsx
│   │   └── PerfilTecnico.tsx
│   ├── components/
│   │   ├── chasis/
│   │   ├── estado/
│   │   └── overlay/
│   ├── api/
│   │   └── client.ts
│   ├── tokens/
│   │   ├── visual.css
│   │   └── typography.css
│   └── types/
└── tests/
    ├── integration/
    └── e2e/
```

**Structure Decision**: Use existing `front/` app structure. Add `Inicio.tsx` and route guard logic
under `front/src/app/`. Do not plan backend source changes for page composition; JWT compatibility
is treated as a frontend auth contract using existing token flow.

## Pattern Research Targets

Planning research will summarize common patterns from known login/register experiences at a
pattern level only, without copying UI: GitHub-style direct sign-in with secondary create-account
path, Google-style sparse form progression, Notion/Slack-style top-right sign-in entry, and
Stripe/Linear-style clear primary CTA with minimal supporting text. These patterns must be adapted
to BloqIA blocks, not reproduced visually.

## Story Phase Mapping

| Story | Front | JWT/Auth | Visual QA |
|-------|-------|----------|-----------|
| US1 Ver inicio publico | Add public `Inicio` route, circle logo top-right, phrase, login CTA | No token required | Logo/phrase/button visible and non-overlapping |
| US2 Login/Register publicos | Keep login/register reachable without token and linked from start | No token required | Forms follow BloqIA visual system |
| US3 Rutas privadas protegidas | Guard all non-public routes before rendering private content | Valid JWT required | Guard state offers login path without prohibited visuals |
| US4 Coherencia visual normativa | Apply visual system to start/auth/guard states | Preserve server-authoritative auth | Palette/radius/layout/prohibition checks |

## Complexity Tracking

No constitution violations require justification.

## Post-Design Constitution Check

- **Specification traceability**: PASS. Research, route contract, data model, and quickstart trace to
  FR-001 through FR-014.
- **Layer boundaries**: PASS. Frontend route visibility is separate from backend data authority;
  JWT is not stored in browser storage.
- **Testing and documentation**: PASS. Quickstart includes route, JWT, visual, and responsive checks.
- **Visual design compliance**: PASS. The visual source of truth is explicitly referenced in each
  frontend-facing design artifact.
- **Phase discipline**: PASS. Only Spec Kit planning/design artifacts are created or updated.
