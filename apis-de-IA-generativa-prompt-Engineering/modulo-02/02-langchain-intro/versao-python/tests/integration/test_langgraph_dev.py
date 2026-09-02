import subprocess
import sys
import time
from collections.abc import Generator

import httpx
import pytest

from langchain_intro.graph import FALLBACK_MESSAGE, create_initial_state, graph


@pytest.fixture
def langgraph_dev() -> Generator[tuple[subprocess.Popen[str], str], None, None]:
    port = "8124"
    process = subprocess.Popen(
        [
            "poetry",
            "run",
            "langgraph",
            "dev",
            "--no-browser",
            "--no-reload",
            "--port",
            port,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
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
        process.terminate()
        output = process.communicate(timeout=5)[0]
        pytest.fail(f"LangGraph Dev did not become ready:\n{output}")

    yield process, base_url

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
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
        ("make this UPPER please", "MAKE THIS UPPER PLEASE"),
        ("make this lower please", "make this lower please"),
        ("hello there", FALLBACK_MESSAGE),
    ],
)
def test_loaded_graph_preserves_baseline_paths(
    question: str, expected: str
) -> None:
    result = graph.invoke(create_initial_state(question))

    assert result["output"] == expected
