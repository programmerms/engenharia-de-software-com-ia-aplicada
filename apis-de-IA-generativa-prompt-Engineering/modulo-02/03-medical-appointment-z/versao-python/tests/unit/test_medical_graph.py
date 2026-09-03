from datetime import datetime, timezone

from app.appointment import AppointmentCatalog, Professional
from app.graph import create_medical_state
from app.graph_factory import build_graph


def catalog() -> AppointmentCatalog:
    now = datetime(2026, 9, 1, 9, tzinfo=timezone.utc)
    return AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        now=lambda: now,
    )


def test_schedule_routes_and_updates_state() -> None:
    result = build_graph(catalog=catalog()).invoke(create_medical_state("Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"))
    assert result["intent"] == "schedule"
    assert result["action_success"] is True
    assert result["visited"] == ["identify_intent", "schedule", "message"]
    assert result["appointment_data"]["patient_name"] == "Maria Santos"


def test_unknown_routes_directly_to_message() -> None:
    result = build_graph(catalog=catalog()).invoke(create_medical_state("Olá, preciso de ajuda médica"))
    assert result["intent"] == "unknown"
    assert result["visited"] == ["identify_intent", "message"]
    assert result["action_success"] is False


def test_cancel_routes_and_extracts_patient_and_professional() -> None:
    result = build_graph(catalog=catalog()).invoke(create_medical_state("Sou Maria Santos e quero cancelar uma consulta com Dr. Alicio da Silva amanhã às 16h"))
    assert result["intent"] == "cancel"
    assert result["professional_id"] == 1
    assert result["patient_name"] == "Maria Santos"
    assert result["visited"] == ["identify_intent", "cancel", "message"]
