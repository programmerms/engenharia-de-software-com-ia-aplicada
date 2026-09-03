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

O `langgraph.json` publica o grafo compilado em `src/app/graph/graph.py:graph`. FastAPI e CLI
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

## Organização arquitetural do template

```text
src/app/
├── api/                 # FastAPI e contrato HTTP
├── config/              # ambiente e configuração
├── domain/
│   ├── models/          # Professional e Appointment
│   └── services/        # AppointmentService e regras de negócio
├── graph/
│   ├── nodes/           # etapas únicas do workflow
│   ├── state.py         # dados do workflow
│   ├── router.py        # conditional routing
│   └── graph.py         # definição/publicação do grafo
├── llm/                 # contratos, Structured Output e providers
├── prompts/             # prompts versionados
└── factory/             # Composition Root e injeção de dependências
```

O princípio permanente é `State = dados`, `Services = comportamento` e `Factory = composição`.
O LLM interpreta linguagem natural e produz estruturas Pydantic; nunca executa regras de negócio.
As próximas aulas devem evoluir esses pacotes, sem criar arquiteturas paralelas.

## Fluxo completo

```text
Cliente → FastAPI → LangGraph → identify_intent → LangChain → OpenRouter → LLM
        → Structured Output/Pydantic → GraphState → Router → schedule/cancel
        → AppointmentService → message → LLM/fallback → resposta
```

- `api`: recebe a requisição e normaliza a resposta HTTP.
- `config`: carrega ambiente e segredos sem expô-los.
- `llm`: isola OpenRouter, abstração `MedicalLLM`, fakes e saída estruturada.
- `graph`: orquestra nodes, estado e conditional edges.
- `domain`: mantém modelos e regras determinísticas de consulta.
- `factory`: cria implementações, injeta dependências e compila o grafo.
- `prompts`: mantém instruções versionadas fora dos nodes.

Os módulos antigos na raiz de `app` (`graph_factory.py`, `llm_service.py`, `models.py`,
`appointment_service.py` e `state.py`) são fachadas de compatibilidade. Novas aulas devem usar os
pacotes canônicos e evoluir componentes existentes antes de criar responsabilidades paralelas.

`OpenRouterMedicalLLM` é a integração real; `FakeMedicalLLM` serve aos testes determinísticos;
`OfflineMedicalLLM` permite execução local sem provider externo. Executar sem API key não significa
que um LLM real esteja sendo utilizado.

FastAPI/Pydantic substituem Fastify/Zod de forma idiomática. A referência TypeScript é somente
leitura e não é copiada literalmente.
