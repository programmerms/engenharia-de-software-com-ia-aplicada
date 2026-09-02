from langchain_core.messages import HumanMessage

from langchain_intro.graph import (
    FALLBACK_MESSAGE,
    create_initial_state,
    identify_intent,
)


def test_identifies_uppercase_case_insensitively() -> None:
    state = create_initial_state("make this UPPER please")

    result = identify_intent(state)

    assert result["command"] == "uppercase"
    assert result["output"] == "make this UPPER please"


def test_uppercase_has_precedence_over_lowercase() -> None:
    state = create_initial_state("upper and lower")

    result = identify_intent(state)

    assert result["command"] == "uppercase"


def test_identifies_unknown_command() -> None:
    state = create_initial_state("hello there")

    result = identify_intent(state)

    assert result["command"] == "unknown"
    assert result["output"] == "hello there"
    assert FALLBACK_MESSAGE.startswith("Unknown command.")


def test_initial_state_contains_human_message() -> None:
    state = create_initial_state("hello")

    assert len(state["messages"]) == 1
    assert isinstance(state["messages"][0], HumanMessage)
    assert state["output"] == "hello"

