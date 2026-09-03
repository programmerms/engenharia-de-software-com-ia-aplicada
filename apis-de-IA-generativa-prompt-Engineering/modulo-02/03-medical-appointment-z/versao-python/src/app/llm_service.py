"""Fronteira canônica do serviço LangChain/OpenRouter.

Os símbolos são reexportados do módulo histórico `llm.py` para que a mudança
de nomenclatura não crie uma segunda implementação do serviço ou dos fakes.
"""

from app.llm import (
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
