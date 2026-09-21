# US1 Login Curl Evidence

Planned/validated endpoints:

```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"mail":"usuario.demo@example.com","password":"ClaveSegura-123"}'

curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"mail":"usuario.demo@example.com","password":"incorrecta"}'

curl -i http://localhost:8000/auth/google/start

curl -i -X POST http://localhost:8000/auth/google/complete \
  -H "Content-Type: application/json" \
  -d '{"code":"usuario.demo@gmail.com","state":"demo"}'
```

Automated evidence: `back/tests/contract/test_auth_contract.py`, `back/tests/integration`, and `front/tests/e2e/login.spec.ts` passed.
