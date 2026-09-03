from datetime import datetime, timezone

from app.graph import create_medical_state
from app.llm import FakeMedicalLLM, Intent, IntentExtraction
from app.nodes.identify_intent import create_identify_intent_node


def test_identify_node_puts_structured_schedule_data_in_state() -> None:
    node = create_identify_intent_node(
        FakeMedicalLLM(
            extraction=IntentExtraction(
                intent=Intent.SCHEDULE,
                professional_id=1,
                professional_name="Dr. Alicio da Silva",
                patient_name="Maria Santos",
                datetime=datetime(2026, 9, 4, 16, tzinfo=timezone.utc),
                reason="check-up",
            )
        )
    )

    result = node(create_medical_state("Gostaria de marcar uma consulta"))

    assert result["intent"] == Intent.SCHEDULE.value
    assert result["patient_name"] == "Maria Santos"
    assert result["professional_id"] == 1
    assert result["datetime"].hour == 16


def test_identify_node_routes_provider_failure_to_safe_error() -> None:
    class BrokenLLM(FakeMedicalLLM):
        def extract_intent(self, question, professionals, now):
            raise RuntimeError("provider unavailable")

    result = create_identify_intent_node(BrokenLLM(extraction=IntentExtraction(intent=Intent.UNKNOWN)))(
        create_medical_state("Gostaria de marcar uma consulta")
    )

    assert result["intent"] == Intent.UNKNOWN.value
    assert "LLM" in result["error"]
