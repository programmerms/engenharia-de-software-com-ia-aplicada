from datetime import datetime, timedelta, timezone
import pytest
from langchain_intro.appointment import Appointment, AppointmentCatalog, Professional

def make_catalog() -> AppointmentCatalog:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    return AppointmentCatalog(professionals=[Professional(id=1, name="Dr. Alicio da Silva", specialty="Cardiologia")], appointments=[Appointment(professional_id=1, professional_name="Dr. Alicio da Silva", patient_name="Joao da Silva", datetime=now + timedelta(days=1), reason="check-up")], now=lambda: now)

def test_free_slot_can_be_booked() -> None:
    service = make_catalog(); when = service.now() + timedelta(days=2)
    appointment = service.book(1, when, "Maria Santos", "avaliação")
    assert appointment.patient_name == "Maria Santos"
    assert service.find(1, when, "Maria Santos") == appointment

def test_occupied_slot_is_rejected() -> None:
    service = make_catalog()
    with pytest.raises(ValueError, match="indisponível"):
        service.book(1, service.appointments[0].datetime, "Maria Santos", "consulta")

def test_missing_professional_is_rejected() -> None:
    service = make_catalog()
    with pytest.raises(ValueError, match="Profissional"):
        service.book(99, service.now() + timedelta(days=2), "Maria Santos", "consulta")

def test_failed_cancellation_does_not_mutate_catalog() -> None:
    service = make_catalog(); before = len(service.appointments)
    with pytest.raises(ValueError, match="não encontrada"):
        service.cancel(1, service.appointments[0].datetime, "Outra Pessoa")
    assert len(service.appointments) == before


def test_matching_appointment_can_be_cancelled() -> None:
    service = make_catalog()
    appointment = service.appointments[0]
    removed = service.cancel(appointment.professional_id, appointment.datetime, appointment.patient_name)
    assert removed == appointment
    assert service.find(appointment.professional_id, appointment.datetime) is None
