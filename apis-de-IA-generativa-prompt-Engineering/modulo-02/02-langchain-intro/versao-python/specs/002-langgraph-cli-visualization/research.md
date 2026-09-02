# Research: Suporte ao LangGraph CLI e visualização do grafo

## Contexto

A pesquisa considerou a especificação, a baseline em `src/langchain_intro/graph.py`,
o `pyproject.toml` existente e a documentação oficial atual do LangGraph consultada
via Context7 em 2026-08-31.

## Decisão: configuração oficial atual

- **Decision**: criar `langgraph.json` na raiz com `dependencies`, `graphs` e `env`,
  apontando `graphs` para `./src/langchain_intro/graph.py:graph`.
- **Rationale**: a documentação atual descreve o arquivo como a configuração de
  dependências, grafos disponíveis e ambiente; `graphs` aceita o grafo compilado ou
  uma factory. Isso corresponde ao objeto já exportado pela baseline.
- **Alternatives considered**: formatos antigos foram rejeitados; uma factory
  exclusiva duplicaria a implementação e violaria FR-003/FR-007.

Fonte: [application structure](https://docs.langchain.com/oss/python/langgraph/application-structure)
e [Studio/local development](https://docs.langchain.com/oss/python/langgraph/studio).

## Decisão: CLI com extra de desenvolvimento local

- **Decision**: declarar `langgraph-cli[inmem]` no Poetry e executar
  `poetry run langgraph dev`.
- **Rationale**: a documentação oficial atual indica esse extra para o servidor
  local em memória e o comando para iniciar o ambiente. Python 3.13.12 satisfaz o
  requisito documentado de Python 3.11 ou superior.
- **Alternatives considered**: instalação global por pip, uv e providers foram
  rejeitados por conflitarem com Poetry ou com o escopo determinístico.

Fonte: [LangGraph Studio setup](https://docs.langchain.com/oss/python/langgraph/studio).

**Implementação confirmada**: Poetry resolveu `langgraph-cli` 0.4.31 com o extra
`inmem`, incluindo `langgraph-api` 0.5.42 e `langgraph-runtime-inmem` 0.20.1 no
lockfile. O servidor iniciou e registrou o grafo `langchain_intro` com Python
3.13.12. O `langgraph-api` emitiu aviso de versão mais nova/EOL durante a execução;
essa informação fica registrada para uma futura atualização, sem ampliar o escopo
desta feature.

## Decisão: grafo determinístico sem credenciais

- **Decision**: o entrypoint importará o mesmo objeto `graph` compilado existente e
  nenhum provider será configurado.
- **Rationale**: a baseline usa StateGraph, mensagens, funções Python e `invoke()`;
  carregamento, visualização e execução não precisam de rede, LLM, API key ou
  LangSmith.
- **Alternatives considered**: adicionar LLM introduziria nondeterminismo, credenciais
  e escopo de próxima etapa.

## Decisão: estrutura e comportamento testados separadamente

- **Decision**: combinar testes de configuração textual, carregamento/importação,
  inspeção do grafo compilado e execução dos três caminhos, preservando a integração
  HTTP existente.
- **Rationale**: configuração válida não garante entrypoint correto, e estrutura
  correta não garante equivalência de resultados. A UI oficial é demonstrada
  manualmente, mas a validação automatizada não depende dela.
- **Alternatives considered**: iniciar a UI em todos os testes seria frágil, lento e
  desnecessário para os contratos essenciais.

## Decisão: compatibilidade de importação do entrypoint

- **Decision**: trocar somente a importação relativa de `messages` por uma importação
  absoluta no módulo `src/langchain_intro/graph.py`.
- **Rationale**: o CLI atual carrega o arquivo apontado pelo caminho do JSON; nesse
  modo, a importação relativa falha porque o módulo não recebe um parent package.
  A importação absoluta funciona tanto no pacote Poetry quanto no carregamento do
  CLI e não altera nodes, edges, estado ou resultados.
- **Alternatives considered**: criar um wrapper/factory paralelo ou duplicar o grafo
  violaria a exigência de reutilização do objeto existente.

## Decisões sem clarificação

Não restam decisões bloqueantes. A versão exata de `langgraph-cli` será resolvida
pelo Poetry no ambiente de implementação, respeitando Python 3.13.12 e registrando
a versão no lockfile; fixar uma versão sem consultar o índice disponível seria menos
seguro do que seguir a documentação e o resolvedor atual.
