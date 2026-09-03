"""Camada de linguagem do template.

O código histórico ainda vive em ``app/llm.py`` para compatibilidade com
imports das aulas anteriores. Este pacote é a superfície canônica e carrega
essa implementação única como módulo legado, evitando uma segunda versão do
serviço durante a migração incremental.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_LEGACY_NAME = "app._llm_legacy"
_LEGACY_PATH = Path(__file__).parent.parent / "llm.py"

if _LEGACY_NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_LEGACY_NAME, _LEGACY_PATH)
    if _spec is None or _spec.loader is None:
        raise ImportError("Não foi possível carregar a implementação legada do LLM")
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_LEGACY_NAME] = _module
    _spec.loader.exec_module(_module)
else:
    _module = sys.modules[_LEGACY_NAME]

Intent = _module.Intent
IntentExtraction = _module.IntentExtraction
MessageGeneration = _module.MessageGeneration
LLMError = _module.LLMError
MedicalLLM = _module.MedicalLLM
OpenRouterMedicalLLM = _module.OpenRouterMedicalLLM
FakeMedicalLLM = _module.FakeMedicalLLM
OfflineMedicalLLM = _module.OfflineMedicalLLM

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
