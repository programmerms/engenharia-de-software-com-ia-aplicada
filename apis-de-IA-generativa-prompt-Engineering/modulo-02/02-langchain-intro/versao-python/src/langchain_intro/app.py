"""Aplicação FastAPI que adapta HTTP ao grafo LangGraph.

FastAPI cuida do contrato HTTP e da validação do corpo. Depois da validação,
esta camada cria o estado inicial e faz o invoke do grafo; o consumidor recebe
somente output, não os detalhes internos do workflow.
"""

import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .graph import create_initial_state, graph

logger = logging.getLogger(__name__)
app = FastAPI(title="LangChain Intro Python")


class ChatRequest(BaseModel):
    """Modelo Pydantic do request; Field aplica o mínimo do contrato."""

    question: str = Field(min_length=5)


@app.post("/chat")
def chat(request: ChatRequest) -> str:
    """Executa o grafo para um request validado e retorna apenas o resultado."""
    try:
        result = graph.invoke(create_initial_state(request.question))
        return result["output"]
    except Exception:
        # O log auxilia o desenvolvedor local, enquanto a resposta pública não
        # expõe stack trace, detalhes internos ou credenciais.
        logger.exception("Unexpected error while processing /chat")
        raise HTTPException(status_code=500, detail="Internal server error")


def run() -> None:
    """Inicia o servidor Uvicorn no endereço local documentado."""
    uvicorn.run("langchain_intro.app:app", host="127.0.0.1", port=8000)
