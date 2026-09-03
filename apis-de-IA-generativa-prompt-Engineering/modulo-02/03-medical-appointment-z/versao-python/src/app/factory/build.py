"""Composition Root do template Python."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.domain.services.appointment_service import AppointmentCatalog, default_catalog
from app.config import config
from app.graph.nodes.canceller import create_cancel_node
from app.graph.nodes.identify_intent import create_identify_intent_node
from app.graph.nodes.message import create_message_node
from app.graph.nodes.scheduler import create_schedule_node
from app.graph.router import route_medical
from app.graph.state import GraphState
from app.llm.service import MedicalLLM, OfflineMedicalLLM, OpenRouterMedicalLLM


def build_graph(llm: MedicalLLM | None = None, catalog: AppointmentCatalog | None = None):
    """Cria o grafo e injeta suas dependências no Composition Root."""

    llm_client = llm or (OpenRouterMedicalLLM(config) if config.api_key else OfflineMedicalLLM())
    catalog_client = catalog or default_catalog()
    workflow = StateGraph(GraphState)
    workflow.add_node("identify_intent", create_identify_intent_node(llm_client, catalog_client))
    workflow.add_node("schedule", create_schedule_node(catalog_client))
    workflow.add_node("cancel", create_cancel_node(catalog_client))
    workflow.add_node("message", create_message_node(llm_client))
    workflow.add_edge(START, "identify_intent")
    workflow.add_conditional_edges("identify_intent", route_medical, {"schedule": "schedule", "cancel": "cancel", "message": "message"})
    workflow.add_edge("schedule", "message")
    workflow.add_edge("cancel", "message")
    workflow.add_edge("message", END)
    return workflow.compile()
