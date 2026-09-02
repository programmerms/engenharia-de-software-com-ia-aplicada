# Contrato do LangGraph CLI Dev

## Configuração

O projeto deve fornecer `langgraph.json` na raiz com o formato oficial atual:

```json
{
  "dependencies": ["."],
  "graphs": {
    "langchain_intro": "./src/langchain_intro/graph.py:graph"
  },
  "env": ".env"
}
```

O valor de `env` pode ser omitido se não for necessário para o grafo determinístico;
se existir, não deve conter credenciais. O valor essencial é o entrypoint do objeto
compilado já existente.

## Comando

Com Python 3.13.12 selecionado por pyenv e dependências instaladas por Poetry:

```bash
poetry install
poetry run langgraph dev
```

O comando deve iniciar o servidor local e informar a URL da interface oficial de
visualização e execução.

## Garantias

- O grafo carregado é `langchain_intro.graph:graph` via caminho indicado.
- Os nodes são `identify_intent`, `uppercase`, `lowercase`, `fallback` e
  `append_response`.
- O roteamento condicional oferece os três caminhos e converge em `append_response`.
- A execução não exige LLM, provider, API key ou serviço externo.
- O servidor é complementar e independente da aplicação FastAPI.
