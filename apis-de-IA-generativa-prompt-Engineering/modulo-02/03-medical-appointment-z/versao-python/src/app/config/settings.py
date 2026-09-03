"""Configuração de ambiente usada pela composição da aplicação."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    """Configuração imutável que a factory injeta no serviço de LLM."""

    api_key: str | None = None
    model: str = "arcee-ai/trinity-large-preview:free"
    base_url: str = "https://openrouter.ai/api/v1"
    http_referer: str = ""
    x_title: str = "Medical Appointment Python"
    temperature: float = 0.7
    timeout: float = 30.0
    provider: dict[str, object] | None = None

    @classmethod
    def from_environment(cls, values: Mapping[str, str] | None = None) -> "LLMConfig":
        """Lê ambiente/.env sem exigir credencial para testes offline."""

        load_dotenv()
        source = os.environ if values is None else values

        def value(name: str, default: str = "") -> str:
            return source.get(name, default).strip()

        def number(name: str, default: float) -> float:
            raw = value(name)
            return default if not raw else float(raw)

        return cls(
            api_key=value("OPENROUTER_API_KEY") or None,
            model=value("OPENROUTER_MODEL", cls.model),
            base_url=value("OPENROUTER_BASE_URL", cls.base_url),
            http_referer=value("OPENROUTER_HTTP_REFERER"),
            x_title=value("OPENROUTER_X_TITLE", cls.x_title),
            temperature=number("LLM_TEMPERATURE", cls.temperature),
            timeout=number("LLM_TIMEOUT_SECONDS", cls.timeout),
        )

    def require_api_key(self) -> str:
        """Retorna a chave ou falha somente ao usar o provider real."""

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for the real LLM")
        return self.api_key


config = LLMConfig.from_environment()
