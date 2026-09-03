from app.graph import create_medical_state
from app.llm import FakeMedicalLLM, Intent, IntentExtraction, MessageGeneration
from app.nodes.message import create_message_node


def test_message_node_generates_structured_unknown_response() -> None:
    llm = FakeMedicalLLM(
        extraction=IntentExtraction(intent=Intent.UNKNOWN),
        generated=MessageGeneration(message="Posso ajudar com consultas."),
    )
    state = create_medical_state("Olá")
    state["intent"] = Intent.UNKNOWN.value

    result = create_message_node(llm)(state)

    assert result["output"] == "Posso ajudar com consultas."
    assert result["messages"][-1].content == "Posso ajudar com consultas."


def test_message_node_has_non_empty_fallback_when_provider_fails() -> None:
    class BrokenLLM(FakeMedicalLLM):
        def generate_message(self, scenario, details):
            raise RuntimeError("provider unavailable")

    state = create_medical_state("Olá")
    state["intent"] = Intent.UNKNOWN.value

    result = create_message_node(BrokenLLM(extraction=IntentExtraction(intent=Intent.UNKNOWN)))(state)

    assert result["output"]
    assert "agendar" in result["output"]
