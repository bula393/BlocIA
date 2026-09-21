# Frontend Test Evidence

Commands:

```powershell
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm test
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npm run build
Set-Location 'C:\Users\facub\Documents\BlocIA\front'; npx playwright test
```

Results:

- Vitest: 4 test files passed, 4 tests passed.
- Build: TypeScript and Vite production build completed successfully.
- Playwright: 1 e2e test passed.

Note: `npm install` reported 5 dependency audit findings in transitive packages. No `npm audit fix --force` was applied because it may introduce breaking changes outside this feature's scope.
