from langchain_intro.app import ChatRequest, chat
from langchain_intro.graph import FALLBACK_MESSAGE


def test_fastapi_chat_works_without_langgraph_dev_process() -> None:
    assert chat(ChatRequest(question="make this UPPER")) == "MAKE THIS UPPER"
    assert chat(ChatRequest(question="make this lower")) == "make this lower"
    assert chat(ChatRequest(question="hello there")) == FALLBACK_MESSAGE
