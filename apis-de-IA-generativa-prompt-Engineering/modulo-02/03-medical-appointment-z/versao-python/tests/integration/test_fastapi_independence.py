from app.app import ChatRequest, chat


def test_fastapi_chat_works_without_langgraph_dev_process() -> None:
    result = chat(ChatRequest(question="Olá, preciso de ajuda médica"))
    assert result["intent"] == "unknown"
    assert result["success"] is False
