from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app import app as app_module
from app.appointment import Appointment, AppointmentCatalog, Professional
from app.graph_factory import build_graph
from app.llm import FakeMedicalLLM, Intent, IntentExtraction, MessageGeneration
from app.app import app
from app.graph import create_medical_state

client = TestClient(app)


def test_schedule_response_is_structured() -> None:
    response = client.post("/chat", json={"question": "Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"})
    assert response.status_code == 200
    assert response.json()["intent"] == "schedule"
    assert response.json()["success"] is True


def test_unknown_guidance_is_structured() -> None:
    response = client.post("/chat", json={"question": "Olá, preciso de ajuda médica"})
    assert response.status_code == 200
    assert response.json()["intent"] == "unknown"
    assert response.json()["success"] is False


def test_cancel_not_found_is_structured() -> None:
    response = client.post("/chat", json={"question": "Sou Maria Santos e quero cancelar uma consulta com Dr. Alicio da Silva amanhã às 16h"})
    assert response.status_code == 200
    assert response.json()["intent"] == "cancel"
    assert response.json()["success"] is False
    assert "não encontrada" in response.json()["error"]


def test_short_question_is_rejected_before_graph() -> None:
    response = client.post("/chat", json={"question": "curta"})
    assert response.status_code == 422


def test_schedule_without_datetime_returns_structured_business_error() -> None:
    response = client.post("/chat", json={"question": "Quero agendar uma consulta"})

    assert response.status_code == 200
    assert response.json()["intent"] == "schedule"
    assert response.json()["success"] is False
    assert "data" in response.json()["error"]


def test_cancel_existing_appointment_returns_success(monkeypatch) -> None:
    when = datetime(2026, 9, 4, 16, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        appointments=[Appointment(1, "Dr. Alicio da Silva", "Maria Santos", when, "check-up")],
    )
    fake = FakeMedicalLLM(
        extraction=IntentExtraction(intent=Intent.CANCEL, professional_id=1, professional_name="Dr. Alicio da Silva", patient_name="Maria Santos", datetime=when),
        generated=MessageGeneration(message="Cancelamento confirmado."),
    )
    monkeypatch.setattr(app_module, "graph", build_graph(fake))
    monkeypatch.setattr(app_module, "create_medical_state", lambda question: create_medical_state(question, catalog))

    response = client.post("/chat", json={"question": "Quero cancelar minha consulta"})

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_schedule_occupied_slot_returns_error_without_duplicate(monkeypatch) -> None:
    now = datetime(2026, 9, 3, 9, tzinfo=timezone.utc)
    when = datetime(2026, 9, 4, 16, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        appointments=[Appointment(1, "Dr. Alicio da Silva", "Outra Pessoa", when, "check-up")],
        now=lambda: now,
    )
    fake = FakeMedicalLLM(
        extraction=IntentExtraction(intent=Intent.SCHEDULE, professional_id=1, professional_name="Dr. Alicio da Silva", patient_name="Maria Santos", datetime=when, reason="consulta"),
        generated=MessageGeneration(message="Horário indisponível."),
    )
    monkeypatch.setattr(app_module, "graph", build_graph(fake))
    monkeypatch.setattr(app_module, "create_medical_state", lambda question: create_medical_state(question, catalog))

    response = client.post("/chat", json={"question": "Quero agendar uma consulta"})

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert "indisponível" in response.json()["error"]
    assert len(catalog.appointments) == 1
