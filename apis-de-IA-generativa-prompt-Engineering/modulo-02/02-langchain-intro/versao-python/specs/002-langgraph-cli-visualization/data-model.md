# Data Model: Suporte ao LangGraph CLI e visualização do grafo

## Configuração do ambiente de desenvolvimento

Arquivo versionado na raiz, lido pelo CLI a partir do diretório atual.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---:|---|
| `dependencies` | lista | sim | inclui a aplicação local necessária para resolver `src/langchain_intro` |
| `graphs` | mapa nome → entrypoint | sim | aponta para `./src/langchain_intro/graph.py:graph` |
| `env` | caminho | conforme formato atual | não contém segredos nem introduz provider |

O arquivo deve ser JSON válido e o nome lógico do grafo deve ser estável.

## Grafo executável

É o objeto `graph` já existente, compilado a partir de `StateGraph(GraphState)`.
CLI e FastAPI apontam para a mesma instância exportada pelo módulo.

| Elemento | Valor/Regra |
|---|---|
| Estado | `messages`, `command` e `output` |
| Entrada | estado inicial criado a partir de pergunta textual |
| Nodes | `identify_intent`, `uppercase`, `lowercase`, `fallback`, `append_response` |
| Roteamento | `identify_intent` escolhe três destinos por comando |
| Finalização | todos convergem em `append_response` e terminam em `END` |
| Persistência | nenhuma; execução efêmera |

## Execução observável

1. A entrada inicia o estado com mensagem humana e `output` igual ao texto.
2. `identify_intent` define o comando; `upper` tem precedência sobre `lower`.
3. O caminho selecionado atualiza `output` ou define o fallback.
4. `append_response` acrescenta a mensagem final.
5. A saída funcional é o valor final de `output`.

Invariantes: transformações preservam espaços, pontuação e acentos; o fallback é
exato; nenhuma execução solicita credenciais ou compartilha estado.
