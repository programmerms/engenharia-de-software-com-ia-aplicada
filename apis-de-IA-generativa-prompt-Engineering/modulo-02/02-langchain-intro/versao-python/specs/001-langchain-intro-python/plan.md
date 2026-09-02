# Implementation Plan: LangChain Intro Python

**Branch**: `001-langchain-intro-python` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-langchain-intro-python/spec.md`

## Summary

Reconstruir a aplicação didática da referência TypeScript como um pequeno serviço HTTP
Python. O serviço receberá `question`, validará o corpo, executará um grafo
determinístico com estado explícito e devolverá apenas a saída textual. O grafo terá
um nó de identificação, um roteamento condicional para `uppercase`, `lowercase` ou
`unknown`, nós de transformação/fallback e um nó final de resposta.

O equivalente conceitual será implementado com FastAPI, Pydantic, LangGraph Python e
mensagens do ecossistema LangChain. Não haverá LLM, provider, persistência ou LangSmith
obrigatório. A solução manterá a estrutura pequena para que o estudante consiga
visualizar o percurso do estado.

## Technical Context

**Language/Version**: Python 3.13.12, selecionado por pyenv e fixado no Poetry

**Primary Dependencies**: FastAPI, Pydantic (via FastAPI), LangGraph, LangChain

**Storage**: N/A; estado somente durante uma requisição

**Testing**: pytest, cliente de teste do FastAPI e testes unitários de funções puras

**Target Platform**: Linux/macOS/Windows para execução local; servidor HTTP local

**Project Type**: serviço web didático

**Performance Goals**: 95% de 20 requisições válidas locais em até 1 segundo,
conforme SC-003; sem meta de throughput de produção

**Constraints**: sem rede externa, sem API key, sem LLM, sem persistência, sem
autenticação e com respostas determinísticas

**Scale/Scope**: uma rota, três caminhos de processamento, um estado por execução e
pequeno conjunto de testes didáticos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Aprendizado e simplicidade**: PASS. O grafo tem somente as responsabilidades
  exigidas e não introduz camadas arquiteturais artificiais.
- **Python e stack**: PASS. Python será a linguagem principal; Poetry, FastAPI,
  LangGraph e LangChain têm papéis explícitos e limitados.
- **Reconstrução conceitual**: PASS. O plano preserva comportamento e conceitos, não
  nomes ou diretórios TypeScript.
- **APIs atuais**: PASS. As escolhas de `StateGraph`, estado tipado, arestas
  condicionais, `compile` e `invoke` foram confrontadas com a documentação oficial
  atual; detalhes estão em [research.md](./research.md).
- **Evolução incremental**: PASS. LLM, RAG, persistência, agentes, LangSmith e demais
  conceitos futuros permanecem fora do escopo.
- **Segredos**: PASS. A baseline não requer credenciais e não armazenará valores reais.
- **Testabilidade**: PASS. Contratos HTTP e lógica de classificação/transformação serão
  testados sem serviços externos.
- **Transparência e referência**: PASS. O mapeamento TypeScript → conceito → Python
  está registrado em [research.md](./research.md).
- **Integridade da evolução**: PASS. O [quickstart.md](./quickstart.md) define
  instalação, execução e validação local.
- **Gate result**: PASS antes da pesquisa; PASS após o design abaixo.

## Project Structure

### Documentation (this feature)

```text
specs/001-langchain-intro-python/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── chat.md
└── tasks.md                 # criado posteriormente por $speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── langchain_intro/
    ├── __init__.py
    ├── app.py                 # criação da aplicação FastAPI e rota /chat
    ├── graph.py               # estado, nós, edges, compilação e execução do grafo
    └── messages.py             # conversão/representação didática de mensagens

tests/
├── unit/
│   ├── test_intent.py
│   └── test_transformations.py
└── integration/
    └── test_chat_endpoint.py
