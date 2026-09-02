# Research: LangChain Intro Python

## Contexto da pesquisa

A pesquisa confrontou a referência em `../versao-typescript`, a especificação da
feature e a documentação oficial atual consultada pelo Context7 em 2026-08-30.

## Decisão: usar StateGraph com estado explícito

- **Decision**: representar o fluxo com `StateGraph`, um schema de estado explícito,
  nós nomeados, `START`, `END`, aresta condicional, `compile()` e `invoke()`.
- **Rationale**: a documentação oficial descreve `StateGraph` como a implementação
  principal para workflows com schema de estado; compilação prepara e valida o grafo,
  e a invocação executa uma entrada. Isso preserva diretamente os conceitos da
  referência sem usar persistência.
- **Alternatives considered**: uma cadeia linear de funções Python esconderia o
  roteamento condicional; `MessagesState` pronto simplificaria mensagens, mas um
  estado próprio torna `command` e `output` visíveis para o estudo.

Fonte: [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) e
[LangGraph Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart).

## Decisão: mensagens atuais do LangChain

- **Decision**: usar os tipos atuais de mensagem do ecossistema LangChain para a
  mensagem humana e a resposta de IA, mantendo o histórico somente na execução.
- **Rationale**: a referência usa `HumanMessage` e `AIMessage`; a equivalência
  conceitual deve preservar o papel dessas mensagens, não os imports ou pacotes da
  versão TypeScript.
- **Alternatives considered**: strings simples seriam suficientes para o resultado,
  mas removeriam o conceito didático de mensagens; memória persistente foi excluída
  por não existir na referência.

Fonte: [LangChain Python overview](https://docs.langchain.com/oss/python/langchain/overview).

## Decisão: LangChain sem chamada a modelo

- **Decision**: LangChain será limitado à representação conceitual de mensagens.
- **Rationale**: a análise do código original não encontrou modelo, provider, prompt ou
  chamada de LLM. Adicionar um provider criaria credenciais, rede e comportamento não
  presente na aula.
- **Alternatives considered**: incluir um modelo para “demonstrar IA” foi rejeitado por
  violar o escopo da baseline e tornar os testes não determinísticos.

## Decisão: FastAPI e Pydantic para a borda HTTP

- **Decision**: declarar um modelo de entrada com `question` textual e tamanho mínimo
  de cinco, e uma única operação `POST /chat`.
- **Rationale**: FastAPI documenta modelos Pydantic para corpos de requisição e
  validação declarativa; isso evita duplicação de validação e mantém o contrato
  verificável.
- **Alternatives considered**: parsing manual do JSON e validação dentro do grafo
  seriam menos claros e permitiriam executar o fluxo com entrada inválida.

Fonte: [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body),
[FastAPI Body Fields](https://fastapi.tiangolo.com/tutorial/body-fields) e
[FastAPI Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors).

## Decisão: Poetry e dependências mínimas

- **Decision**: declarar FastAPI, LangGraph e a dependência mínima de mensagens
  LangChain em `pyproject.toml`; declarar pytest e o cliente HTTP necessário como
  dependências de desenvolvimento.
- **Rationale**: Poetry é o mecanismo estabelecido pela Constitution para ambiente,
  metadados e dependências. O conjunto é suficiente para a aplicação e seus testes.
- **Alternatives considered**: providers, `langsmith`, banco, framework adicional,
  carregador de configuração e servidor alternativo foram rejeitados por não serem
  necessários.
- **Implementation note**: confirmar versões compatíveis no ambiente durante a
  implementação e registrar a escolha no `pyproject.toml`.

Fonte: [Poetry documentation](https://python-poetry.org/docs/).

## Mapeamento da referência

| TypeScript original | Conceito | Plano Python |
|---|---|---|
| Fastify `POST /chat` | borda HTTP | uma rota FastAPI |
| schema com `question` e minLength 5 | contrato/validação | modelo Pydantic |
| `GraphState` | estado tipado | schema de estado explícito do LangGraph |
| `HumanMessage` | entrada conversacional | mensagem humana LangChain |
| `AIMessage` | resposta conversacional | mensagem de resposta LangChain |
| `identifyIntent` | classificação determinística | nó de identificação |
| `upperCaseNode` | transformação | nó uppercase |
| `lowerCaseNode` | transformação | nó lowercase |
| `fallbackNode` | caminho desconhecido | nó fallback |
| `addConditionalEdges` | roteamento | aresta condicional do StateGraph |
| `compile` | grafo executável | grafo compilado |
| `invoke` | execução | uma invocação por requisição |
| Fastify inject + Node:test | contrato testável | pytest + cliente de teste FastAPI |
| `langgraph.json` | execução de desenvolvimento | não reproduzir formato; manter grafo compilável |

