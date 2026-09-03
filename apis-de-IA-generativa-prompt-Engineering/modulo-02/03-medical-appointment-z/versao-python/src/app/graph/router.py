"""Decisão de conditional edges baseada apenas em dados estruturados."""

from app.graph.state import GraphState


def route_medical(state: GraphState) -> str:
    """Retorna somente ``schedule``, ``cancel`` ou ``message``."""

    if state.get("error") or state.get("intent") == "unknown":
        return "message"
    return state.get("intent", "unknown") if state.get("intent") in {"schedule", "cancel"} else "message"

