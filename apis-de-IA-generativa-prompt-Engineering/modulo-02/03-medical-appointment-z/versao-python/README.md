# Medical Appointment com LLM — Python

Transposição didática do fluxo de consultas médicas de `../versao-typescript`. A implementação
Python preserva o template Poetry, FastAPI, LangChain, LangGraph e o catálogo em memória, mas usa
um serviço LLM injetável, Structured Output com Pydantic e roteamento condicional.

## Configuração

```bash
pyenv local 3.13.12
poetry install
cp .env.example .env
poetry run pytest
```

A suíte padrão usa fake LLMs e não exige API key, rede ou provider. Para usar OpenRouter, preencha
`.env` localmente:

```env
OPENROUTER_API_KEY=your-openrouter-key-here
OPENROUTER_MODEL=arcee-ai/trinity-large-preview:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=
OPENROUTER_X_TITLE=Medical Appointment Python
LLM_TEMPERATURE=0.7
LLM_TIMEOUT_SECONDS=30
```

Nunca versione `.env` ou API keys.

## Fluxo

```text
entrada → identify_intent → Structured Output → GraphState
                           ↓
                schedule / cancel / message
                           ↓
             scheduler/canceller → message → END
```

`identify_intent` usa o LLM para classificar `schedule`, `cancel` ou `unknown` e extrair dados.
O resultado não executa regras diretamente: o LangGraph decide o caminho, e o `AppointmentCatalog`
aplica as regras de negócio em memória. O node `message` gera a resposta final com Structured
Output e possui fallback seguro.

## API

```bash
poetry run uvicorn app.app:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"}'
```

A resposta contém `intent`, `success`, `message` e, quando aplicável, `appointment` ou `error`.
Entradas inválidas retornam 422; falhas inesperadas retornam 500 sem detalhes internos.

## LangGraph CLI

```bash
poetry run langgraph dev --no-browser --no-reload
```

O `langgraph.json` publica o grafo compilado em `src/langchain_intro/graph.py:graph`. FastAPI e CLI
são modos distintos de execução que compartilham a factory do grafo.

## Testes

```bash
poetry run pytest
```

Os testes unitários e de integração determinística injetam um fake LLM. O teste do provider real é
opt-in e só deve ser executado com configuração válida:

```bash
RUN_LLM_INTEGRATION_TESTS=1 poetry run pytest -m llm_integration
```

## Organização didática

- `config.py`: ambiente e configuração do modelo.
- `llm.py`: schemas Pydantic, protocolo, fake e serviço OpenRouter.
- `prompts/v1/`: templates separados da orquestração.
- `nodes/`: uma responsabilidade por etapa do fluxo.
- `graph.py` e `graph_factory.py`: estado, router, edges e composição.
- `appointment.py`: regras determinísticas do domínio.

FastAPI/Pydantic substituem Fastify/Zod de forma idiomática. A referência TypeScript é somente
leitura e não é copiada literalmente.
