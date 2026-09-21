# US4 Visual QA Evidence

Implemented:

- Start, login, register, and protected-route guard states use the BloqIA block chassis.
- Public start logo is a plain circle and does not introduce additional circular shapes.
- Visual CSS uses the approved palette, approved opacity derivatives, and allowed radii.
- Public/auth/guard states avoid gradients, floating cards as primary layout, pill buttons, diffuse shadows, emoji, and prohibited AI iconography.

Validated by:

- `front/tests/e2e/correccion-grafica-visual.spec.ts`
- `front/tests/e2e/correccion-grafica-responsive.spec.ts`
- `front/tests/e2e/correccion-grafica-text-fit.spec.ts`
- Existing visual regression checks under `front/tests/e2e/`.
