"""Schemas, protocolo, fake e serviço LangChain/OpenRouter.

O módulo representa a camada de integração com modelos. Nodes dependem do
protocolo, e não da implementação concreta, para que o fluxo possa ser testado
sem internet. O serviço real usa Structured Output para transformar respostas
do modelo em objetos Pydantic antes de entregá-las ao LangGraph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime as DateTime
from enum import Enum
import re
from datetime import timedelta, timezone
from typing import Protocol

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.config import LLMConfig, config


class Intent(str, Enum):
    """Tipo compatível com o contrato de intenções controladas."""

    SCHEDULE = "schedule"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


class IntentExtraction(BaseModel):
    """Saída estruturada usada para decidir o caminho do grafo."""

    model_config = ConfigDict(extra="forbid")

    intent: Intent = Field(description="Uma destas opções: schedule, cancel ou unknown")
    professional_id: int | None = Field(default=None, ge=1)
    professional_name: str | None = None
    patient_name: str | None = None
    datetime: DateTime | None = None
    reason: str | None = None

    def normalized_intent(self) -> str:
        """Retorna a intenção permitida ou ``unknown`` para valores inválidos."""

        return self.intent.value if self.intent in {Intent.SCHEDULE, Intent.CANCEL, Intent.UNKNOWN} else Intent.UNKNOWN.value


class MessageGeneration(BaseModel):
    """Saída estruturada da resposta final apresentada ao usuário."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)


class LLMError(RuntimeError):
    """Erro seguro de transporte, configuração ou parsing do LLM."""


class MedicalLLM(Protocol):
    """Contrato mínimo que os nodes precisam do serviço de linguagem."""

    def extract_intent(self, question: str, professionals: list[dict[str, object]], now: DateTime) -> IntentExtraction: ...

    def generate_message(self, scenario: str, details: dict[str, object]) -> MessageGeneration: ...


class OpenRouterMedicalLLM:
    """Serviço real que conecta LangChain ao endpoint OpenRouter.

    O modelo é criado sob demanda para manter importações e testes offline sem
    exigir API key. Cada operação aplica Structured Output com um schema
    Pydantic, evitando que texto livre seja consumido pelo domínio ou router.
    """

    def __init__(self, settings: LLMConfig = config) -> None:
        """Armazena a configuração sem realizar chamada de rede."""

        self.settings = settings
        self._model: ChatOpenAI | None = None

    def _chat_model(self) -> ChatOpenAI:
        """Cria o ChatOpenAI apontado para OpenRouter na primeira chamada real."""

        if self._model is None:
            headers = {
                key: value
                for key, value in {
                    "HTTP-Referer": self.settings.http_referer,
                    "X-Title": self.settings.x_title,
                }.items()
                if value
            }
            model_options: dict[str, object] = {
                "api_key": self.settings.require_api_key(),
                "model": self.settings.model,
                "base_url": self.settings.base_url,
                "temperature": self.settings.temperature,
                "timeout": self.settings.timeout,
                "max_retries": 0,
                "default_headers": headers,
            }
            if self.settings.provider:
                model_options["model_kwargs"] = {"provider": self.settings.provider}
            self._model = ChatOpenAI(**model_options)
        return self._model

    def extract_intent(self, question: str, professionals: list[dict[str, object]], now: DateTime) -> IntentExtraction:
        """Extrai intenção e dados de consulta usando Structured Output.

        Erros do provider ou de parsing são convertidos em ``LLMError`` para que
        o node possa seguir pelo caminho seguro de mensagem.
        """

        from app.prompts.v1.identify_intent import build_identify_intent_prompt

        try:
            structured = self._chat_model().with_structured_output(IntentExtraction, include_raw=True)
            result = structured.invoke(build_identify_intent_prompt(question, professionals, now))
            parsed = result.get("parsed") if isinstance(result, dict) else result
            if not isinstance(parsed, IntentExtraction):
                raise LLMError("LLM returned an invalid structured intent")
            return parsed
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("Falha ao interpretar a solicitação com o LLM") from exc

    def generate_message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """Gera mensagem natural estruturada para o cenário informado."""

        from app.prompts.v1.message import build_message_prompt

        try:
            structured = self._chat_model().with_structured_output(MessageGeneration, include_raw=True)
            result = structured.invoke(build_message_prompt(scenario, details))
            parsed = result.get("parsed") if isinstance(result, dict) else result
            if not isinstance(parsed, MessageGeneration):
                raise LLMError("LLM returned an invalid structured message")
            return parsed
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("Falha ao gerar a mensagem final com o LLM") from exc

    def extract(self, text: str) -> IntentExtraction:
        """Mantém uma API curta de compatibilidade para demonstrações/testes."""

        return self.extract_intent(text, [], DateTime.now())

    def message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """Alias didático para a operação de geração de mensagem."""

        return self.generate_message(scenario, details)


