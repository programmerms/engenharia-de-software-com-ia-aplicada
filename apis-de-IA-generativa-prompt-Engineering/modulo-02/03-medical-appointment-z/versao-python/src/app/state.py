"""Contrato canônico do estado transportado pelo LangGraph.

O módulo oferece o nome didático `state.py` sem duplicar o GraphState já usado
pelos pontos de entrada legados do template.
"""

from app.graph import GraphState, create_initial_state, create_medical_state

__all__ = ["GraphState", "create_initial_state", "create_medical_state"]
