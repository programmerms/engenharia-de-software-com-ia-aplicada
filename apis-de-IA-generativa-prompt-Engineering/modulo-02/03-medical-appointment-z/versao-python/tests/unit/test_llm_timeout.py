from datetime import datetime, timezone

from app.appointment import AppointmentCatalog, Professional
from app.graph import create_medical_state
from app.graph_factory import build_graph
from app.llm import IntentExtraction, MessageGeneration


class TimeoutLLM:
    """Fake imediato para exercitar a fronteira de timeout sem esperar."""

    def extract_intent(self, question, professionals, now):
        """Simula timeout na identificação sem acessar rede."""

        raise TimeoutError("simulated LLM timeout")

    def generate_message(self, scenario, details):
        """Simula indisponibilidade também na geração da mensagem."""

        raise TimeoutError("simulated LLM timeout")


def test_identification_timeout_is_safe_and_keeps_domain_untouched() -> None:
    now = datetime(2026, 9, 3, 9, tzinfo=timezone.utc)
    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        now=lambda: now,
    )

    result = build_graph(TimeoutLLM(), catalog).invoke(create_medical_state("Quero agendar", catalog))

    assert result["intent"] == "unknown"
    assert "interpretação" in result["error"]
    assert result["output"]
    assert result["action_success"] is False
    assert catalog.appointments == []


def test_schedule_missing_optional_reason_does_not_block_domain() -> None:
    class ScheduleLLM:
        """Fake que fornece os campos obrigatórios sem motivo."""

        def extract_intent(self, question, professionals, now):
            """Retorna agendamento estruturado sem ``reason``."""

            return IntentExtraction(
                intent="schedule",
                professional_id=1,
                patient_name="Maria Santos",
                datetime=datetime(2026, 9, 4, 16, tzinfo=timezone.utc),
            )

        def generate_message(self, scenario, details):
            """Retorna uma confirmação determinística."""

            return MessageGeneration(message="Consulta confirmada.")

    catalog = AppointmentCatalog(
        professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia")],
        now=lambda: datetime(2026, 9, 3, 9, tzinfo=timezone.utc),
    )
    result = build_graph(ScheduleLLM(), catalog).invoke(create_medical_state("Agendar", catalog))

    assert result["action_success"] is True
    assert result["appointment_data"]["reason"] == "consulta"
