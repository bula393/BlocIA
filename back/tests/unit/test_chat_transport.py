import httpx
import pytest

from app.application.chat.ai_responder import AIResponder, AIResponseUnavailableError


def test_shared_transport_keeps_each_users_credentials_and_prompt_separate():
    requests = []

    def reply(request):
        requests.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "Respuesta"}}]},
                              headers={"set-cookie": "session=previous-user; Path=/"})

    client = httpx.Client(transport=httpx.MockTransport(reply))
    responder = AIResponder(client)
    try:
        responder.generate("openai", "example", "Primera consulta", "first-key")
        responder.generate("openai", "example", "Segunda consulta", "second-key")
        assert responder._http_client() is client
        assert [request.headers["authorization"] for request in requests] == ["Bearer first-key", "Bearer second-key"]
        assert all("cookie" not in request.headers for request in requests)
        assert b"Primera consulta" not in requests[1].content
    finally:
        responder.close()
    assert client.is_closed


@pytest.mark.parametrize(("status", "payload", "message"), [
    (429, {"error": {"code": "insufficient_quota"}}, "cuota o límite"),
    (429, {"error": {"status": "RESOURCE_EXHAUSTED"}}, "cuota o límite"),
    (401, {}, "rechazó la clave"),
    (404, {}, "no encontró el modelo"),
    (503, {}, "problema temporal"),
    (200, {"choices": []}, "respuesta vacía"),
])
def test_pooled_transport_preserves_provider_errors(status, payload, message):
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=payload))) as client:
        with pytest.raises(AIResponseUnavailableError, match=message):
            AIResponder(client).generate("openai", "example", "Consulta privada", "private-key")


def test_connection_timeouts_remain_retryable_without_echoing_secrets():
    def timeout(request):
        raise httpx.ReadTimeout("private-key Consulta privada", request=request)

    with httpx.Client(transport=httpx.MockTransport(timeout)) as client:
        with pytest.raises(AIResponseUnavailableError) as error:
            AIResponder(client).generate("openai", "example", "Consulta privada", "private-key")
    assert "private-key" not in str(error.value)
    assert "Consulta privada" not in str(error.value)


def test_provider_connection_failures_explain_server_network_requirement_without_echoing_secrets():
    def blocked(request):
        raise httpx.ConnectError("blocked", request=request)

    with httpx.Client(transport=httpx.MockTransport(blocked)) as client:
        with pytest.raises(AIResponseUnavailableError, match="red saliente") as error:
            AIResponder(client).generate("groq", "llama-example", "private-prompt", "private-key")

    assert "private-key" not in str(error.value)
    assert "private-prompt" not in str(error.value)


@pytest.mark.parametrize("status", [401, 403])
def test_google_disabled_service_account_reports_recovery_with_same_key(status):
    payload = {"error": {"code": status, "status": "UNAUTHENTICATED", "message": "private-key private-prompt",
                         "details": [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": "ACCOUNT_STATE_INVALID"}]}}
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=payload))) as client:
        with pytest.raises(AIResponseUnavailableError) as error:
            AIResponder(client).generate("google", "gemini-3.8-flash", "private-prompt", "private-key")
    message = str(error.value)
    assert "ACCOUNT_STATE_INVALID" in message
    assert "cuenta de servicio" in message
    assert "misma clave" in message
    assert "private-key" not in message and "private-prompt" not in message


def test_google_auth_key_is_sent_unchanged_in_native_api_header():
    requests = []

    def reply(request):
        requests.append(request)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "OK"}]}}]})

    key = "AQ.test-private-auth-key"
    with httpx.Client(transport=httpx.MockTransport(reply)) as client:
        assert AIResponder(client).generate("google", "gemini-3.8-flash", "Prueba", key) == "OK"
    assert requests[0].headers["x-goog-api-key"] == key
    assert "authorization" not in requests[0].headers
    assert key not in str(requests[0].url)
