import json
import sys
from contextlib import nullcontext
from types import SimpleNamespace

from app.application.chat import ai_responder
from app.application.chat.ai_responder import AIResponder, LocalTextModel, MODEL_SYSTEM_INSTRUCTION
from app.application.chat.context import build_model_context
from app.domain.user.user import User


def test_model_context_uses_profile_and_only_recent_answered_turns():
    user = User(mail="ana@example.com", age=27, profession="Docente", display_name="Ana")
    messages = [
        {"role": "user", "content": "Mi correo es secreto@example.com", "requestId": "blocked"},
        {"role": "assistant", "content": "Sin modelo conectado", "requestId": "blocked", "providerId": None},
    ]
    for number in range(5):
        request_id = str(number)
        messages.extend([
            {"role": "user", "content": f"Pregunta {number}", "requestId": request_id},
            {"role": "assistant", "content": f"Respuesta {number}", "requestId": request_id, "providerId": "local"},
        ])

    result = build_model_context(user, "Explicá el ejercicio nuevo", messages)

    assert "Nombre visible: Ana" in result
    assert "Edad: 27 años" in result
    assert "Profesión o actividad: Docente" in result
    assert "Pregunta 0" not in result
    assert "Pregunta 1" in result and "Respuesta 4" in result
    assert "Sin modelo conectado" not in result
    assert "secreto@example.com" not in result
    assert "ana@example.com" not in result
    assert result.endswith("Consulta actual:\nExplicá el ejercicio nuevo")


def test_all_external_model_requests_include_the_deep_explanation_instruction(monkeypatch):
    responder = AIResponder()
    requests = []

    def capture(request, extract, provider_name):
        requests.append(json.loads(request.data))
        return "Respuesta"

    monkeypatch.setattr(responder, "_text", capture)
    for provider in ("openai", "google", "anthropic"):
        assert responder.generate(provider, "modelo-prueba", "Consulta actual:\n¿Qué es una API?", "clave") == "Respuesta"
    assert responder.generate("openai", "o3-prueba", "Consulta actual:\nOtro ejercicio", "clave") == "Respuesta"

    openai, google, anthropic, openai_reasoning = requests
    assert openai["messages"][0] == {"role": "system", "content": MODEL_SYSTEM_INSTRUCTION}
    assert openai["messages"][1]["content"].startswith("Consulta actual:")
    assert google["systemInstruction"]["parts"][0]["text"] == MODEL_SYSTEM_INSTRUCTION
    assert google["contents"][0]["parts"][0]["text"].startswith("Consulta actual:")
    assert anthropic["system"] == MODEL_SYSTEM_INSTRUCTION
    assert anthropic["messages"][0]["content"].startswith("Consulta actual:")
    assert openai_reasoning["messages"][0] == {"role": "developer", "content": MODEL_SYSTEM_INSTRUCTION}
    assert "explicación en profundidad" in MODEL_SYSTEM_INSTRUCTION
    assert "procedimiento" in MODEL_SYSTEM_INSTRUCTION


def test_local_model_receives_the_same_instruction(monkeypatch, tmp_path):
    (tmp_path / "model.safetensors").touch()
    received = []

    class FakeTokens:
        shape = (1, 1)

        def __getitem__(self, key):
            return self

    class FakeTokenizer:
        eos_token_id = 0

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def apply_chat_template(self, messages, **kwargs):
            received.extend(messages)
            return FakeTokens()

        def decode(self, tokens, **kwargs):
            return "Explicación detallada"

    class FakeModel:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def eval(self):
            pass

        def generate(self, tokens, **kwargs):
            assert kwargs["max_new_tokens"] >= 1024
            return [FakeTokens()]

    monkeypatch.setattr(ai_responder, "LOCAL_MODEL_PATH", tmp_path)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(set_num_threads=lambda count: None, inference_mode=nullcontext))
    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(AutoModelForCausalLM=FakeModel, AutoTokenizer=FakeTokenizer))

    assert LocalTextModel().generate("Consulta actual:\nResolvé este ejercicio") == "Explicación detallada"
    assert received == [
        {"role": "system", "content": MODEL_SYSTEM_INSTRUCTION},
        {"role": "user", "content": "Consulta actual:\nResolvé este ejercicio"},
    ]
