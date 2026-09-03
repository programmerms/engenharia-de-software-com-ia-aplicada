from datetime import datetime, timezone

from app.appointment import Appointment, AppointmentCatalog, Professional
from app.graph import create_medical_state
from app.graph_factory import build_graph
from app.llm import FakeMedicalLLM, Intent, IntentExtraction, MessageGeneration


def test_cancel_graph_uses_same_domain_service_and_structured_result() -> None:
    when = datetime(2026, 9, 4, 16, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        appointments=[Appointment(1, "Dr. Alicio da Silva", "Maria Santos", when, "check-up")],
    )
    llm = FakeMedicalLLM(
        extraction=IntentExtraction(
            intent=Intent.CANCEL,
            professional_id=1,
            professional_name="Dr. Alicio da Silva",
            patient_name="Maria Santos",
            datetime=when,
        ),
        generated=MessageGeneration(message="Cancelamento confirmado para Maria Santos."),
    )

    result = build_graph(llm, catalog).invoke(create_medical_state("Quero cancelar"))

    assert result["intent"] == Intent.CANCEL.value
    assert result["action_success"] is True
    assert result["visited"] == ["identify_intent", "cancel", "message"]
    assert catalog.appointments == []
