# Implementation Notes

- Implemented backend as FastAPI with domain/application/infrastructure/presentation separation.
- Added in-memory repository implementations to make tests and local validation runnable without requiring a PostgreSQL service. The migration file documents the intended PostgreSQL schema.
- Implemented React + Vite + TypeScript PWA shell with TanStack Query for server state and Zustand only for local UI draft state.
- Added `playwright.config.ts` so Playwright only collects `front/tests/e2e` and does not attempt to execute Vitest integration tests.
- Adjusted `front/tsconfig.json` to compile production `src` only; Vitest handles test compilation.
- Installed Playwright Chromium locally to run the e2e validation.
- `npm install` reported 5 dependency audit findings in transitive dependencies; force-fixing was not applied to avoid breaking dependency changes during feature implementation.
