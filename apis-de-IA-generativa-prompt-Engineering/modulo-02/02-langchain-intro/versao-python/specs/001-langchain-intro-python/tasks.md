---
description: "Task list for LangChain Intro Python"
---

# Tasks: LangChain Intro Python

**Input**: Design documents from `specs/001-langchain-intro-python/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/chat.md`, `quickstart.md`

**Tests**: Incluídos porque a especificação exige validação automatizada de todos os
comportamentos relevantes. Nenhum teste dependerá de LLM, API key, LangSmith ou serviço
externo.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configurar o projeto Python com Poetry e a estrutura mínima da aplicação.

- [X] T001 Criar `pyproject.toml` com metadados do projeto, Python 3.11+ e dependências de produção FastAPI, LangGraph e a dependência mínima atual de mensagens LangChain (FR-015, NFR-006).
- [X] T002 Adicionar pytest e o cliente de teste HTTP necessário como dependências de desenvolvimento em `pyproject.toml`, sem adicionar provider de LLM ou `langsmith` (NFR-004, NFR-006).
- [X] T003 Gerar e validar `poetry.lock` a partir do `pyproject.toml`, confirmando instalação reprodutível pelo ambiente Poetry (FR-014, NFR-003).
- [X] T004 [P] Criar a estrutura inicial `src/langchain_intro/__init__.py`, `tests/unit/` e `tests/integration/` sem criar camadas não previstas no plano (Princípios I, II e XIII).
- [X] T005 [P] Configurar o layout de importação do pacote em `pyproject.toml` e documentar o comando base de testes em `README.md` (FR-014, NFR-003).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar os conceitos compartilhados de pergunta, mensagens e estado; bloqueia
todas as histórias.

**⚠️ CRITICAL**: Nenhuma tarefa de User Story começa antes desta fase.

- [X] T006 Definir o tipo de comando e o estado tipado com `messages`, `command` e `output` em `src/langchain_intro/graph.py`, sem persistência ou checkpointer (FR-010, data-model.md).
- [X] T007 Implementar a criação da mensagem humana inicial e a mensagem de resposta no histórico conceitual em `src/langchain_intro/messages.py`, usando os tipos atuais de mensagem LangChain (FR-010, data-model.md).
- [X] T008 [P] Criar testes unitários da inicialização do estado e das mensagens em `tests/unit/test_state.py`, verificando mensagem de entrada, saída inicial e ausência de memória entre execuções (FR-010, NFR-001).
- [X] T009 Definir a constante da mensagem de fallback em `src/langchain_intro/graph.py` ou arquivo didático equivalente, mantendo exatamente o texto do contrato `contracts/chat.md` (FR-008, AC-003).
- [X] T010 [P] Criar `.env.example` sem credenciais, somente se a execução precisar de variáveis opcionais, e registrar a ausência de API keys obrigatórias em `README.md` (FR-014, NFR-005).

**Checkpoint**: Poetry instala o ambiente, o estado é representável e as mensagens são
efêmeras; as histórias podem ser implementadas sem infraestrutura adicional.

---

## Phase 3: User Story 1 - Transformar texto para maiúsculas (Priority: P1) 🎯 MVP

**Goal**: Entregar o primeiro incremento funcional: reconhecer `upper`, transformar a
pergunta inteira em maiúsculas e demonstrar o caminho principal do grafo.

**Independent Test**: Executar os testes unitários de identificação/transformação e um
teste HTTP com uma pergunta válida contendo `upper`; o resultado deve ser o texto
completo em maiúsculas e status 200.

### Tests for User Story 1

- [X] T011 [P] [US1] Criar testes unitários de identificação case-insensitive e precedência de `upper` em `tests/unit/test_intent.py`, cobrindo `upper` isolado, variações de caixa e presença simultânea de `upper`/`lower` (FR-004, FR-005, FR-009, AC-004, AC-005).
- [X] T012 [P] [US1] Criar testes unitários da transformação uppercase em `tests/unit/test_transformations.py`, verificando texto completo, espaços, pontuação e acentos (FR-006, AC-001, AC-007).
- [X] T013 [US1] Criar teste de contrato HTTP para `POST /chat` com `upper` em `tests/integration/test_chat_endpoint.py`, verificando status 200 e resposta textual conforme `contracts/chat.md` (FR-001, FR-012, AC-001).

### Implementation for User Story 1

- [X] T014 [US1] Implementar o nó de identificação determinística em `src/langchain_intro/graph.py`, comparando em caixa normalizada, preservando `output` original e aplicando `upper` antes de `lower` (FR-004, FR-005, FR-009).
- [X] T015 [US1] Implementar o nó uppercase em `src/langchain_intro/graph.py`, convertendo somente a caixa de `output` e preservando espaços, pontuação e acentos (FR-006, AC-007).
- [X] T016 [US1] Criar o roteador condicional `uppercase | lowercase | unknown` e o grafo mínimo com `START`, nó de identificação, caminho uppercase e `END` em `src/langchain_intro/graph.py`, usando `StateGraph`, edge condicional, `compile()` e `invoke()` (FR-010, FR-011, plano: State/Node/Conditional Edge/Compile/Invoke).
- [X] T017 [US1] Criar a aplicação FastAPI e o modelo de request em `src/langchain_intro/app.py`, declarando `question` obrigatório e com mínimo de cinco caracteres para preparar o contrato `POST /chat` (FR-001, FR-002, FR-003).
- [X] T018 [US1] Conectar `POST /chat` ao grafo compilado em `src/langchain_intro/app.py`, retornando somente `output` e mantendo o estado interno fora da resposta (FR-012, FR-015).
- [X] T019 [US1] Executar os testes de US1 e ajustar somente o necessário para que o caminho uppercase fique demonstrável sem serviço externo (AC-001, AC-004, AC-005, AC-008).

