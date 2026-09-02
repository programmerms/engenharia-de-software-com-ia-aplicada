# Quickstart: LangGraph CLI e visualização do grafo

Este guia valida a evolução sem alterar a aplicação FastAPI existente.

## Pré-requisitos

- pyenv instalado;
- Python 3.13.12 disponível;
- Poetry 2.x instalado;
- nenhum LLM, provider, API key ou serviço externo.

## Instalação e testes da baseline

Na raiz do projeto:

```bash
pyenv local 3.13.12
python --version
poetry install
poetry run pytest
```

`python --version` deve exibir `Python 3.13.12`. A suíte deve passar sem credenciais
ou chamadas externas.

## Iniciar o LangGraph Dev

```bash
poetry run langgraph dev
```

O terminal deve informar que o servidor local iniciou e fornecer a URL da interface
oficial. Nela, selecionar o grafo configurado e verificar:

```text
START
  ↓
identify_intent
  ↓
conditional routing
  ├── uppercase
  ├── lowercase
  └── fallback
  ↓
append_response
  ↓
END
```

Os nomes devem corresponder aos nodes de `src/langchain_intro/graph.py`.

## Executar os três caminhos

Submeter uma entrada contendo `upper`, uma contendo `lower` e uma entrada desconhecida.
Confirmar, respectivamente:

1. `identify_intent → uppercase → append_response` e texto em maiúsculas;
2. `identify_intent → lowercase → append_response` e texto em minúsculas;
3. `identify_intent → fallback → append_response` e a mensagem exata
   `Unknown command. Try 'make this uppercase' or 'convert to lowercase'`.

Comparar com as chamadas de referência:

```python
from langchain_intro.graph import create_initial_state, graph

graph.invoke(create_initial_state("make this UPPER please"))
graph.invoke(create_initial_state("make this lower please"))
graph.invoke(create_initial_state("hello there"))
```

## Validar a aplicação FastAPI independentemente

Em outro terminal:

```bash
poetry run uvicorn langchain_intro.app:app --reload
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"make this UPPER please"}'
```

A resposta deve ser `MAKE THIS UPPER PLEASE`. Repetir com lower e fallback conforme
[contracts/chat.md](contracts/chat.md). Parar `langgraph dev` não deve interromper
o `POST /chat`.

## Preservação da referência TypeScript

Esta evolução altera somente a versão Python. O diretório `../versao-typescript`
permanece fora do escopo e deve continuar sem modificações.

## O que observar

`State` é o conjunto de dados da execução; `Node` é uma transformação; `Edge` liga
etapas; `Conditional Edge` escolhe um caminho; `StateGraph` descreve o workflow;
`compile()` produz o objeto executável; `invoke()` executa uma entrada. O
`langgraph.json` diz ao CLI qual grafo Python carregar, e `langgraph dev` fornece o
ambiente local que visualiza e executa esse mesmo workflow. FastAPI continua sendo
somente o servidor HTTP da aplicação.
