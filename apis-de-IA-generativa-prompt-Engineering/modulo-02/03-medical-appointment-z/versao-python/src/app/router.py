"""Router canônico das conditional edges do fluxo médico."""

def route_medical(state: dict[str, object]) -> str:
    """Escolhe um destino fechado a partir da intenção já estruturada.

    Erros e intenções desconhecidas seguem para ``message``. O router não
    interpreta texto nem aceita nomes de nodes fornecidos diretamente pelo LLM.
    """

    if state.get("error") or state.get("intent") == "unknown":
        return "message"
    return state.get("intent", "unknown") if state.get("intent") in {"schedule", "cancel"} else "message"

__all__ = ["route_medical"]
