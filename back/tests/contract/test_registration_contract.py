from app.application.user.google_auth import registration_token


def test_registration_contract(client):
    response = client.post("/auth/register", json={"mail": "contract@example.com", "password": "ClaveSegura-123", "age": 22, "profession": "Tester"})
    assert response.status_code == 201
    completion = client.post("/auth/register/complete-google", json={"registrationToken": registration_token("contract-google", "contract.google@example.com"), "age": 22, "profession": "Tester"})
    assert completion.status_code == 201
