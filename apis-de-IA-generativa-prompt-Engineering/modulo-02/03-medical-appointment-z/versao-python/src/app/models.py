"""Modelos Pydantic canônicos dos contratos estruturados da aplicação.

As implementações são reexportadas do módulo legado para preservar a API do
template enquanto a nomenclatura didática da feature evolui.
"""

from app.llm import Intent, IntentExtraction, MessageGeneration

__all__ = ["Intent", "IntentExtraction", "MessageGeneration"]
