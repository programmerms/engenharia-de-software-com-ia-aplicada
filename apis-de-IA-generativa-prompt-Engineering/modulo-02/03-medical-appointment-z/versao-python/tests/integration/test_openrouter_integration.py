from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from app.config import LLMConfig
from app.llm import Intent, OpenRouterMedicalLLM


@pytest.mark.llm_integration
def test_openrouter_returns_structured_intent_when_opted_in() -> None:
    """Valida provider real somente com credencial e opt-in explícitos."""

    if os.getenv("RUN_LLM_INTEGRATION_TESTS") != "1":
        pytest.skip("provider real desabilitado; defina RUN_LLM_INTEGRATION_TESTS=1")
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY não configurada")

    service = OpenRouterMedicalLLM(LLMConfig.from_environment())
    result = service.extract_intent(
        "Quero agendar uma consulta",
        [{"id": 1, "name": "Dr. Alicio da Silva", "specialty": "Cardiologia"}],
        datetime.now(timezone.utc),
    )

    assert result.intent in {Intent.SCHEDULE, Intent.CANCEL, Intent.UNKNOWN}
