from datetime import datetime, timezone

from app.appointment import AppointmentCatalog, Professional
from app.graph_factory import build_graph
from app.graph import create_medical_state
from app.llm import FakeMedicalLLM, Intent, IntentExtraction, MessageGeneration


def test_schedule_graph_uses_structured_llm_result_and_domain_service() -> None:
    now = datetime(2026, 9, 3, 9, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        now=lambda: now,
    )
    llm = FakeMedicalLLM(
        extraction=IntentExtraction(
            intent=Intent.SCHEDULE,
            professional_id=1,
            professional_name="Dr. Alicio da Silva",
            patient_name="Maria Santos",
            datetime=datetime(2026, 9, 4, 16, tzinfo=timezone.utc),
            reason="check-up",
        ),
        generated=MessageGeneration(message="Consulta confirmada para Maria Santos."),
    )

    result = build_graph(llm, catalog).invoke(create_medical_state("Quero marcar uma consulta", catalog))

    assert result["intent"] == Intent.SCHEDULE.value
    assert result["action_success"] is True
    assert result["visited"] == ["identify_intent", "schedule", "message"]
    assert result["appointment_data"]["patient_name"] == "Maria Santos"
    assert result["messages"][-1].content == "Consulta confirmada para Maria Santos."