**Checkpoint**: O MVP aceita uma pergunta válida com `upper`, percorre State → Node →
Conditional Edge → Node → Response e retorna o texto em maiúsculas.

---

## Phase 4: User Story 2 - Transformar texto para minúsculas (Priority: P1)

**Goal**: Adicionar o caminho `lower` preservando o caminho uppercase e a precedência
determinística.

**Independent Test**: Executar teste unitário e teste HTTP com `lower` em caixa variável;
a resposta deve ser a pergunta inteira em minúsculas, sem quebrar US1.

### Tests for User Story 2

- [X] T020 [P] [US2] Adicionar testes unitários de reconhecimento case-insensitive e transformação lowercase em `tests/unit/test_transformations.py`, incluindo espaços, pontuação e acentos (FR-005, FR-007, AC-002, AC-004, AC-007).
- [X] T021 [US2] Adicionar teste HTTP do caminho lowercase em `tests/integration/test_chat_endpoint.py`, verificando status 200 e corpo textual (FR-001, FR-012, AC-002).

### Implementation for User Story 2

- [X] T022 [US2] Implementar o nó lowercase em `src/langchain_intro/graph.py`, convertendo `output` integralmente para minúsculas sem alterar os demais caracteres (FR-007, AC-007).
- [X] T023 [US2] Conectar o rótulo `lowercase` do roteamento condicional ao nó lowercase e ao nó de resposta em `src/langchain_intro/graph.py`, preservando o caminho uppercase (FR-007, FR-009, FR-011).
- [X] T024 [US2] Executar os testes de US1 e US2 e corrigir regressões somente em `src/langchain_intro/graph.py` ou nos testes correspondentes (AC-001, AC-002, AC-004, AC-005).

**Checkpoint**: Os caminhos uppercase e lowercase funcionam independentemente através do
mesmo contrato HTTP e do mesmo grafo.

---

## Phase 5: User Story 3 - Orientar comandos desconhecidos (Priority: P1)

**Goal**: Completar o terceiro caminho do grafo com fallback determinístico para perguntas
sem comando reconhecido.

**Independent Test**: Enviar uma pergunta válida sem `upper` nem `lower` e verificar
status 200 com a mensagem de fallback exata.

### Tests for User Story 3

- [X] T025 [P] [US3] Criar teste unitário do comando `unknown` e da mensagem de fallback em `tests/unit/test_intent.py`, incluindo texto válido com espaços (FR-008, AC-003).
- [X] T026 [US3] Adicionar teste HTTP do fallback em `tests/integration/test_chat_endpoint.py`, verificando status 200 e mensagem exata (FR-008, FR-012, AC-003).

### Implementation for User Story 3

- [X] T027 [US3] Implementar o nó fallback em `src/langchain_intro/graph.py`, definindo `output` como a mensagem contratada e mantendo o histórico conceitual válido (FR-008, FR-010).
- [X] T028 [US3] Conectar o rótulo `unknown` ao nó fallback e ao nó de resposta em `src/langchain_intro/graph.py`, encerrando o fluxo em `END` (FR-008, FR-011).
- [X] T029 [US3] Executar os testes das três histórias e confirmar a precedência `upper > lower` em `tests/unit/test_intent.py` e `tests/integration/test_chat_endpoint.py` (FR-009, AC-005).

**Checkpoint**: Os três caminhos da referência TypeScript estão disponíveis e testáveis
pelo mesmo endpoint.

---

## Phase 6: Validation, Errors & Cross-Cutting Tests

**Purpose**: Completar validação, tratamento de erros, documentação e verificação final
dos contratos sem adicionar funcionalidades fora do escopo.

