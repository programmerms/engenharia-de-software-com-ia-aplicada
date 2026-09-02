from langchain_intro.graph import classify_medical_intent

def test_classifies_schedule_and_cancel_in_portuguese() -> None:
    assert classify_medical_intent("Quero agendar uma consulta") == "schedule"
    assert classify_medical_intent("Cancele minha consulta") == "cancel"

def test_classification_is_case_insensitive() -> None:
    assert classify_medical_intent("AGENDE uma consulta") == "schedule"

def test_unknown_and_conflicting_messages_are_safe() -> None:
    assert classify_medical_intent("Olá, preciso de ajuda médica") == "unknown"
    assert classify_medical_intent("Quero agendar e cancelar") == "unknown"
