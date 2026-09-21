# Route Access Contract: Correccion Grafica

## Public Routes

| Route | Access | Expected Behavior |
|-------|--------|-------------------|
| `/` | Public | Shows start page with top-right circular logo, main phrase, and login action |
| `/login` | Public | Shows login page without requiring JWT |
| `/register` | Public | Shows register page without requiring JWT |

## Protected Routes

| Route Pattern | Access | Expected Behavior Without Valid JWT | Expected Behavior With Valid JWT |
|---------------|--------|--------------------------------------|----------------------------------|
| `/perfil` | Protected | Do not show profile content; show login path | Show profile page |
| `/perfil-tecnico` | Protected | Do not show technical profile content; show login path | Show technical profile page |
| Any future app route not listed as public | Protected | Do not show private content; show login path | Show requested route if user is authorized |

## JWT Guard Contract

- Missing JWT: unauthenticated.
- Invalid JWT: unauthenticated.
- Expired JWT: unauthenticated.
- Valid JWT: authenticated for frontend route visibility.
- Backend APIs remain authoritative for private data.
- JWT must not be persisted in `localStorage` or `sessionStorage`.

## Visual Contract

- Start, login, register, and guard states must use only allowed colors and forms from
  `apartadoDIseñoGraficoBlocIA.md`.
- The temporary logo is a circle and is allowed only as a logo placeholder.
- Primary actions use one blue button per screen.
- No floating card primary layouts, pill buttons, decorative gradients, diffuse shadows, emoji, or
  prohibited AI iconography.
