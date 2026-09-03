"""Node que gera a mensagem final a partir do resultado do fluxo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage

from app.llm.service import MedicalLLM

if TYPE_CHECKING:
    from app.state import GraphState

MEDICAL_GUIDANCE = "Posso ajudar a agendar ou cancelar consultas médicas."


def create_message_node(llm: MedicalLLM):
    """Cria o node de resposta, mantendo o cliente LLM injetável."""

    def message(state: GraphState) -> GraphState:
        """Gera resposta estruturada ou fallback sem apagar resultado de domínio."""

        intent = state.get("intent", "unknown")
        success = bool(state.get("action_success"))
        scenario = "unknown" if intent == "unknown" else f"{intent}_{'success' if success else 'error'}"
        details = {"professional_name": state.get("professional_name"), "datetime": state.get("datetime"), "patient_name": state.get("patient_name"), "appointment_data": state.get("appointment_data"), "action_error": state.get("action_error"), "error": state.get("error")}
        try:
            output = llm.generate_message(scenario, details).message
        except Exception:
            if scenario == "unknown":
                output = MEDICAL_GUIDANCE
            elif success:
                output = "Sua operação foi concluída, mas não foi possível gerar os detalhes da mensagem."
            else:
                output = "Não foi possível processar sua solicitação. Verifique os dados e tente novamente."
        return {"output": output, "messages": [AIMessage(content=output)], "visited": ["message"]}

    return message
