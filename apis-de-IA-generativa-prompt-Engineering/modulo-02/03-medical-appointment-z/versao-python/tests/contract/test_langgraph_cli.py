import json
from pathlib import Path
from app.graph import graph

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "langgraph.json"


def test_langgraph_config_points_to_medical_graph() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert config["dependencies"] == ["."]
    assert config["graphs"] == {"app": "./src/app/graph.py:graph"}


def test_configured_graph_is_compiled_and_invokable() -> None:
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "get_graph")


def test_graph_exposes_medical_nodes_and_conditional_edges() -> None:
    graph_view = graph.get_graph()
    assert {"identify_intent", "schedule", "cancel", "message"} <= set(graph_view.nodes)
    edges = {(edge.source, edge.target) for edge in graph_view.edges}
    assert ("__start__", "identify_intent") in edges
    assert {("identify_intent", target) for target in ("schedule", "cancel", "message")} <= edges
    assert ("message", "__end__") in edges


def test_cli_configuration_has_no_provider_or_secret_requirement() -> None:
    config_text = CONFIG_PATH.read_text(encoding="utf-8").lower()
    assert "api_key" not in config_text
    assert "langchain_openai" not in config_text
