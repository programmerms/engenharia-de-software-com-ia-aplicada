"""Prompt versionado para geração da resposta final ao paciente."""

from __future__ import annotations

import json


def build_message_prompt(scenario: str, details: dict[str, object]) -> str:
    """Monta o prompt de mensagem para um cenário já validado pelo fluxo."""

    payload = {
        "role": "Recepcionista médica cordial",
        "task": "Gere uma resposta clara, profissional, empática e concisa",
        "language": "português",
        "allowed_scenarios": ["schedule_success", "schedule_error", "cancel_success", "cancel_error", "unknown"],
        "scenario": scenario,
        "details": details,
        "rules": [
            "Não invente dados que não estejam nos detalhes.",
            "Para unknown, explique que o sistema ajuda a agendar ou cancelar consultas.",
            "Para erro, explique a situação sem expor detalhes internos.",
            "Retorne somente o campo message no schema estruturado.",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, default=str)
