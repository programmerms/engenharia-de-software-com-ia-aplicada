import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_cli_config_has_no_external_provider_or_secret_settings() -> None:
    config = json.loads((PROJECT_ROOT / "langgraph.json").read_text(encoding="utf-8"))

    assert set(config) <= {"dependencies", "graphs", "env"}
    assert all("api" not in value.lower() for value in config.values() if isinstance(value, str))
    assert all("key" not in value.lower() for value in config.values() if isinstance(value, str))


def test_typescript_reference_is_outside_python_feature_scope() -> None:
    typescript_reference = PROJECT_ROOT.parent / "versao-typescript"

    assert typescript_reference.is_dir()
    assert not (PROJECT_ROOT / "src" / "langchain_intro" / "graph.ts").exists()
