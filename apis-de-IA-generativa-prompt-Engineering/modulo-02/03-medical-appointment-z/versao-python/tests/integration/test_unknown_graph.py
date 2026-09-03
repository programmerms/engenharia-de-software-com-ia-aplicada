from app.appointment import AppointmentCatalog, Professional
from app.graph import create_medical_state
from app.graph_factory import build_graph
from app.llm import FakeMedicalLLM, Intent, IntentExtraction, MessageGeneration


def test_unknown_graph_does_not_call_domain_action() -> None:
    catalog = AppointmentCatalog(professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")])
    llm = FakeMedicalLLM(
        extraction=IntentExtraction(intent=Intent.UNKNOWN),
        generated=MessageGeneration(message="Posso ajudar com consultas."),
    )

    result = build_graph(llm).invoke(create_medical_state("Qual é a previsão do tempo?", catalog))

    assert result["intent"] == Intent.UNKNOWN.value
    assert result["visited"] == ["identify_intent", "message"]
    assert result["action_success"] is False
    assert catalog.appointments == []
