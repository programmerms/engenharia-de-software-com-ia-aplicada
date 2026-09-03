"""Dados transportados pelo workflow LangGraph, sem comportamento de negócio."""

from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

Intent = Literal["schedule", "cancel", "unknown"]


class GraphState(TypedDict, total=False):
    """Estado efêmero da conversa; serviços e dependências ficam fora dele."""

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

