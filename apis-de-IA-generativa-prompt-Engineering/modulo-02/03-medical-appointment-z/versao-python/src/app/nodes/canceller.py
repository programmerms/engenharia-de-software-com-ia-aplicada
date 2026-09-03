"""Node que delega cancelamento ao serviço de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.nodes.scheduler import appointment_data

if TYPE_CHECKING:
    from app.graph import GraphState


def create_cancel_node(catalog):
    """Cria o node com o serviço de domínio explicitamente injetado."""

    def cancel(state: GraphState) -> GraphState:
        """Executa a operação de cancelamento no serviço recebido."""

        return _cancel(state, catalog)

    return cancel


def _cancel(state: GraphState, catalog) -> GraphState:
    """Valida identificação da consulta e solicita remoção ao catálogo."""

    try:
        if not all(state.get(key) is not None for key in ("patient_name", "professional_id", "datetime")):
            raise ValueError("Informe nome, profissional, data e horário")
        item = catalog.cancel(state["professional_id"], state["datetime"], state["patient_name"])
        return {"action_success": True, "appointment_data": appointment_data(item), "visited": ["cancel"]}
    except ValueError as exc:
        return {"action_success": False, "action_error": str(exc), "visited": ["cancel"]}


def cancel_node(state: GraphState) -> GraphState:
    """Mantém compatibilidade para chamadas antigas com catálogo no estado."""

    from app.domain.services.appointment_service import default_catalog

    return _cancel(state, state.get("catalog") or default_catalog())
