import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx
import pytest
from fastapi import HTTPException

from langchain_intro import app as app_module
from langchain_intro.app import ChatRequest, chat
from langchain_intro.graph import FALLBACK_MESSAGE


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "langchain_intro.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 8765), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        process.terminate()
        pytest.fail("Uvicorn did not start")
    yield "http://127.0.0.1:8765"
    process.terminate()
    process.wait(timeout=5)


def post(server: str, payload: dict) -> httpx.Response:
    with httpx.Client(base_url=server, timeout=5) as client:
        return client.post("/chat", json=payload)


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("make THis message UPPER please!", "MAKE THIS MESSAGE UPPER PLEASE!"),
        ("MAKE THIS MESSAGE lower PLEASE!", "make this message lower please!"),
        ("HEY THERE!", FALLBACK_MESSAGE),
    ],
)
def test_chat_returns_expected_result(
    server: str, question: str, expected: str
) -> None:
    response = post(server, {"question": question})

    assert response.status_code == 200
    assert response.json() == expected


def test_chat_accepts_exactly_five_characters(server: str) -> None:
    response = post(server, {"question": "hello"})

    assert response.status_code == 200
    assert response.json() == FALLBACK_MESSAGE


@pytest.mark.parametrize(
    "payload",
    [{}, {"question": 12345}, {"question": "four"}],
)
def test_chat_rejects_invalid_input(server: str, payload: dict) -> None:
    response = post(server, payload)

    assert response.status_code == 422


def test_chat_preserves_spaces_punctuation_and_accents(server: str) -> None:
    response = post(server, {"question": "  Olá, ação UPPER!  "})

    assert response.status_code == 200
    assert response.json() == "  OLÁ, AÇÃO UPPER!  "


def test_chat_returns_500_for_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_invoke(*args: object, **kwargs: object) -> None:
        raise RuntimeError("internal test failure")

    monkeypatch.setattr(app_module.graph, "invoke", fail_invoke)

    with pytest.raises(HTTPException) as error:
        chat(ChatRequest(question="valid question"))

    assert error.value.status_code == 500
    assert error.value.detail == "Internal server error"

