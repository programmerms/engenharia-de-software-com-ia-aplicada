"""Estado e pontos de entrada do grafo de consultas médicas.

O grafo é montado na factory para permitir injeção de LLM e catálogo em testes.
Este módulo concentra o contrato do estado, a criação da entrada e o router;
assim o caminho conceitual do LangGraph fica visível para estudantes.
"""

from __future__ import annotations

import operator
import re
from datetime import datetime
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.appointment_service import AppointmentCatalog, default_catalog
from app.messages import human_message
from app.router import route_medical  # noqa: F401 - compatibilidade do contrato público

Intent = Literal["schedule", "cancel", "unknown"]
MEDICAL_GUIDANCE = "Posso ajudar a agendar ou cancelar consultas médicas."


class GraphState(TypedDict, total=False):
    """Estado efêmero que atravessa identificação, roteamento e domínio."""

    messages: Annotated[list[BaseMessage], add_messages]
    visited: Annotated[list[str], operator.add]
    output: str
    intent: Intent
    patient_name: str
    professional_id: int
    professional_name: str
    datetime: datetime
    reason: str
    action_success: bool
    action_error: str
    appointment_data: dict[str, object]
    error: str
    catalog: AppointmentCatalog


def create_medical_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    """Cria estado inicial com mensagem humana e catálogo isolado."""

    return {"messages": [human_message(question)], "output": question, "catalog": catalog or default_catalog(), "visited": []}


def create_initial_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    """Mantém o nome de entrada usado pelo template anterior."""

    return create_medical_state(question, catalog)


def classify_medical_intent(text: str) -> Intent:
    """Classifica texto localmente para compatibilidade com testes legados."""

    value = text.casefold()
    schedule = bool(re.search(r"\b(agendar|agende|marcar|marque)\b", value))
    cancel = bool(re.search(r"\b(cancelar|cancele|cancelamento)\b", value))
    if schedule == cancel:
        return "unknown"
    return "schedule" if schedule else "cancel"


def identify_intent(state: GraphState) -> GraphState:
    """Executa identificação offline para chamadas diretas legadas."""

    from app.llm_service import OfflineMedicalLLM
    from app.nodes.identify_intent import create_identify_intent_node

    return create_identify_intent_node(OfflineMedicalLLM())(state)


def medical_message_node(state: GraphState) -> GraphState:
    """Gera fallback local para chamadas unitárias do template anterior."""

    if state.get("intent") == "unknown":
        output = MEDICAL_GUIDANCE
    elif state.get("action_success"):
        output = "Sua consulta foi confirmada." if state.get("intent") == "schedule" else "Sua consulta foi cancelada com sucesso."
    else:
        output = f"Não foi possível processar sua solicitação: {state.get('action_error') or state.get('error') or 'dados incompletos'}."
    return {"output": output, "messages": [AIMessage(content=output)], "visited": ["message"]}


from app.graph_factory import build_graph  # noqa: E402 - inicialização tardia evita ciclo

graph = build_graph()
medical_graph = graph
