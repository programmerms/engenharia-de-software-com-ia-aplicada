from datetime import datetime, timezone

from app.appointment import Appointment, AppointmentCatalog, Professional
from app.graph import create_medical_state
from app.nodes.canceller import create_cancel_node


def test_canceller_removes_matching_appointment() -> None:
    when = datetime(2026, 9, 4, 16, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        appointments=[Appointment(1, "Dr. Alicio da Silva", "Maria Santos", when, "check-up")],
    )
    state = create_medical_state("cancelar")
    state.update({"patient_name": "Maria Santos", "professional_id": 1, "datetime": when})

    result = create_cancel_node(catalog)(state)

    assert result["action_success"] is True
    assert catalog.find(1, when, "Maria Santos") is None


def test_canceller_reports_missing_appointment_without_mutation() -> None:
    when = datetime(2026, 9, 4, 16, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")])
    state = create_medical_state("cancelar")
    state.update({"patient_name": "Maria Santos", "professional_id": 1, "datetime": when})

    result = create_cancel_node(catalog)(state)

    assert result["action_success"] is False
    assert "não encontrada" in result["action_error"]
    assert catalog.appointments == []


def test_canceller_does_not_call_domain_with_missing_required_field() -> None:
    catalog = AppointmentCatalog(professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")])
    state = create_medical_state("cancelar")
    state.update({"professional_id": 1, "datetime": datetime(2026, 9, 4, 16, tzinfo=timezone.utc)})

    result = create_cancel_node(catalog)(state)

    assert result["action_success"] is False
    assert "nome" in result["action_error"]
    assert catalog.appointments == []
