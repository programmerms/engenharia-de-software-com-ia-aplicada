"""Adaptador HTTP do fluxo médico.

Este módulo representa a borda da aplicação: valida a entrada, invoca o grafo
compilado e transforma seu estado interno em um contrato HTTP estável.
"""
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graph.graph import create_medical_state, graph

logger = logging.getLogger(__name__)
app = FastAPI(title="Medical Appointment Intent Flow")


class ChatRequest(BaseModel):
    """Entrada pública do endpoint de conversa médica."""

    question: str = Field(min_length=10)


class MedicalResponse(BaseModel):
    """Resposta pública sem histórico interno ou detalhes do provider."""

    intent: str
    success: bool
    message: str
    appointment: dict | None = None
    error: str | None = None


@app.post("/chat", response_model=MedicalResponse)
def chat(request: ChatRequest) -> dict:
    """Executa o grafo e normaliza sucesso, consulta e erros para HTTP."""

    try:
        result = graph.invoke(create_medical_state(request.question))
        response = {
            "intent": result.get("intent", "unknown"),
            "success": result.get("action_success", False),
            "message": result.get("output", ""),
        }
        if result.get("appointment_data"):
            response["appointment"] = result["appointment_data"]
        if result.get("action_error") or result.get("error"):
            response["error"] = result.get("action_error") or result.get("error")
        return response
    except Exception as exc:
        logger.exception("Unexpected error while processing /chat: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


def run() -> None:
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000)
