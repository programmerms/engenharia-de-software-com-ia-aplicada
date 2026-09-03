"""Node que delega cancelamento ao serviço de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.nodes.scheduler import appointment_data

if TYPE_CHECKING:
    from app.graph import GraphState


def cancel_node(state: GraphState) -> GraphState:
    """Valida identificação da consulta e solicita remoção ao catálogo."""

    try:
        if not all(state.get(key) is not None for key in ("patient_name", "professional_id", "datetime")):
            raise ValueError("Informe nome, profissional, data e horário")
        item = state["catalog"].cancel(state["professional_id"], state["datetime"], state["patient_name"])
        return {"action_success": True, "appointment_data": appointment_data(item), "visited": ["cancel"]}
    except ValueError as exc:
        return {"action_success": False, "action_error": str(exc), "visited": ["cancel"]}
