"""Composição e compilação do StateGraph médico."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.appointment_service import AppointmentCatalog
from app.config import config
from app.llm_service import MedicalLLM, OfflineMedicalLLM, OpenRouterMedicalLLM
from app.nodes.canceller import cancel_node
from app.nodes.identify_intent import create_identify_intent_node
from app.nodes.message import create_message_node
from app.nodes.scheduler import schedule_node


def build_graph(llm: MedicalLLM | None = None, catalog: AppointmentCatalog | None = None):
    """Monta e compila o grafo com dependências reais ou fornecidas pelo teste."""

    # Imports tardios evitam ciclo: graph.py publica o grafo e a factory importa
    # o contrato de estado somente quando começa a composição.
    from app.graph import GraphState
    from app.router import route_medical

    llm_client = llm or (OpenRouterMedicalLLM(config) if config.api_key else OfflineMedicalLLM())
    workflow = StateGraph(GraphState)
    # Cada node transforma uma parte do estado: identificação usa LLM,
    # scheduler/canceller usam apenas domínio e message produz a resposta.
    workflow.add_node("identify_intent", create_identify_intent_node(llm_client))
    workflow.add_node("schedule", schedule_node)
    workflow.add_node("cancel", cancel_node)
    workflow.add_node("message", create_message_node(llm_client))
    workflow.add_edge(START, "identify_intent")
    # O router lê a intenção já validada; ele nunca recebe um nome de node vindo
    # diretamente do modelo, mantendo o conjunto de caminhos fechado.
    workflow.add_conditional_edges("identify_intent", route_medical, {"schedule": "schedule", "cancel": "cancel", "message": "message"})
    workflow.add_edge("schedule", "message")
    workflow.add_edge("cancel", "message")
    workflow.add_edge("message", END)
    return workflow.compile()
