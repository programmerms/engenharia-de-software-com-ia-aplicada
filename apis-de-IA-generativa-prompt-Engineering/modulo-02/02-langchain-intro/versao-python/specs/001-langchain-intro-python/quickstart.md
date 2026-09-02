# Quickstart: LangChain Intro Python

Este guia valida a baseline depois que a implementação for criada.

## Pré-requisitos

- Python 3.13.12 selecionado pelo pyenv e registrado no `.python-version`.
- Poetry instalado.
- Nenhuma API key ou serviço externo.

## Instalação

Na raiz do repositório:

```bash
poetry install
poetry run pytest
```

A execução dos testes deve concluir sem exigir LLM, provider, LangSmith ou rede.

## Iniciar localmente

O comando definitivo deve ser registrado no `pyproject.toml` e na documentação da
implementação. A forma esperada é equivalente a:

```bash
poetry run uvicorn langchain_intro.app:app --reload
```

O endereço e a porta efetivos devem ser documentados quando definidos.

## Validar os três caminhos

Com o servidor em execução, enviar:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"make this message UPPER please"}'
```

Resultado esperado: status `200` e a pergunta completa em maiúsculas.

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"MAKE THIS MESSAGE lower PLEASE"}'
```

Resultado esperado: status `200` e a pergunta completa em minúsculas.

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"HEY THERE!"}'
```

Resultado esperado: status `200` e a mensagem de fallback exata.

## Validar entradas inválidas

Testes automatizados devem demonstrar rejeição para:

- `{}`;
- `{"question": 12345}`;
- `{"question": "four"}`.

Também devem demonstrar que uma string válida com exatamente cinco caracteres é
aceita e que espaços, pontuação e acentos são preservados.

## Entender o grafo

Durante a leitura do código, localizar:

```text
State
  ↓
identify_intent
  ↓
conditional edge: uppercase | lowercase | unknown
  ↓
uppercase / lowercase / fallback
  ↓
append_response
  ↓
END
```

A estrutura de estado e os nós devem estar documentados sem exigir conhecimento da
referência TypeScript.
