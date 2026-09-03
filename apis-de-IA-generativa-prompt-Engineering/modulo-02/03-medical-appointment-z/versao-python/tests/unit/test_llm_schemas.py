from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.config import LLMConfig
from app.llm import Intent, IntentExtraction, MessageGeneration


def test_intent_extraction_restricts_intent_contract() -> None:
    result = IntentExtraction(
        intent=Intent.SCHEDULE,
        professional_id=1,
        patient_name="Maria Santos",
        datetime=datetime(2026, 9, 4, 16, tzinfo=timezone.utc),
    )

    assert result.intent is Intent.SCHEDULE
    assert result.professional_id == 1


def test_invalid_intent_is_rejected() -> None:
    with pytest.raises(ValidationError):
        IntentExtraction(intent="book")


def test_message_generation_requires_non_empty_message() -> None:
    with pytest.raises(ValidationError):
        MessageGeneration(message="")


def test_config_can_be_created_without_api_key_for_offline_tests() -> None:
    config = LLMConfig.from_environment({"OPENROUTER_MODEL": "test-model"})

    assert config.model == "test-model"
    assert config.api_key is None
    assert config.base_url == "https://openrouter.ai/api/v1"


def test_real_client_configuration_requires_api_key_only_on_demand() -> None:
    config = LLMConfig.from_environment({})

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        config.require_api_key()


def test_llm_timeout_defaults_to_thirty_seconds_when_environment_is_absent() -> None:
    settings = LLMConfig.from_environment({})

    assert settings.timeout == 30.0


def test_llm_timeout_uses_environment_override_without_waiting() -> None:
    settings = LLMConfig.from_environment({"LLM_TIMEOUT_SECONDS": "10"})

    assert settings.timeout == 10.0


def test_invalid_llm_timeout_is_rejected_before_provider_configuration() -> None:
    with pytest.raises(ValueError):
        LLMConfig.from_environment({"LLM_TIMEOUT_SECONDS": "not-a-number"})
