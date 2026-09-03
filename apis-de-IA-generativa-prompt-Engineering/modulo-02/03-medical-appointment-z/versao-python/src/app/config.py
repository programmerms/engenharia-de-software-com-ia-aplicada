"""Configuração didática do modelo e do provider OpenRouter.

Este módulo representa a fronteira de configuração da aplicação. Ele lê valores
do ambiente, mas não exige a credencial durante a importação, pois o grafo deve
continuar disponível para testes offline e para o LangGraph CLI.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from collections.abc import Mapping

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    """Configuração imutável usada pelo cliente LLM.

    A classe representa a camada de configuração e participa do fluxo quando a
    factory cria o serviço OpenRouter. A API key fica opcional até uma chamada
    real, permitindo que schemas, grafo e testes sejam carregados sem segredo.
    """

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
        """Cria a configuração a partir do ambiente e de um mapa opcional.

        ``values`` existe para testes determinísticos e tem precedência sobre o
        ambiente. A função pode carregar `.env`, mas nunca imprime seus valores.
        Valores numéricos inválidos levantam ``ValueError``.
        """

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
            # Opções de roteamento/fallback não são inventadas pela aplicação;
            # somente configurações explicitamente fornecidas pelo OpenRouter
            # poderão ser adicionadas futuramente.
            provider=None,
        )

    def require_api_key(self) -> str:
        """Retorna a credencial ou falha somente ao tentar usar o provider real."""

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for the real LLM")
        return self.api_key


config = LLMConfig.from_environment()
