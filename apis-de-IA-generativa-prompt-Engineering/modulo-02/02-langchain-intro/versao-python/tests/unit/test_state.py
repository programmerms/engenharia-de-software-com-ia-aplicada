from langchain_core.messages import AIMessage, HumanMessage

from langchain_intro.graph import append_response, create_initial_state


def test_append_response_adds_ai_message_to_history() -> None:
    state = create_initial_state("hello")
    state["output"] = "HELLO"

    result = append_response(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "HELLO"


def test_each_initial_state_is_ephemeral() -> None:
    first = create_initial_state("first")
    second = create_initial_state("second")

    assert len(first["messages"]) == 1
    assert len(second["messages"]) == 1
    assert first["messages"][0].content == "first"
    assert second["messages"][0].content == "second"

