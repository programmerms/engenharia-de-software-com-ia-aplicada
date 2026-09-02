from langchain_intro.llm import FakeMedicalLLM, IntentExtraction, MessageGeneration


def test_fake_llm_supplies_structured_values_without_provider() -> None:
    fake = FakeMedicalLLM(
        extraction=IntentExtraction(intent="schedule", patient_name="Maria Santos"),
        generated=MessageGeneration(message="Resposta simulada"),
    )
    assert fake.extract("qualquer texto").intent == "schedule"
    assert fake.message("schedule", {}).message == "Resposta simulada"
