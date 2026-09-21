# Backend Test Evidence

Command:

```powershell
Set-Location 'C:\Users\facub\Documents\BlocIA\back'; python -m pytest
```

Result: 15 passed, 2 warnings.

Coverage included:

- Unit tests for password credential, login, registration validation, password policy, profile updates, AI providers, AI models, and provider tokens.
- Integration tests for registration, profile, and technical profile flows.
- Contract tests for auth, registration, profile, and technical profile endpoints.
