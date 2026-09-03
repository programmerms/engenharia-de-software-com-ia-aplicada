from datetime import datetime, timezone

import pytest

from app.config import LLMConfig
from app.llm import (
    FakeMedicalLLM,
    Intent,
    IntentExtraction,
    LLMError,
    MessageGeneration,
    OpenRouterMedicalLLM,
)


def test_fake_llm_supplies_structured_values_without_provider() -> None:
    fake = FakeMedicalLLM(
        extraction=IntentExtraction(intent="schedule", patient_name="Maria Santos"),
        generated=MessageGeneration(message="Resposta simulada"),
    )
    assert fake.extract("qualquer texto").intent == "schedule"
    assert fake.message("schedule", {}).message == "Resposta simulada"


class StructuredDouble:
    """Runnable mínimo que simula o retorno de Structured Output."""

    def __init__(self, value: object) -> None:
        self.value = value

    def invoke(self, prompt: str) -> dict[str, object]:
        assert prompt
        return {"parsed": self.value, "raw": None, "parsing_error": None}


class ChatModelDouble:
    """Modelo fake usado para provar que o serviço não acessa rede."""

    def __init__(self, value: object) -> None:
        self.value = value

    def with_structured_output(self, schema: object, include_raw: bool = False) -> StructuredDouble:
        assert include_raw is True
        return StructuredDouble(self.value)


def test_openrouter_service_consumes_structured_model_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = IntentExtraction(intent=Intent.SCHEDULE, patient_name="Maria Santos")
    service = OpenRouterMedicalLLM(LLMConfig(api_key="test-key"))
    monkeypatch.setattr(service, "_model", ChatModelDouble(expected))

    result = service.extract_intent("Quero agendar", [], datetime.now(timezone.utc))

    assert result == expected


def test_openrouter_service_wraps_invalid_structured_response(monkeypatch: pytest.MonkeyPatch) -> None:
    service = OpenRouterMedicalLLM(LLMConfig(api_key="test-key"))
    monkeypatch.setattr(service, "_model", ChatModelDouble(MessageGeneration(message="ok")))

    with pytest.raises(LLMError, match="structured intent"):
        service.extract_intent("Quero agendar", [], datetime.now(timezone.utc))
