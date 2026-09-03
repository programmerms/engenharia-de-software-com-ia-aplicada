"""Prompt versionado para classificação e extração de intenção."""

from __future__ import annotations

import json
from datetime import datetime


def build_identify_intent_prompt(question: str, professionals: list[dict[str, object]], now: datetime) -> str:
    """Monta o prompt de identificação sem chamar o modelo.

    O prompt explica o contrato de saída e fornece contexto do catálogo para
    reduzir alucinações de profissionais e deixar a função fácil de testar.
    """

    payload = {
        "role": "Recepcionista médica responsável por classificar intenções",
        "task": "Identifique a intenção e extraia dados de agendamento ou cancelamento",
        "allowed_intents": ["schedule", "cancel", "unknown"],
        "professionals": professionals,
        "current_datetime": now.isoformat(),
        "rules": [
            "Use schedule para marcar/agendar uma nova consulta.",
            "Use cancel para cancelar uma consulta existente.",
            "Use unknown para mensagens fora do domínio, ambíguas ou conflitantes.",
            "Não invente dados ausentes e não execute regras de negócio.",
            "Converta datas e horários relativos usando a data de referência.",
        ],
        "question": question,
        "output_instruction": "Retorne somente os campos presentes e compatíveis com o schema estruturado.",
    }
    return json.dumps(payload, ensure_ascii=False, default=str)
