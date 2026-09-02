import json
from pathlib import Path

from langchain_intro.graph import graph


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "langgraph.json"


def test_langgraph_config_points_to_existing_graph() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    assert config["dependencies"] == ["."]
    assert config["graphs"] == {
        "langchain_intro": "./src/langchain_intro/graph.py:graph"
    }
    assert "env" not in config


def test_configured_graph_is_the_existing_compiled_graph() -> None:
    assert graph is not None
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "get_graph")


def test_graph_exposes_expected_nodes() -> None:
    node_names = set(graph.get_graph().nodes)

    assert {
        "identify_intent",
        "uppercase",
        "lowercase",
        "fallback",
        "append_response",
    } <= node_names


def test_graph_preserves_conditional_routing() -> None:
    edges = {(edge.source, edge.target) for edge in graph.get_graph().edges}

    assert ("__start__", "identify_intent") in edges
    assert {("identify_intent", target) for target in ("uppercase", "lowercase", "fallback")} <= edges
    assert {("uppercase", "append_response"), ("lowercase", "append_response"), ("fallback", "append_response")} <= edges
    assert ("append_response", "__end__") in edges


def test_cli_configuration_has_no_provider_requirements() -> None:
    config_text = CONFIG_PATH.read_text(encoding="utf-8")

    assert "langchain_openai" not in config_text
    assert "langchain_anthropic" not in config_text
    assert "api_key" not in config_text.lower()
    assert "langsmith" not in config_text.lower()