```

**Structure Decision**: Single Python web service com pacote pequeno. `app.py`
concentra a borda HTTP; `graph.py` deixa visíveis estado, nós, edges e compilação;
`messages.py` mantém a representação de mensagens separada somente para reforçar o
conceito. Não haverá `services/`, repositórios, containers, banco ou camadas de
domínio porque a aplicação não precisa deles.

## Design Decisions

### Mapeamento tecnológico

| Referência TypeScript | Conceito preservado | Decisão Python | Justificativa e diferença |
|---|---|---|---|
| Fastify + schema da rota | Contrato HTTP e validação de entrada | FastAPI com modelo Pydantic | Validação declarativa e documentação automática; o formato de erro pode diferir do Fastify, mas o comportamento de rejeitar entrada inválida permanece. |
| `GraphState` com Zod | Estado tipado do fluxo | `TypedDict` ou modelo tipado simples com `messages`, `command`, `output` | Expõe as três partes exigidas sem criar persistência. A forma exata será decidida na implementação conforme a API atual do LangGraph. |
| `HumanMessage`/`AIMessage` | Mensagem de entrada e resposta | Mensagens equivalentes atuais de LangChain | Preserva o conceito de histórico conceitual; não há memória entre requisições. |
| `identifyIntent` | Classificação determinística | Nó Python pequeno | A regra textual não é IA generativa e pertence à lógica da aplicação. |
| `upperCaseNode`/`lowerCaseNode` | Transformação | Dois nós Python pequenos | Mantém caminhos explícitos e facilita o estudo. |
| `fallbackNode` | Tratamento de comando desconhecido | Nó Python de fallback | Mantém a mensagem estável e o terceiro caminho observável. |
| `addConditionalEdges` | Roteamento por intenção | Aresta condicional de `StateGraph` | Usa a abstração real de LangGraph; a função retorna um rótulo determinístico. |
| `workflow.compile()` | Preparação do grafo executável | `compile()` | É o fluxo documentado atualmente; a compilação valida a estrutura. |
| `graph.invoke()` | Execução de uma entrada | `invoke()` por requisição | Estado efêmero e resposta determinística, sem checkpointer. |
| Node:test + Fastify inject | Teste de contrato HTTP | pytest + cliente de teste FastAPI | Equivalente idiomático para validar status e corpo sem abrir serviço externo. |
| langgraph.json | Configuração de desenvolvimento do grafo | Não reproduzir automaticamente | O conceito de grafo compilável é preservado; nenhum formato TypeScript é requisito da versão Python. |

### Papel de cada tecnologia

- **Python**: regra textual, tipos de estado, funções dos nós, configuração local e
  composição do serviço.
- **LangGraph**: grafo executável, estado por execução, nós, edges, roteamento
  condicional, compilação e invocação.
- **LangChain**: tipos de mensagens humana/IA que tornam explícito o histórico
  conceitual; não será usado para chamar modelo.
- **FastAPI/Pydantic**: contrato HTTP, parsing e validação de `question`, resposta
  e erros HTTP.
- **Poetry**: metadados, dependências, ambiente e comandos do projeto.
- **LangSmith**: não será dependência obrigatória nem requisito de tracing nesta etapa,
  pois não aparece efetivamente na referência.

### Estado e ciclo de vida

Cada requisição criará um estado novo contendo:

- `messages`: mensagem humana inicial e mensagem de resposta ao final;
- `command`: `uppercase`, `lowercase` ou `unknown`;
- `output`: texto original inicialmente e resultado final após o nó de comando.

O nó de identificação lerá a última mensagem de entrada, normalizará somente para
comparação e definirá `command` e `output`. O roteador lerá `command`. O nó
uppercase, lowercase ou fallback atualizará `output`. O nó de resposta acrescentará a
mensagem de resposta ao histórico conceitual. O endpoint lerá somente `output`, nunca
expondo o estado interno.

### Nós e fluxo

O fluxo será:

```text
START
  ↓
identify_intent
  ↓ (uppercase | lowercase | unknown)
uppercase / lowercase / fallback
  ↓
append_response
  ↓
END
```

Não haverá um nó separado apenas para roteamento, porque a função de roteamento da
aresta condicional é suficiente e corresponde ao comportamento da referência. A função
de identificação testará `upper` antes de `lower`, garantindo a precedência exigida.

### HTTP, validação e erros

- `POST /chat` receberá um corpo JSON com `question: str`.
- O modelo de entrada aplicará mínimo de cinco caracteres.
- Falha de parsing, campo ausente, tipo inválido ou tamanho insuficiente será deixada
  para a validação declarativa da borda FastAPI e resultará em erro HTTP de validação.
- O endpoint invocará o grafo apenas após a entrada ser validada.
- Exceções inesperadas no processamento serão registradas de forma não sensível e
  convertidas em HTTP 500 com resposta sem stack trace ou segredo.
- A resposta bem-sucedida será texto JSON contendo somente o resultado produzido,
  conforme [contracts/chat.md](./contracts/chat.md).

### Dependências e Poetry

Dependências de produção:

- `fastapi`: serviço HTTP e validação integrada;
- `langgraph`: StateGraph, estado, edges, compilação e execução;
- `langchain-core` ou pacote LangChain Python atual que forneça as mensagens
  necessárias: escolher a dependência mínima compatível na implementação.

Dependências de desenvolvimento:

- `pytest`: execução dos testes;
- `httpx`: cliente usado pelo teste HTTP do FastAPI, somente se exigido pelo cliente
  de teste atual.

Não serão adicionados providers de LLM, `langsmith`, banco, servidor alternativo ou
framework de configuração. A versão mínima exata de Python e versões fixadas das
dependências devem ser confirmadas no momento da implementação via documentação oficial
e declaradas no `pyproject.toml`.

### Testes

- **Unitários**: classificação textual, precedência, transformações e preservação de
  espaços, pontuação e acentos; não dependem de FastAPI ou rede.
- **Integração HTTP**: três caminhos principais, caixa variável, entrada exatamente
  com cinco caracteres, campo ausente, tipo inválido, tamanho menor que cinco e
  conversão do erro inesperado em 500.
- **Contrato**: verificar status e corpo observável; não verificar nomes de nós,
  estrutura de arquivos ou detalhes internos.
- **Independência**: nenhum teste precisa de LLM, API key, LangSmith ou serviço externo.

## Phase 0: Research

As decisões e fontes atuais estão consolidadas em [research.md](./research.md).
Não há `NEEDS CLARIFICATION` restante que bloqueie o design. A confirmação da versão
exata de Python e das versões de pacotes será feita como tarefa de implementação, pois
depende do ambiente disponível no momento da execução.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) define o estado, mensagens, comando, pergunta e
  resposta, incluindo validações e transições.
- [contracts/chat.md](./contracts/chat.md) define o contrato observável de `POST /chat`.
- [quickstart.md](./quickstart.md) define a validação local ponta a ponta e os três
  caminhos principais.
- Nenhum arquivo da aplicação foi criado nesta fase.

## Constitution Check — pós-design

- **Escopo**: PASS; somente a baseline da aula foi planejada.
- **Clareza didática**: PASS; os nós e o estado permanecem visíveis.
- **Dependências**: PASS; cada dependência tem justificativa e LangSmith/LLM estão
  excluídos.
- **Testabilidade**: PASS; há testes unitários e HTTP sem serviços externos.
- **Segurança**: PASS; não há credenciais ou persistência.
- **Evolução**: PASS; separação simples permite adicionar capacidades futuras sem
  implementá-las agora.
- **Resultado final**: PASS.

## Complexity Tracking

Nenhuma violação da Constitution requer justificativa.
