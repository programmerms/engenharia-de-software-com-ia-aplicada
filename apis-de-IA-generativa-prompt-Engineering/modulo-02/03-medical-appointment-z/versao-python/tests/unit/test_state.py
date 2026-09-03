from langchain_core.messages import AIMessage
from app.graph import create_medical_state, medical_message_node


def test_unknown_response_adds_ai_message() -> None:
    state = create_medical_state("Olá, preciso de ajuda")
    state["intent"] = "unknown"
    result = medical_message_node(state)
    assert isinstance(result["messages"][0], AIMessage)
    assert "agendar" in result["output"]


def test_each_medical_state_is_ephemeral() -> None:
    first = create_medical_state("primeira mensagem")
    second = create_medical_state("segunda mensagem")
    assert first["messages"][0].content == "primeira mensagem"
    assert second["messages"][0].content == "segunda mensagem"
    assert first["catalog"] is not second["catalog"]
