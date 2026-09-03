---

description: "Task list for Medical Appointment com LLM"
---

# Tasks: Medical Appointment com LLM

**Input**: Design documents from `specs/004-medical-appointment-llm/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/` and `quickstart.md`

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the foundational phase.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar dependências e configuração segura sem alterar o domínio ou o fluxo ainda.

- [X] T001 Atualizar `pyproject.toml` com a integração LangChain para modelos compatíveis com OpenAI e declarar qualquer loader de `.env` realmente utilizado
- [X] T002 [P] Atualizar `.env.example` com nomes fictícios/valores vazios para `OPENROUTER_API_KEY`, modelo, endpoint, headers, temperatura, timeout e flag de teste real
- [X] T003 [P] Atualizar `README.md` com a configuração do provider, execução sem provider e execução opcional da integração real
- [X] T004 [P] Criar a estrutura de pacotes `src/langchain_intro/prompts/v1/` e `src/langchain_intro/nodes/` com seus `__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar os contratos e fronteiras compartilhados que bloqueiam todos os fluxos de usuário.

**⚠️ CRITICAL**: Nenhuma história deve ser considerada implementada antes desta fase.

- [X] T005 [P] Criar `src/langchain_intro/config.py` com modelo de configuração documentado, leitura de ambiente/.env, defaults seguros e validação sob demanda da API key
- [X] T006 [P] Criar `src/langchain_intro/models.py` com enum/tipo controlado de intenção e modelos Pydantic `IntentExtraction` e `MessageGeneration`, além do protocolo `MedicalLLM` em `llm_service.py`
- [X] T007 [P] Criar `src/langchain_intro/prompts/v1/identify_intent.py` com template puro em português para classificação e extração de dados
- [X] T008 [P] Criar `src/langchain_intro/prompts/v1/message.py` com template puro em português para resposta de sucesso, erro e intenção desconhecida
- [X] T009 [P] Criar testes unitários dos schemas, enum de intenção e configuração sem segredo em `tests/unit/test_llm_schemas.py`
- [X] T057 [P] [US3] Adicionar testes determinísticos em `tests/unit/test_llm_schemas.py` para comprovar, por inspeção da configuração e sem espera real, timeout padrão de 30 segundos quando `LLM_TIMEOUT_SECONDS` estiver ausente, override para 10 segundos quando `LLM_TIMEOUT_SECONDS=10` e rejeição de valor inválido conforme `contracts/llm.md`
- [X] T010 [P] Criar testes unitários dos templates e interpolação de contexto em `tests/unit/test_prompts.py`
- [X] T011 Criar `src/langchain_intro/llm_service.py` com a implementação do serviço real OpenRouter via LangChain e Structured Output Pydantic, incluindo `LLM_TIMEOUT_SECONDS` e tratamento de transporte/parsing (depende de T005 e T006)
- [X] T012 Criar testes unitários do fake e do serviço LLM com doubles do modelo em `tests/unit/test_llm_adapter.py` (depende de T006 e T011)
- [X] T013 Criar `src/langchain_intro/state.py` para definir o `GraphState` final, tipos de campos, reducer de mensagens e função de criação do estado sem chamar o provider durante a importação (depende de T006)
- [X] T014 Criar `src/langchain_intro/factory.py` para composição de `MedicalLLM`, `AppointmentCatalog`, nodes e grafo compilado, mantendo a construção injetável (depende de T005, T006 e T013)
- [X] T015 Atualizar `src/langchain_intro/graph.py` e `langgraph.json` para exportar o grafo compilado pelo caminho CLI existente e delegar sua construção à factory (depende de T014)

**Checkpoint**: contratos, configuração, prompts, serviço injetável e grafo publicável estão prontos para as histórias.

---

## Phase 3: User Story 1 - Agendar consulta por linguagem natural (Priority: P1) 🎯 MVP

**Goal**: Interpretar uma solicitação natural de agendamento, extrair dados estruturados, rotear para o scheduler e confirmar a consulta.

**Independent Test**: Usar fake LLM e catálogo com relógio controlado para executar uma solicitação com profissional, paciente, data/hora e motivo; verificar intenção `schedule`, criação da consulta, caminho `identify_intent → schedule → message` e resposta não vazia.

### Tests for User Story 1

- [X] T016 [P] [US1] Adicionar teste unitário do node de identificação com saída `schedule` e dados extraídos em `tests/unit/test_identify_intent_node.py`
- [X] T017 [P] [US1] Adicionar teste de integração determinística do agendamento completo com fake LLM em `tests/integration/test_schedule_graph.py`
- [X] T018 [P] [US1] Adicionar cenários de contrato HTTP para agendamento bem-sucedido, dado ausente e horário ocupado em `tests/integration/test_medical_chat_endpoint.py`

### Implementation for User Story 1

- [X] T019 [P] [US1] Criar `src/langchain_intro/nodes/identify_intent.py` com chamada ao protocolo LLM, prompt de identificação, normalização do resultado e fallback seguro para `unknown` com erro
- [X] T020 [US1] Criar `src/langchain_intro/nodes/scheduler.py` com validação de `professionalId`, `datetime` e `patientName`, tratamento de `reason` opcional e delegação exclusiva ao `AppointmentCatalog`; dados ausentes não podem chamar o domínio (depende de T013 e T019)
- [X] T021 [US1] Criar `src/langchain_intro/nodes/message.py` com montagem de cenário e chamada estruturada ao serviço LLM, incluindo fallback após sucesso/erro de domínio (depende de T008 e T011)
- [X] T022 [US1] Integrar `identify_intent`, `schedule` e `message` na factory e configurar as edges `START → identify_intent → schedule → message → END` em `src/langchain_intro/factory.py` (depende de T019, T020 e T021)
- [X] T023 [US1] Atualizar `src/langchain_intro/app.py` para normalizar o estado em `MedicalResponse`, preservar 422/500 e não expor detalhes do provider (depende de T022)
- [X] T024 [US1] Completar docstrings e comentários didáticos em português nos arquivos `config.py`, `models.py`, `llm_service.py`, `state.py`, `factory.py` e `nodes/identify_intent.py`

**Checkpoint**: O MVP permite agendamento natural com fake e provider real configurável, mantendo testes offline.

---

## Phase 4: User Story 2 - Cancelar consulta por linguagem natural (Priority: P1)

**Goal**: Interpretar cancelamento, rotear para o canceller, remover somente a consulta correspondente e responder ao usuário.

**Independent Test**: Montar catálogo com uma consulta, usar fake LLM que retorna `cancel`, executar o grafo e verificar remoção, caminho `identify_intent → cancel → message` e confirmação.

### Tests for User Story 2

- [X] T025 [P] [US2] Adicionar testes unitários do canceller para cancelamento correspondente, inexistente e dados incompletos em `tests/unit/test_canceller_node.py`
- [X] T026 [P] [US2] Adicionar teste de integração determinística de cancelamento com fake LLM em `tests/integration/test_cancel_graph.py`
- [X] T027 [P] [US2] Estender `tests/integration/test_medical_chat_endpoint.py` com cancelamento existente e não encontrado conforme `contracts/chat.md`

### Implementation for User Story 2

- [X] T028 [US2] Criar `src/langchain_intro/nodes/canceller.py` com validação de `professionalId`, `datetime` e `patientName`; dados ausentes não podem chamar o `AppointmentCatalog` (depende de T013)
- [X] T029 [US2] Integrar `canceller` e o caminho condicional `cancel → canceller → message` em `src/langchain_intro/factory.py` (depende de T021 e T028)
- [X] T030 [US2] Ajustar `src/langchain_intro/appointment_service.py` somente onde necessário para alinhar serialização, mensagens de erro e contrato de cancelamento ao estado estruturado
- [X] T031 [US2] Completar documentação didática do fluxo de cancelamento em `src/langchain_intro/nodes/canceller.py` e `src/langchain_intro/appointment_service.py`

**Checkpoint**: Agendamento e cancelamento funcionam independentemente com o mesmo serviço de domínio e mensagem final.

---

## Phase 5: User Story 3 - Orientar solicitações desconhecidas (Priority: P1)

**Goal**: Garantir que intenções desconhecidas, ambíguas ou erros de LLM sigam para mensagem sem executar domínio.

**Independent Test**: Usar fake LLM que retorna `unknown` ou falha de parsing e verificar caminho direto para `message`, catálogo inalterado e resposta não vazia.

### Tests for User Story 3

- [X] T032 [P] [US3] Adicionar testes unitários do router para `unknown`, intenção inválida e erro em `tests/unit/test_medical_intent.py`
- [X] T033 [P] [US3] Adicionar testes de fallback do node de mensagem e falha do provider em `tests/unit/test_message_node.py`
- [X] T034 [P] [US3] Adicionar teste de integração determinística para mensagem desconhecida/ambígua sem mutação do catálogo em `tests/integration/test_unknown_graph.py`
- [X] T053 [P] [US3] Adicionar teste unitário determinístico que simule timeout na fronteira do LLM sem aguardar 30 segundos reais e comprove `intent="unknown"`, erro registrado e ausência de chamada ao domínio em `tests/unit/test_llm_timeout.py`

### Implementation for User Story 3

- [X] T035 [US3] Implementar/ajustar `route_medical` em `src/langchain_intro/router.py` e conditional edges na factory para aceitar apenas `schedule`, `cancel` e `message`, enviando erro/unknown diretamente para `message`
- [X] T036 [US3] Ajustar `src/langchain_intro/nodes/identify_intent.py` para rejeitar saída inválida/incompleta sem inferir uma ação de domínio
- [X] T037 [US3] Ajustar `src/langchain_intro/nodes/message.py` para gerar orientação ou erro natural e manter fallback não vazio após falha de geração
- [X] T038 [US3] Atualizar `src/langchain_intro/app.py`, `state.py` e `graph.py` para preservar contrato de erro seguro nos cenários unknown/provider
- [X] T054 [US3] Ajustar o serviço e os nodes para usar `LLM_TIMEOUT_SECONDS=30`, capturar timeout sem derrubar o processo e usar fallback determinístico na mensagem, preservando a distinção entre falha de identificação e dados incompletos (depende de T053)

**Checkpoint**: Todas as três intenções possuem caminho seguro e observável, sem operação indevida.

---

## Phase 6: User Story 4 - Aprender o fluxo por meio do código (Priority: P2)

**Goal**: Tornar o código e a execução suficientemente didáticos para acompanhar entrada → LLM → Structured Output → GraphState → router → domínio → resposta.

**Independent Test**: Revisar os componentes principais, executar a suíte e confirmar que cada fronteira arquitetural possui documentação em português e rastreabilidade por `visited`/estado.

### Tests for User Story 4

- [X] T039 [P] [US4] Adicionar teste contratual da estrutura do grafo, nodes, conditional edges e compatibilidade CLI em `tests/contract/test_langgraph_cli.py`
- [X] T040 [P] [US4] Adicionar teste de isolamento FastAPI/CLI e ausência de provider obrigatório em `tests/contract/test_scope_boundaries.py` e `tests/integration/test_fastapi_independence.py`
- [X] T041 [P] [US4] Adicionar teste opt-in do provider real, marcado `llm_integration`, em `tests/integration/test_openrouter_integration.py`

### Implementation for User Story 4

- [X] T042 [US4] Revisar docstrings de todas as classes, funções e métodos modificados em `src/langchain_intro/`
- [X] T043 [US4] Inserir comentários conceituais sobre LangChain, Structured Output, Pydantic, GraphState, StateGraph, router, conditional edges, DI e domínio nos pontos de decisão de `src/langchain_intro/`
- [X] T044 [US4] Documentar no `README.md` o fluxo, as diferenças em relação ao TypeScript, o modo fake/offline e o teste real opt-in
- [X] T045 [US4] Validar que `../versao-typescript` não sofreu alterações e que `langgraph.json` continua apontando para o grafo compilado em `src/langchain_intro/graph.py:graph`
- [X] T055 [US4] Alinhar a implementação aos módulos canônicos `models.py`, `state.py`, `llm_service.py`, `appointment_service.py`, `factory.py` e `router.py`, atualizando imports, graph, testes e documentação sem alterar a referência TypeScript
- [X] T056 [US4] Criar verificação contratual das docstrings e comentários didáticos em português para classes, métodos, funções e pontos conceituais exigidos em `tests/contract/test_documentation.py`

**Checkpoint**: A feature está funcional e explicável por um estudante, com validação offline e provider real isolado.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar qualidade, segurança, documentação e validação final.

- [X] T046 [P] Executar revisão de segurança de configuração e garantir que API keys não aparecem em `src/`, logs, testes ou artefatos versionados
- [X] T047 [P] Executar revisão de tipagem, imports e docstrings em `src/langchain_intro/`
- [X] T048 [P] Atualizar `poetry.lock` após confirmar as dependências finais em `pyproject.toml`
- [X] T049 Executar `poetry run pytest` e corrigir regressões em `tests/` até a suíte padrão passar sem rede
- [X] T050 Executar os comandos do `quickstart.md`, incluindo validação do LangGraph CLI, em ambiente sem provider
- [X] T051 Executar o teste `llm_integration` somente quando explicitamente habilitado, registrar resultado sem expor credenciais e confirmar que a suíte offline continua independente
- [X] T052 Revisar `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/` e `quickstart.md` contra a implementação final e registrar diferenças em `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: sem dependências.
- **Phase 2 Foundational**: depende da Phase 1 e bloqueia todas as histórias.
- **Phase 3 US1**: depende da Phase 2; é o MVP.
- **Phase 4 US2**: depende da Phase 2 e reutiliza a infraestrutura de US1; pode começar em paralelo após a fundação, mas a integração final depende de T021/T029.
- **Phase 5 US3**: depende da Phase 2 e do contrato do node de mensagem; pode começar em paralelo com US1/US2 após a fundação.
- **Phase 6 US4**: depende dos fluxos implementados e dos contratos públicos.
- **Phase 7 Polish**: depende das histórias desejadas concluídas.

