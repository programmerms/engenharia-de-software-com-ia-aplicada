"""Contratos estruturados Pydantic usados pela camada de LLM."""

from app.llm import Intent, IntentExtraction, MessageGeneration

__all__ = ["Intent", "IntentExtraction", "MessageGeneration"]
