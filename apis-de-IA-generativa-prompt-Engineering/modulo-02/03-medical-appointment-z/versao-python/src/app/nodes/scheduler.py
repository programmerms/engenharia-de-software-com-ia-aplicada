"""Node que delega agendamento ao serviço de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.graph import GraphState


def appointment_data(item) -> dict[str, object]:
    """Converte entidade de domínio em dados seguros para estado e API."""

    return {"professional_id": item.professional_id, "professional_name": item.professional_name, "patient_name": item.patient_name, "datetime": item.datetime.isoformat(), "reason": item.reason}


def schedule_node(state: GraphState) -> GraphState:
    """Valida dados estruturados e solicita criação ao catálogo em memória.

    ``professional_id``, ``datetime`` e ``patient_name`` são obrigatórios para
    executar o domínio. O motivo é opcional no contrato da aula e recebe um
    valor didático padrão antes da chamada, sem delegar essa decisão ao LLM.
    """

    try:
        required = ("professional_id", "datetime", "patient_name")
        missing = [key for key in required if state.get(key) is None or state.get(key) == ""]
        if missing:
            labels = {"professional_id": "professionalId", "datetime": "datetime", "patient_name": "patientName"}
            raise ValueError("Campos ausentes: " + ", ".join(labels[key] for key in missing))
        reason = str(state.get("reason") or "consulta")
        item = state["catalog"].book(state["professional_id"], state["datetime"], state["patient_name"], reason)
        return {"action_success": True, "appointment_data": appointment_data(item), "visited": ["schedule"]}
    except ValueError as exc:
        return {"action_success": False, "action_error": str(exc), "visited": ["schedule"]}
