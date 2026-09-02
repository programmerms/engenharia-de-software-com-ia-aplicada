import os
import signal
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException

from langchain_intro import app as app_module
from langchain_intro.app import ChatRequest, chat


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    project_root = Path(__file__).resolve().parents[2]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "langchain_intro.app:app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=project_root,
        start_new_session=True,
        env={**os.environ, "PYTHONPATH": os.pathsep.join([str(project_root / "src"), os.environ.get("PYTHONPATH", "")])},
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.communicate()[0] if process.stdout else ""
            pytest.fail(f"Uvicorn exited during startup:\n{output}")
        try:
            if httpx.get(f"{url}/docs", timeout=0.5).status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.1)
    else:
        os.killpg(process.pid, signal.SIGTERM)
        output = process.communicate(timeout=5)[0]
        pytest.fail(f"Uvicorn did not become ready:\n{output}")
    try:
        yield url
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def post(server: str, payload: dict) -> httpx.Response:
    with httpx.Client(base_url=server, timeout=5) as client:
        return client.post("/chat", json=payload)


def test_chat_schedules_appointment(server: str) -> None:
    response = post(server, {"question": "Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "schedule"
    assert body["success"] is True
    assert body["appointment"]["patient_name"] == "Maria Santos"


def test_chat_returns_unknown_guidance(server: str) -> None:
    response = post(server, {"question": "Olá, preciso de ajuda médica"})
    assert response.status_code == 200
    assert response.json()["intent"] == "unknown"
    assert response.json()["success"] is False


@pytest.mark.parametrize("payload", [{}, {"question": 12345}, {"question": "short"}])
def test_chat_rejects_invalid_input(server: str, payload: dict) -> None:
    assert post(server, payload).status_code == 422


def test_chat_returns_500_for_unexpected_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_invoke(*args: object, **kwargs: object) -> None:
        raise RuntimeError("internal test failure")
    monkeypatch.setattr(app_module.graph, "invoke", fail_invoke)
    with pytest.raises(HTTPException) as error:
        chat(ChatRequest(question="Olá, mensagem válida"))
    assert error.value.status_code == 500
    assert error.value.detail == "Internal server error"