- [X] T030 [P] Criar testes HTTP de entrada inválida em `tests/integration/test_chat_endpoint.py` para campo ausente, tipo inválido e texto com menos de cinco caracteres, confirmando rejeição antes do grafo (FR-002, FR-003, FR-013, AC-006).
- [X] T031 [P] Adicionar testes HTTP para entrada com exatamente cinco caracteres e para preservação de espaços, pontuação e acentos em `tests/integration/test_chat_endpoint.py` (FR-003, AC-007).
- [X] T032 [P] Adicionar teste de erro inesperado em `tests/integration/test_chat_endpoint.py`, isolando uma falha controlada do processamento e verificando HTTP 500 sem stack trace ou segredo (FR-013, NFR-005).
- [X] T033 Implementar tratamento de exceção inesperada e logging não sensível em `src/langchain_intro/app.py`, convertendo falhas do grafo em HTTP 500 sem duplicar validação do modelo de request (FR-013, NFR-005).
- [X] T034 Atualizar `README.md` com pré-requisitos, instalação via Poetry, execução local, exemplos dos três caminhos, comando de testes e explicação State → Nodes → Conditional Edge → Response (FR-014, NFR-003, SC-004).
- [X] T035 [P] Registrar em `README.md` a diferença TypeScript → Python: Fastify para FastAPI, Zod para modelo tipado, mensagens LangChain atuais e StateGraph Python; explicar que não há LLM nem LangSmith obrigatório (Princípios VI, VII, XII).
- [X] T036 Executar o quickstart documentado e a suíte completa com `poetry run pytest`, validando SC-001, SC-002, SC-003 e SC-005 em ambiente local sem serviços externos (SC-001 a SC-005).
- [X] T037 Comparar a implementação Python com `../versao-typescript` usando os contratos, testes e fluxo registrados em `specs/001-langchain-intro-python/contracts/chat.md`, documentando qualquer diferença restante em `README.md` (FR-015, AC-010, Princípios IX, XII e XV).
- [X] T038 Revisar `pyproject.toml`, `README.md`, `src/` e `tests/` contra `.specify/memory/constitution.md`, confirmando Python idiomático, Poetry, FastAPI, simplicidade, ausência de LLM/LangSmith obrigatório, configuração segura, testes e escopo controlado (NFR-006, SC-006).

**Checkpoint final**: A baseline local executa, expõe `POST /chat), cobre os três
caminhos e as bordas, preserva a referência conceitualmente e está pronta para a
próxima etapa sem implementar recursos futuros.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 — Setup**: sem dependências; cria o ambiente e o layout.
- **Phase 2 — Foundational**: depende da Phase 1 e bloqueia todas as histórias.
- **Phase 3 — US1**: depende da Phase 2; entrega o MVP.
- **Phase 4 — US2**: depende da Phase 3 para reutilizar o grafo e preservar US1.
- **Phase 5 — US3**: depende da Phase 4 para completar o roteamento e validar todos os caminhos.
- **Phase 6 — Validation**: depende de US1, US2 e US3; fecha erros, documentação e governança.

### User Story Dependencies

- **US1 (uppercase)**: depende somente da fundação; é o MVP.
- **US2 (lowercase)**: depende da fundação e do grafo criado por US1.
- **US3 (fallback)**: depende do grafo e da rota estabelecidos por US1/US2.
- As histórias não são paralelas entre si porque compartilham `graph.py` e o contrato
  HTTP; os testes unitários distintos podem ser preparados em paralelo quando não
  alterarem o mesmo arquivo.

### Within Each User Story

- Testes específicos são criados antes da implementação do comportamento.
- Estado e mensagens precedem os nós.
- Nós precedem edges e compilação.
- Grafo compilado precede a integração completa da rota.
- Cada checkpoint deve passar antes da fase seguinte.

### Parallel Opportunities

- **Setup**: T004 e T005 podem ser executadas em paralelo após T001/T002.
- **Foundation**: T008 e T010 podem ser executadas em paralelo após T006/T007/T009.
- **US1**: T011 e T012 podem ser executadas em paralelo; T013 pode ser preparado em
  paralelo, mas depende do contrato de teste escolhido.
- **US2**: T020 e T021 podem ser preparados em paralelo.
- **US3**: T025 e T026 podem ser preparados em paralelo.
- **Validation**: T030, T031, T032 e T035 podem ser executadas em paralelo após as
  implementações dos caminhos; T034 depende do comportamento final documentado.

## Parallel Example: User Story 1

```text
Após Phase 2:
- T011: testes de identificação e precedência em tests/unit/test_intent.py
- T012: testes de transformação em tests/unit/test_transformations.py
- T013: teste HTTP uppercase em tests/integration/test_chat_endpoint.py

Depois dos testes:
- T014/T015: nós de identificação e uppercase em src/langchain_intro/graph.py
- T017: modelo de request e aplicação inicial em src/langchain_intro/app.py
```

## Implementation Strategy

### MVP First

1. Completar Setup e Foundation.
2. Implementar US1, incluindo teste unitário e contrato HTTP.
3. Executar o checkpoint do MVP e validar o caminho uppercase.
4. Só então adicionar US2 e US3.

### Incremental Delivery

1. US1 entrega o primeiro caminho e a forma básica do grafo.
2. US2 adiciona lowercase sem quebrar uppercase.
3. US3 adiciona fallback e fecha o comportamento funcional.
4. A fase final adiciona validação de borda, documentação e revisão constitucional.

### Final Definition of Done

- Todas as tarefas T001–T038 concluídas.
- `poetry install` e `poetry run pytest` executam localmente.
- `POST /chat` atende o contrato em `contracts/chat.md`.
- Uppercase, lowercase, fallback, precedência, validações e HTTP 500 estão testados.
- Nenhum LLM, provider, LangSmith obrigatório, persistência ou funcionalidade futura foi adicionado.
- `../versao-typescript` permanece inalterado.

