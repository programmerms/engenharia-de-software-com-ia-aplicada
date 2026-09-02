# Medical Appointment Intent Flow — Python

Implementação funcional do Módulo 3, transposta conceitualmente de `../versao-typescript`.
O Módulo 2 forneceu o template técnico (Python, Poetry, FastAPI, LangChain, LangGraph e CLI); seu
domínio de transformação textual não é preservado como contrato.

## Configuração

```bash
pyenv local 3.13.12
poetry install
poetry run pytest
```

O Poetry usa o `.venv` local deste projeto. O fluxo padrão é determinístico e não exige API key,
provider LLM ou rede externa.

## API

Inicie com:

```bash
poetry run uvicorn langchain_intro.app:app --reload
```

`POST /chat` recebe uma solicitação médica:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"}'
```

A resposta contém `intent`, `success`, `message` e, quando aplicável, `appointment` ou `error`.
As intenções são `schedule`, `cancel` e `unknown`. Entradas estruturais inválidas retornam 422;
falhas inesperadas retornam 500 sem detalhes internos.

## Grafo

```text
START → identify_intent → roteamento condicional
                       ├→ schedule ─┐
                       ├→ cancel   ├→ message → END
                       └→ unknown  ┘
```

O estado é efêmero por invocação e contém mensagens, intenção, dados extraídos, resultado, erro e
resposta. Profissionais e consultas são mantidos em catálogo didático em memória; conflitos são
rejeitados e cancelamentos exigem correspondência de profissional, paciente e data/hora.

## LangGraph CLI

```bash
poetry run langgraph dev --no-browser --no-reload
```

O `langgraph.json` publica o grafo compilado em `src/langchain_intro/graph.py:graph`. FastAPI e o
CLI são modos de execução distintos que usam o mesmo grafo médico.

## Testes

```bash
poetry run pytest
```

A suíte cobre modelos e regras de domínio, identificação, estado, roteamento, contrato HTTP,
carregamento do CLI e fake de structured output. O fake LLM documenta a fronteira para uma futura
integração; a referência TypeScript analisada não invoca LLM nos nodes executáveis, portanto nenhum
provider real é necessário nesta etapa.

## Limites da transposição

FastAPI/Pydantic substituem Fastify/Zod e `StateGraph` Python substitui a API TypeScript de forma
idiomática. Nomes e diretórios não são copiados literalmente. `../versao-typescript` permanece
somente leitura.
