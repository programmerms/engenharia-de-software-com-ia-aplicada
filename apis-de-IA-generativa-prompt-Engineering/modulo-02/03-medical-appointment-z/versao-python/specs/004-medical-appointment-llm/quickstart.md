# Quickstart de validação

Este guia valida a feature sem depender de chamadas reais ao LLM por padrão.

## Pré-requisitos

1. Python 3.13.x selecionado pelo projeto.
2. Poetry instalado.
3. Dependências instaladas com `poetry install`.
4. Nenhuma API key para a suíte determinística.

## Validação padrão

```bash
poetry run pytest
```

Resultado esperado: testes de schema, prompts, fake LLM, domínio e grafo passam sem rede; os cenários `schedule`, `cancel`, `unknown` e erro seguem os caminhos esperados; e o catálogo não sofre mutação indevida.

## Validação do servidor HTTP

```bash
poetry run uvicorn app.app:app --host 127.0.0.1 --port 8000
```

Enviar `POST /chat` conforme [contracts/chat.md](./contracts/chat.md). O contrato deve manter respostas estruturadas e erros seguros.

## Validação do LangGraph CLI

```bash
poetry run langgraph dev --no-browser --no-reload
```

Confirmar que `langgraph.json` carrega `langchain_intro` por `src/langchain_intro/graph.py:graph` e expõe `identify_intent`, `schedule`, `cancel` e `message` com conditional edges.

## Validação opt-in do provider real

Configurar localmente, sem versionar o arquivo:

```bash
export OPENROUTER_API_KEY="..."
export OPENROUTER_MODEL="..."
export RUN_LLM_INTEGRATION_TESTS="1"
poetry run pytest -m llm_integration
```

O teste deve validar conectividade, resposta estruturada de intenção e mensagem. Não é requisito de `poetry run pytest`, não compartilha estado mutável com testes determinísticos e não imprime credenciais.

## Cenários mínimos de aceitação

- Agendamento natural com horário futuro livre → `schedule`, consulta criada e confirmação.
- Agendamento ocupado → erro de domínio, sem duplicação.
- Cancelamento existente → `cancel`, consulta removida e confirmação.
- Cancelamento inexistente → erro informado, catálogo preservado.
- Mensagem não relacionada → `unknown`, caminho direto para `message`, sem alteração.
- Saída inválida/falha do LLM → fallback seguro, sem ação baseada em dado parcial.
