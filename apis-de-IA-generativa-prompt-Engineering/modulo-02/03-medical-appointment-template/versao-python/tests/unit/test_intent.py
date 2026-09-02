from langchain_core.messages import HumanMessage
from langchain_intro.graph import create_medical_state, identify_intent


def test_initial_medical_state_contains_human_message() -> None:
    state = create_medical_state("Quero agendar uma consulta")
    assert isinstance(state["messages"][0], HumanMessage)
    assert state["output"] == "Quero agendar uma consulta"


def test_identifies_schedule_and_patient() -> None:
    result = identify_intent(create_medical_state("Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"))
    assert result["intent"] == "schedule"
    assert result["patient_name"] == "Maria Santos"
    assert result["professional_id"] == 1
    assert result["datetime"].hour == 16


def test_identifies_unknown_conflicting_intent() -> None:
    result = identify_intent(create_medical_state("Quero agendar e cancelar uma consulta"))
    assert result["intent"] == "unknown"
