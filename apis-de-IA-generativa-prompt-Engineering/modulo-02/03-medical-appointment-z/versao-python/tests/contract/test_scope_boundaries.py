import json
from pathlib import Path

import fastapi
import langchain_core
import langgraph

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_template_stack_imports_from_active_environment() -> None:
    assert fastapi.__version__
    assert langchain_core is not None
    assert langgraph.__path__


def test_cli_config_has_no_external_provider_or_secret_settings() -> None:
    config = json.loads((PROJECT_ROOT / "langgraph.json").read_text(encoding="utf-8"))
    assert set(config) <= {"dependencies", "graphs", "env"}
    assert "api_key" not in json.dumps(config).lower()


def test_typescript_reference_is_outside_python_feature_scope() -> None:
    assert (PROJECT_ROOT.parent / "versao-typescript").is_dir()
    assert not (PROJECT_ROOT / "src" / "app" / "graph.ts").exists()
