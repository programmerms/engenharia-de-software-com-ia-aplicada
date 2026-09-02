# Research: Medical Appointment Intent Flow

## Evidence from TypeScript

- `src/graph/graph.ts` usa `StateGraph` com `identifyIntent`, `schedule`, `cancel` e `message`,
  incluindo roteamento condicional.
- `src/services/appointmentService.ts` modela profissionais/consultas em memória, disponibilidade,
  inclusão e cancelamento.
- `src/server.ts` expõe `POST /chat` e invoca o grafo com mensagem humana.
- `src/prompts/` e `src/config.ts` descrevem prompts/OpenRouter, mas não são importados pelos nodes
  executáveis observados.
- `tests/router.e2e.test.ts` comprova principalmente status HTTP, não uso de LLM ou structured output.

## Decisions

### Template versus domínio

Python 3.13.12, pyenv, Poetry, `.venv`, FastAPI, LangChain, LangGraph, CLI, configuração, `src/`
e práticas de testes são infraestrutura herdada. Uppercase, lowercase, fallback, comandos, estado,
nodes, rotas e contratos do exercício anterior não são preservados por obrigação funcional.

### LangGraph

Usar `StateGraph`, `START`, `END`, nodes, `add_conditional_edges`, `compile` e `invoke`, com estado
tipado e atualizações parciais. A topologia preserva o conceito, não nomes ou sintaxe TypeScript.

### Domínio

Usar modelos Python para profissional/consulta, catálogo em memória, relógio injetável, validação
determinística e proteção contra conflito. Regras ficam fora do adapter HTTP.

### LLM

LLM, OpenRouter e structured output não são requisito do MVP: não há invocação de modelo nos nodes
executáveis analisados. A configuração declarada é contexto, não comportamento observado. Se uma
etapa posterior exigir LLM, ele entrará por adapter com fake/mock e variáveis de ambiente.

### HTTP e testes

`POST /chat` pode ser mantido como interface, mas seu contrato funcional será médico e estruturado.
Testes protegerão domínio, grafo, API, CLI e infraestrutura; não transformações textuais anteriores.

## Sources

- https://docs.langchain.com/oss/python/langgraph/use-graph-api
- https://docs.langchain.com/oss/python/langchain/models
- https://fastapi.tiangolo.com/tutorial/body
