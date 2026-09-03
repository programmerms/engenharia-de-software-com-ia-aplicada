from app.graph import classify_medical_intent

def test_classifies_schedule_and_cancel_in_portuguese() -> None:
    assert classify_medical_intent("Quero agendar uma consulta") == "schedule"
    assert classify_medical_intent("Cancele minha consulta") == "cancel"

def test_classification_is_case_insensitive() -> None:
    assert classify_medical_intent("AGENDE uma consulta") == "schedule"

def test_unknown_and_conflicting_messages_are_safe() -> None:
    assert classify_medical_intent("Olá, preciso de ajuda médica") == "unknown"
    assert classify_medical_intent("Quero agendar e cancelar") == "unknown"


def test_router_accepts_only_safe_graph_destinations() -> None:
    from app.graph import route_medical

    assert route_medical({"intent": "unknown"}) == "message"
    assert route_medical({"intent": "unexpected"}) == "message"
    assert route_medical({"intent": "schedule"}) == "schedule"


def test_router_sends_provider_error_to_message() -> None:
    from app.graph import route_medical

    assert route_medical({"intent": "schedule", "error": "falha de parsing"}) == "message"
