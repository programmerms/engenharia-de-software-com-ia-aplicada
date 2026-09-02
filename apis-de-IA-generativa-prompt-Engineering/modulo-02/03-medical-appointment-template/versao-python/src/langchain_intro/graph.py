"""Fluxo LangGraph do domínio de consultas médicas."""
from __future__ import annotations

import operator
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from langchain_intro.appointment import AppointmentCatalog, default_catalog
from langchain_intro.messages import human_message

Intent = Literal["schedule", "cancel", "unknown"]
MEDICAL_GUIDANCE = "Posso ajudar a agendar ou cancelar consultas médicas."


class GraphState(TypedDict, total=False):
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
    appointment_data: dict
    error: str
    catalog: AppointmentCatalog


def create_medical_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    return {"messages": [human_message(question)], "output": question, "catalog": catalog or default_catalog(), "visited": []}


def create_initial_state(question: str, catalog: AppointmentCatalog | None = None) -> GraphState:
    return create_medical_state(question, catalog)


def classify_medical_intent(text: str) -> Intent:
    value = text.casefold()
    schedule = bool(re.search(r"\b(agendar|agende|marcar|marque)\b", value))
    cancel = bool(re.search(r"\b(cancelar|cancele|cancelamento)\b", value))
    if schedule == cancel:
        return "unknown"
    return "schedule" if schedule else "cancel"


def _when(text: str, now: datetime) -> datetime:
    value = text.casefold()
    match = re.search(r"(?:às|as)\s*(\d{1,2})(?::(\d{2}))?h?\b", value)
    if match:
        day = now.date() + timedelta(days=1 if "amanhã" in value or "amanha" in value else 0)
        return datetime(day.year, day.month, day.day, int(match.group(1)), int(match.group(2) or 0), tzinfo=timezone.utc)
    iso = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", value)
    if iso:
        day = datetime.strptime(iso.group(1), "%Y-%m-%d").date()
        return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    raise ValueError("Informe a data e o horário da consulta")


def _patient(text: str) -> str | None:
    match = re.search(r"(?:sou|me chamo|paciente(?: é| e)?)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){1,3}?)(?=\s+e\s+|\s*,|$)", text, re.IGNORECASE)
    return match.group(1).strip(" .,;:") if match else None


def identify_intent(state: GraphState) -> GraphState:
    text = str(state["messages"][-1].content)
    intent = classify_medical_intent(text)
    result: GraphState = {"intent": intent, "visited": ["identify_intent"]}
    if intent == "unknown":
        result["action_success"] = False
    person = next((item for item in state["catalog"].professionals if item.name.casefold() in text.casefold()), None)
    if person:
        result.update({"professional_id": person.id, "professional_name": person.name})
    patient = _patient(text)
    if patient:
        result["patient_name"] = patient
    if result["intent"] in ("schedule", "cancel"):
        try:
            result["datetime"] = _when(text, state["catalog"].now())
        except ValueError as exc:
            result["error"] = str(exc)
    if result["intent"] == "schedule":
        value = text.casefold()
        result["reason"] = value.split(" para ", 1)[-1].strip() if " para " in value else "consulta"
    return result


def route_medical(state: GraphState) -> str:
    return "message" if state.get("error") or state.get("intent") == "unknown" else state["intent"]


def _data(item) -> dict:
    return {"professional_id": item.professional_id, "professional_name": item.professional_name, "patient_name": item.patient_name, "datetime": item.datetime.isoformat(), "reason": item.reason}


def schedule_node(state: GraphState) -> GraphState:
    try:
        if not all(state.get(key) for key in ("patient_name", "professional_id", "datetime", "reason")):
            raise ValueError("Informe nome, profissional, data, horário e motivo")
        item = state["catalog"].book(state["professional_id"], state["datetime"], state["patient_name"], state["reason"])
        return {"action_success": True, "appointment_data": _data(item), "visited": ["schedule"]}
    except ValueError as exc:
        return {"action_success": False, "action_error": str(exc), "visited": ["schedule"]}


def cancel_node(state: GraphState) -> GraphState:
    try:
        if not all(state.get(key) for key in ("patient_name", "professional_id", "datetime")):
            raise ValueError("Informe nome, profissional, data e horário")
        item = state["catalog"].cancel(state["professional_id"], state["datetime"], state["patient_name"])
        return {"action_success": True, "appointment_data": _data(item), "visited": ["cancel"]}
    except ValueError as exc:
        return {"action_success": False, "action_error": str(exc), "visited": ["cancel"]}


def medical_message_node(state: GraphState) -> GraphState:
    if state.get("intent") == "unknown":
        output = MEDICAL_GUIDANCE
    elif state.get("action_success"):
        output = "Sua consulta foi confirmada." if state["intent"] == "schedule" else "Sua consulta foi cancelada com sucesso."
    else:
        output = f"Não foi possível processar sua solicitação: {state.get('action_error') or state.get('error') or 'dados incompletos'}."
    return {"output": output, "messages": [AIMessage(content=output)], "visited": ["message"]}


def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("identify_intent", identify_intent)
    workflow.add_node("schedule", schedule_node)
    workflow.add_node("cancel", cancel_node)
    workflow.add_node("message", medical_message_node)
    workflow.add_edge(START, "identify_intent")
    workflow.add_conditional_edges("identify_intent", route_medical, {"schedule": "schedule", "cancel": "cancel", "message": "message"})
    workflow.add_edge("schedule", "message")
    workflow.add_edge("cancel", "message")
    workflow.add_edge("message", END)
    return workflow.compile()


graph = build_graph()
medical_graph = graph
