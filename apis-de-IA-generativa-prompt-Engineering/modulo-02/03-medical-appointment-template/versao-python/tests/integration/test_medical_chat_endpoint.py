from fastapi.testclient import TestClient

from langchain_intro.app import app

client = TestClient(app)


def test_schedule_response_is_structured() -> None:
    response = client.post("/chat", json={"question": "Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"})
    assert response.status_code == 200
    assert response.json()["intent"] == "schedule"
    assert response.json()["success"] is True


def test_unknown_guidance_is_structured() -> None:
    response = client.post("/chat", json={"question": "Olá, preciso de ajuda médica"})
    assert response.status_code == 200
    assert response.json()["intent"] == "unknown"
    assert response.json()["success"] is False


def test_cancel_not_found_is_structured() -> None:
    response = client.post("/chat", json={"question": "Sou Maria Santos e quero cancelar uma consulta com Dr. Alicio da Silva amanhã às 16h"})
    assert response.status_code == 200
    assert response.json()["intent"] == "cancel"
    assert response.json()["success"] is False
    assert "não encontrada" in response.json()["error"]


def test_short_question_is_rejected_before_graph() -> None:
    response = client.post("/chat", json={"question": "curta"})
    assert response.status_code == 422
