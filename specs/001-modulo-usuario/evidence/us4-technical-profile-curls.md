# US4 Technical Profile Curl Evidence

Planned/validated endpoints:

```bash
curl -i http://localhost:8000/technical-profile/providers \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -i -X POST http://localhost:8000/technical-profile/tokens \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"providerId":"openai","token":"test-token-value"}'

curl -i -X DELETE http://localhost:8000/technical-profile/tokens/openai \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Automated evidence: `back/tests/integration/test_technical_profile_flow.py` and `back/tests/contract/test_technical_profile_contract.py` passed.
