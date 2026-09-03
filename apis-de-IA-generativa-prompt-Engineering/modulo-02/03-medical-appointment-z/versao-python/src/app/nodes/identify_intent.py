"""Node responsável por interpretar a mensagem e atualizar o GraphState."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.llm_service import Intent, MedicalLLM

if TYPE_CHECKING:
    from app.state import GraphState


def create_identify_intent_node(llm: MedicalLLM):
    """Cria o node que usa LLM estruturado sem executar regras de domínio."""

    def identify(state: GraphState) -> GraphState:
        """Extrai intenção/dados e devolve uma atualização parcial do estado."""

        question = str(state["messages"][-1].content)
        catalog = state["catalog"]
        professionals = [{"id": item.id, "name": item.name, "specialty": item.specialty} for item in catalog.professionals]
        try:
            extraction = llm.extract_intent(question, professionals, catalog.now())
            intent = extraction.normalized_intent()
            result: GraphState = {"intent": intent, "visited": ["identify_intent"]}
            if intent == Intent.UNKNOWN.value:
                result["action_success"] = False
            for key in ("professional_id", "professional_name", "patient_name", "datetime", "reason"):
                value = getattr(extraction, key)
                if value is not None:
                    result[key] = value
            if intent in {Intent.SCHEDULE.value, Intent.CANCEL.value} and not extraction.datetime:
                result["error"] = "Informe a data e o horário da consulta"
            return result
        except Exception as exc:
            return {"intent": Intent.UNKNOWN.value, "action_success": False, "error": f"Falha de interpretação do LLM: {exc}", "visited": ["identify_intent"]}

    return identify
