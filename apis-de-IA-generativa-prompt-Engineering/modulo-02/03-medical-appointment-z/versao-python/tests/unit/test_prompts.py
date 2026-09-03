from datetime import datetime, timezone

from app.prompts.v1.identify_intent import build_identify_intent_prompt
from app.prompts.v1.message import build_message_prompt


def test_identify_prompt_contains_question_and_professional_catalog() -> None:
    prompt = build_identify_intent_prompt(
        "Quero marcar uma consulta",
        [{"id": 1, "name": "Dr. Alicio da Silva", "specialty": "Cardiologia"}],
        datetime(2026, 9, 3, tzinfo=timezone.utc),
    )

    assert "Quero marcar uma consulta" in prompt
    assert "Dr. Alicio da Silva" in prompt
    assert "schedule" in prompt
    assert "cancel" in prompt
    assert "unknown" in prompt


def test_message_prompt_contains_scenario_and_details() -> None:
    prompt = build_message_prompt(
        "schedule_success",
        {"patient_name": "Maria Santos", "professional_name": "Dr. Alicio da Silva"},
    )

    assert "schedule_success" in prompt
    assert "Maria Santos" in prompt
    assert "Dr. Alicio da Silva" in prompt
    assert "português" in prompt
