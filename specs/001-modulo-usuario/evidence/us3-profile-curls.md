# US3 Profile Curl Evidence

Planned/validated endpoints:

```bash
curl -i http://localhost:8000/profile \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -i -X PATCH http://localhost:8000/profile \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"age":29,"profession":"Programador"}'
```

Automated evidence: `back/tests/integration/test_profile_flow.py` and `back/tests/contract/test_profile_contract.py` passed.
