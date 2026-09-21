# US2 Register Curl Evidence

Planned/validated endpoints:

```bash
curl -i -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"mail":"nuevo.usuario@example.com","password":"ClaveSegura-123","age":28,"profession":"Estudiante"}'

curl -i -X POST http://localhost:8000/auth/register/complete-google \
  -H "Content-Type: application/json" \
  -d '{"registrationToken":"google-subject","age":20,"profession":"Docente"}'
```

Automated evidence: `back/tests/integration/test_registration_flow.py` and `back/tests/contract/test_registration_contract.py` passed.
