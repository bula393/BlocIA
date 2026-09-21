# Visual QA Evidence

## Scope

Phase 7 applied the visual system from `apartadoDIseñoGraficoBlocIA.md` to the user module.

## Implemented Checks

- Approved palette and opacity derivatives are centralized in `front/src/tokens/visual.css`.
- Typography roles are centralized in `front/src/tokens/typography.css`.
- Shared block chassis is implemented in `front/src/components/chasis/ChasisBloqIA.tsx`.
- Left rail active state uses a 3 px blue bar without rounded active background.
- Meter component supports desktop 10 px edge meter and mobile 4 px top meter.
- Profile drawer/panel language uses structural 0 px radius and 4 px controls.
- Login, Register, Perfil, and Perfil Tecnico pages use the shared chassis.
- Technical profile status indicators use semantic status bars and do not expose full tokens.

## Validation Commands

```powershell
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm test
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm run build
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npx playwright test
```

## Results

- Vitest: 4 test files passed, 4 tests passed.
- Build: TypeScript and Vite production build completed successfully.
- Playwright: 12 tests passed.

## Visual Gates Covered

- No prohibited CSS patterns for gradients, violet/indigo, diffuse shadows, pill radius, blobs,
  emoji, or chat-tail shapes were detected by `visual-prohibitions.spec.ts`.
- Desktop, compact desktop, tablet, and mobile chassis rendering passed in
  `visual-responsive.spec.ts`.
- Button, field, chip, panel text-fit checks passed in `visual-text-fit.spec.ts`.
- Login, Register, Perfil, and Perfil Tecnico visual page checks passed.

## Deviations

- No deviations recorded for Phase 7.