### User Story Dependencies

- **US1 (P1)**: independente após a fundação; MVP recomendado.
- **US2 (P1)**: independente após a fundação, usando o mesmo `MedicalLLM`, `GraphState` e `AppointmentCatalog`.
- **US3 (P1)**: independente após a fundação, mas compartilha `message` e router.
- **US4 (P2)**: depende dos fluxos para documentar e validar o percurso completo.

### Parallel Opportunities

- T002–T004 podem ser executadas em paralelo.
- T005–T010 podem ser executadas em paralelo; T011 depende dos contratos T005/T006.
- T016–T018, T025–T027, T032–T034 e T039–T041 são grupos de testes paralelizáveis por arquivos distintos.
- Após a Phase 2, US1, US2 e US3 podem ser distribuídas em frentes separadas, com atenção às alterações compartilhadas na factory e no node de mensagem.
- T046–T048 podem ser executadas em paralelo antes da validação final.

## Parallel Example: User Story 1

```text
Faixa A: T016 em tests/unit/test_identify_intent_node.py
Faixa B: T017 em tests/integration/test_schedule_graph.py
Faixa C: T018 em tests/integration/test_medical_chat_endpoint.py
Após os testes: T019 → T020/T021 → T022 → T023 → T024
```

## Implementation Strategy

### MVP First (US1 only)

1. Completar Setup e Foundational.
2. Implementar identificação estruturada, scheduler e message.
3. Validar agendamento com fake, API e grafo compilado.
4. Parar no checkpoint de US1 e demonstrar o fluxo antes de adicionar cancelamento e unknown.

### Incremental Delivery

1. Phase 1 + Phase 2 → fronteiras prontas.
2. US1 → agendamento demonstrável.
3. US2 → cancelamento usando o mesmo serviço.
4. US3 → fallback e segurança para entradas fora do domínio.
5. US4 → documentação, CLI e teste real opt-in.
6. Polish → suíte completa, quickstart e revisão final.

## Notes

- Cada tarefa possui checkbox, ID sequencial, marcador `[P]` somente quando aplicável, label de história nas fases de usuário e caminho de arquivo.
- Testes foram incluídos porque a especificação exige testes determinísticos e integração real opcional.
- A implementação deve ser feita somente no projeto Python; `../versao-typescript` permanece somente leitura.
