"""Fachada histórica para a fronteira canônica ``app.llm.service``.

Os símbolos são reexportados para preservar imports existentes sem duplicar a
implementação do serviço ou dos fakes.
"""

from app.llm.service import (
    FakeMedicalLLM,
    Intent,
    IntentExtraction,
    LLMError,
    MedicalLLM,
    MessageGeneration,
    OfflineMedicalLLM,
    OpenRouterMedicalLLM,
)

__all__ = [
    "FakeMedicalLLM",
    "Intent",
    "IntentExtraction",
    "LLMError",
    "MedicalLLM",
    "MessageGeneration",
    "OfflineMedicalLLM",
    "OpenRouterMedicalLLM",
]
