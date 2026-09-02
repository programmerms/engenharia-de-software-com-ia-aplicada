"""Optional boundary for LLM and structured-output concepts."""
from dataclasses import dataclass, field
from typing import Protocol
from pydantic import BaseModel, Field

class IntentExtraction(BaseModel):
    intent: str = Field(description="schedule, cancel or unknown")
    patient_name: str | None = None
    professional_name: str | None = None
    datetime_text: str | None = None
    reason: str | None = None

class MessageGeneration(BaseModel):
    message: str = Field(min_length=1)

class MedicalLLM(Protocol):
    def extract(self, text: str) -> IntentExtraction: ...
    def message(self, scenario: str, details: dict) -> MessageGeneration: ...

@dataclass
class FakeMedicalLLM:
    extraction: IntentExtraction
    generated: MessageGeneration = field(default_factory=lambda: MessageGeneration(message="Resposta simulada"))

    def extract(self, text: str) -> IntentExtraction:
        return self.extraction

    def message(self, scenario: str, details: dict) -> MessageGeneration:
        return self.generated
