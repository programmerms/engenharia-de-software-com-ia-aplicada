# Implementation Plan: Medical Appointment Intent Flow

**Branch**: `003-medical-appointment-intent` | **Date**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

## Strategy

O projeto Python do Módulo 2 é template técnico, não aplicação funcional legada. Poetry, Python,
`.venv`, FastAPI, LangChain, LangGraph, CLI, `langgraph.json`, `src/` e práticas de testes serão
reutilizados. Estado, nodes, rotas e contratos de transformação textual podem ser substituídos pelo
domínio médico da referência.

## Technical Context

**Language/Version**: Python 3.13.12
**Project management**: Poetry com `.venv` local independente
**Stack**: FastAPI/Pydantic, LangChain Core, LangGraph e LangGraph CLI
**Functional source**: `../versao-typescript`, somente leitura
**Storage**: catálogo e consultas em memória
**Testing**: pytest, httpx, testes unitários, grafo, HTTP e contrato CLI
**LLM**: não utilizado pelos nodes executáveis observados; não é requisito desta etapa
**Constraints**: sem aplicação paralela, segredos versionados ou dependência de rede

## Architecture

```text
POST /chat → adapter HTTP → identify_intent
                              ↓ conditional routing
                    schedule / cancel / unknown
                              ↓
                         message → END
```

O estado será específico do domínio médico e conterá mensagens, intenção, dados, resultado, erro e
resposta. O grafo publicado em `langgraph.json` será o grafo médico compilado.

## Constitution Check

Passa: Python, Poetry e APIs atuais são mantidos; a referência permanece somente leitura; testes
serão offline; a implementação será didática. A substituição do domínio funcional do Módulo 2 é
intencional e explicitamente delimitada na especificação.

## Project Structure

```text
src/langchain_intro/
├── app.py          # API médica e adapter HTTP
├── graph.py        # estado, nodes e roteamento médico
├── appointment.py  # profissionais, consultas e regras
└── messages.py     # mensagens LangChain
tests/{unit,integration,contract}/
```

Os nomes são diretrizes Python, não contrato de compatibilidade com TypeScript ou com o exercício
anterior.

## Design Artifacts

- [research.md](./research.md): evidências e equivalências.
- [data-model.md](./data-model.md): entidades e transições médicas.
- [contracts/chat.md](./contracts/chat.md): contrato HTTP médico.
- [quickstart.md](./quickstart.md): execução e cenários.

## Phases

1. Validar template técnico e fronteira com a referência.
2. Definir estado médico, domínio, contrato HTTP e grafo.
3. Implementar e testar agendamento.
4. Implementar e testar cancelamento.
5. Integrar identificação, roteamento, resposta e CLI.
6. Documentar, validar infraestrutura e confirmar escopo.

## Post-Design Constitution Check

O design não exige preservar upper/lower/fallback, não introduz provider sem evidência, mantém
testes focados no domínio médico e preserva a referência TypeScript.
