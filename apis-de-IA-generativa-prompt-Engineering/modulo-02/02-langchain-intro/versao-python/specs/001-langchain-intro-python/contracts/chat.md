# Contrato HTTP: POST /chat

## Request

**Method**: `POST`

**Path**: `/chat`

**Content-Type**: `application/json`

**Body**:

```json
{
  "question": "make this message upper please"
}
```

### Request rules

- `question` é obrigatório.
- `question` deve ser texto.
- `question` deve ter pelo menos cinco caracteres.
- Campos adicionais não são necessários para o contrato.
- O conteúdo é usado integralmente no processamento.

## Successful response

**Status**: `200`

**Content-Type**: `application/json`

A resposta contém somente a saída textual do fluxo. Como a referência retorna uma
string JSON, exemplos conceituais:

```json
"MAKE THIS MESSAGE UPPER PLEASE"
```

Para uma pergunta sem comando conhecido:

```json
"Unknown command. Try 'make this uppercase' or 'convert to lowercase'"
```

## Processing rules

| Condição em `question` | Resultado |
|---|---|
| contém `upper`, ignorando caixa | pergunta completa em maiúsculas |
| não contém `upper` e contém `lower`, ignorando caixa | pergunta completa em minúsculas |
| não contém nenhum dos dois | mensagem de fallback exata |
| contém ambos | pergunta completa em maiúsculas |

## Validation errors

Corpo ausente, campo ausente, tipo não textual ou texto com menos de cinco caracteres
devem produzir erro HTTP de validação. O status exato deve seguir o comportamento padrão
do FastAPI/Pydantic escolhido no planejamento de implementação; o requisito observável
é rejeitar a entrada antes de executar o grafo.

## Unexpected errors

Uma exceção inesperada durante o processamento deve produzir HTTP `500`, sem stack
trace, credenciais ou detalhes internos sensíveis na resposta.