@dataclass
class FakeMedicalLLM:
    """Double determinístico da fronteira LLM usado na suíte sem rede."""

    extraction: IntentExtraction
    generated: MessageGeneration = field(default_factory=lambda: MessageGeneration(message="Resposta simulada"))

    def extract_intent(self, question: str, professionals: list[dict[str, object]], now: DateTime) -> IntentExtraction:
        """Retorna a extração preparada no teste, ignorando transporte externo."""

        return self.extraction

    def generate_message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """Retorna a mensagem preparada no teste."""

        return self.generated

    def extract(self, text: str) -> IntentExtraction:
        """API curta preservada para os testes da etapa anterior."""

        return self.extraction

    def message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """API curta preservada para os testes da etapa anterior."""

        return self.generated


@dataclass
class OfflineMedicalLLM:
    """Fallback local determinístico para desenvolvimento sem credenciais.

    Ele não substitui a integração real: mantém API e CLI demonstráveis offline,
    usando o mesmo protocolo que o provider OpenRouter.
    """

    def extract_intent(self, question: str, professionals: list[dict[str, object]], now: DateTime) -> IntentExtraction:
        """Interpreta padrões didáticos locais sem rede ou API key."""

        value = question.casefold()
        wants_schedule = bool(re.search(r"\b(agendar|agende|marcar|marque)\b", value))
        wants_cancel = bool(re.search(r"\b(cancelar|cancele|cancelamento)\b", value))
        if wants_schedule == wants_cancel:
            return IntentExtraction(intent=Intent.UNKNOWN)
        professional = next((item for item in professionals if str(item.get("name", "")).casefold() in value), None)
        patient_match = re.search(
            r"(?:sou|me chamo|paciente(?: é| e)?)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){1,3}?)(?=\s+e\s+|\s*,|$)",
            question,
            re.IGNORECASE,
        )
        time_match = re.search(r"(?:às|as)\s*(\d{1,2})(?::(\d{2}))?h?\b", value)
        parsed_datetime = None
        if time_match:
            day = now.date() + timedelta(days=1 if "amanhã" in value or "amanha" in value else 0)
            parsed_datetime = DateTime(day.year, day.month, day.day, int(time_match.group(1)), int(time_match.group(2) or 0), tzinfo=timezone.utc)
        reason = question.split(" para ", 1)[1].strip() if " para " in value and wants_schedule else None
        return IntentExtraction(
            intent=Intent.SCHEDULE if wants_schedule else Intent.CANCEL,
            professional_id=int(professional["id"]) if professional else None,
            professional_name=str(professional["name"]) if professional else None,
            patient_name=patient_match.group(1).strip(" .,;:") if patient_match else None,
            datetime=parsed_datetime,
            reason=reason or ("consulta" if wants_schedule else None),
        )

    def generate_message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """Gera uma mensagem local para manter o fluxo utilizável offline."""

        if scenario == "unknown":
            text = "Posso ajudar a agendar ou cancelar consultas médicas."
        elif scenario == "schedule_success":
            text = "Sua consulta foi confirmada."
        elif scenario == "cancel_success":
            text = "Sua consulta foi cancelada com sucesso."
        else:
            error = details.get("action_error") or details.get("error") or "dados incompletos"
            text = f"Não foi possível processar sua solicitação: {error}."
        return MessageGeneration(message=text)

    def extract(self, text: str) -> IntentExtraction:
        """Expõe a API curta de compatibilidade do fake legado."""

        return self.extract_intent(text, [], DateTime.now(timezone.utc))

    def message(self, scenario: str, details: dict[str, object]) -> MessageGeneration:
        """Expõe a API curta de geração para compatibilidade didática."""

        return self.generate_message(scenario, details)
