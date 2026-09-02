# Contrato preservado: `POST /chat`

## Request

`POST /chat` recebe JSON com uma propriedade obrigatória `question`.

| Campo | Tipo | Regra |
|---|---|---|
| `question` | string | mínimo de 5 caracteres |

## Response

Para entrada válida, responde `200` com uma string JSON contendo somente o `output`
produzido pelo mesmo `graph` usado pelo LangGraph CLI.

| Entrada | Resultado |
|---|---|
| texto contendo `upper` | texto integralmente em maiúsculas |
| texto sem `upper` contendo `lower` | texto integralmente em minúsculas |
| texto sem os comandos | `Unknown command. Try 'make this uppercase' or 'convert to lowercase'` |

`upper` tem precedência quando ambos aparecem. Espaços, pontuação e acentos são
preservados nas transformações.

## Independência

O endpoint continua funcionando sem `langgraph dev`. FastAPI e o servidor de
desenvolvimento do grafo são modos complementares; um não é requisito do outro.
