"""Orquestração LangGraph do atendimento médico.

Os símbolos do grafo compilado são carregados sob demanda para evitar um
ciclo entre o módulo publicado e a Composition Root durante os imports.
"""

from app.graph.router import route_medical
from app.graph.state import GraphState

_GRAPH_EXPORTS = {
    "classify_medical_intent",
    "create_initial_state",
    "create_medical_state",
    "graph",
    "identify_intent",
    "medical_graph",
    "medical_message_node",
}


def __getattr__(name: str):
    """Resolve helpers do grafo somente quando solicitados."""

    if name in _GRAPH_EXPORTS:
        from importlib import import_module

        graph_module = import_module("app.graph.graph")
        return getattr(graph_module, name)
    raise AttributeError(name)


__all__ = ["GraphState", "route_medical", *_GRAPH_EXPORTS]
