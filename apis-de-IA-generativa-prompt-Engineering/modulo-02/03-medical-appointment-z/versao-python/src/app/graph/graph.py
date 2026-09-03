"""Definição e publicação do grafo médico compilado."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage

from app.graph.state import GraphState
from app.messages import human_message

if TYPE_CHECKING:
    from app.appointment import AppointmentCatalog

MEDICAL_GUIDANCE = "Posso ajudar a agendar ou cancelar consultas médicas."


def create_medical_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    """Cria a entrada do grafo; ``catalog`` é aceito apenas por compatibilidade."""

    # O estado transporta dados. O catálogo é composto pela factory e não é
    # armazenado no workflow.
    return {"messages": [human_message(question)], "output": question, "visited": []}


def create_initial_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    """Mantém o nome de entrada histórico do template."""

    return create_medical_state(question, catalog)


def identify_intent(state: GraphState) -> GraphState:
    """Executa identificação offline para compatibilidade do template."""

    from app.domain.services.appointment_service import default_catalog
    from app.llm.service import OfflineMedicalLLM
    from app.nodes.identify_intent import create_identify_intent_node

    return create_identify_intent_node(OfflineMedicalLLM(), default_catalog())(state)


def classify_medical_intent(text: str) -> str:
    """Mantém classificação local somente para compatibilidade histórica."""

    value = text.casefold()
    schedule = bool(re.search(r"\b(agendar|agende|marcar|marque)\b", value))
    cancel = bool(re.search(r"\b(cancelar|cancele|cancelamento)\b", value))
    if schedule == cancel:
        return "unknown"
    return "schedule" if schedule else "cancel"


def medical_message_node(state: GraphState) -> GraphState:
    """Fornece o helper de mensagem do template anterior."""

    if state.get("intent") == "unknown":
        output = MEDICAL_GUIDANCE
    elif state.get("action_success"):
        output = "Sua consulta foi confirmada." if state.get("intent") == "schedule" else "Sua consulta foi cancelada com sucesso."
    else:
        output = f"Não foi possível processar sua solicitação: {state.get('action_error') or state.get('error') or 'dados incompletos'}."
    return {"output": output, "messages": [AIMessage(content=output)], "visited": ["message"]}


from app.factory.build import build_graph  # noqa: E402

graph = build_graph()
medical_graph = graph

__all__ = ["GraphState", "classify_medical_intent", "create_initial_state", "create_medical_state", "graph", "medical_graph", "medical_message_node"]
