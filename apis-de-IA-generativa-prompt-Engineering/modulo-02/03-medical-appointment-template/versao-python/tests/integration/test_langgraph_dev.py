import subprocess
import sys
import time
import os
import signal
import socket
from pathlib import Path
from collections.abc import Generator

import httpx
import pytest

from langchain_intro.graph import create_medical_state, graph


@pytest.fixture
def langgraph_dev() -> Generator[tuple[subprocess.Popen[str], str], None, None]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = str(probe.getsockname()[1])

    project_root = Path(__file__).resolve().parents[2]
    langgraph_executable = Path(sys.executable).with_name("langgraph")
    process = subprocess.Popen(
        [
            str(langgraph_executable),
            "dev",
            "--no-browser",
            "--no-reload",
            "--port",
            port,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=project_root,
        start_new_session=True,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                [str(project_root / "src"), os.environ.get("PYTHONPATH", "")]
            ),
        },
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            pytest.fail(f"LangGraph Dev exited during startup:\n{output}")
        try:
            response = httpx.get(f"{base_url}/docs", timeout=0.5)
            if response.status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    else:
        os.killpg(process.pid, signal.SIGTERM)
        output = process.communicate(timeout=5)[0]
        pytest.fail(f"LangGraph Dev did not become ready:\n{output}")

    yield process, base_url

    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def test_langgraph_dev_starts_and_loads_graph(
    langgraph_dev: tuple[subprocess.Popen[str], str],
) -> None:
    process, base_url = langgraph_dev

    assert process.poll() is None
    response = httpx.get(f"{base_url}/openapi.json", timeout=2)
    assert response.status_code == 200
    assert "langchain_intro" in response.text


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Quero agendar uma consulta", "schedule"),
        ("Quero cancelar uma consulta", "cancel"),
        ("Olá, preciso de ajuda médica", "unknown"),
    ],
)
def test_loaded_graph_routes_medical_intents(question: str, expected: str) -> None:
    result = graph.invoke(create_medical_state(question))
    assert result["intent"] == expected
