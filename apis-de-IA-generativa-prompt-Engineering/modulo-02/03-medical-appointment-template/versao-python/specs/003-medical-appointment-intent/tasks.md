# Tasks: Medical Appointment Intent Flow

**Scope**: infraestrutura/template do Módulo 2 herdada; domínio médico do Módulo 3 implementado.
Não há obrigação de preservar upper/lower/fallback ou contratos funcionais anteriores.

## Phase 1: Setup — template técnico herdado

- [X] T001 Confirmar Python 3.13.12, pyenv, Poetry e `.venv` local independente em `pyproject.toml`, `poetry.toml` e comandos do projeto
- [X] T002 [P] Validar imports de FastAPI, LangChain e LangGraph no `.venv` em `tests/contract/test_scope_boundaries.py`
- [X] T003 [P] Validar `langgraph.json` e um único grafo compilado em `tests/contract/test_langgraph_cli.py`
- [X] T004 [P] Registrar instalação, testes, Uvicorn e LangGraph CLI em `README.md`
- [X] T005 Confirmar referência TypeScript somente leitura e registrar fronteira em `research.md`

## Phase 2: Foundational — novo domínio e estado

- [X] T006 Definir modelos validados de profissional e consulta em `src/langchain_intro/appointment.py`
- [X] T007 [P] Definir catálogo determinístico, consultas iniciais e relógio injetável em `src/langchain_intro/appointment.py`
- [X] T008 Definir estado médico tipado, mensagens, intenção e atualizações parciais em `src/langchain_intro/graph.py`
- [X] T009 [P] Definir request/response médicos e erros HTTP em `src/langchain_intro/app.py`
- [X] T010 [P] Atualizar modelo de dados e contrato médico em `specs/003-medical-appointment-intent/data-model.md` e `specs/003-medical-appointment-intent/contracts/chat.md`

## Phase 3: User Story 1 — Agendar consulta (P1) 🎯 MVP

- [X] T011 [P] [US1] Testar busca, validação e normalização de data em `tests/unit/test_appointments.py`
- [X] T012 [P] [US1] Testar disponibilidade, criação, conflito e duplicidade em `tests/unit/test_appointments.py`
- [X] T013 [P] [US1] Testar estado, node e resposta de agendamento em `tests/unit/test_medical_graph.py`
- [X] T014 [P] [US1] Testar contrato HTTP de agendamento em `tests/integration/test_medical_chat_endpoint.py`
- [X] T015 [US1] Implementar resolução e disponibilidade em `src/langchain_intro/appointment.py`
- [X] T016 [US1] Implementar criação atômica e rejeição de conflito em `src/langchain_intro/appointment.py`
- [X] T017 [US1] Implementar node de agendamento em `src/langchain_intro/graph.py`
- [X] T018 [US1] Implementar confirmação e falhas de domínio em `src/langchain_intro/graph.py`
- [X] T019 [US1] Expor agendamento no `POST /chat` em `src/langchain_intro/app.py`

## Phase 4: User Story 2 — Cancelar consulta (P1)

- [X] T020 [P] [US2] Testar correspondência exata de cancelamento em `tests/unit/test_appointments.py`
- [X] T021 [P] [US2] Testar ausência de mutação em cancelamento não encontrado em `tests/unit/test_appointments.py`
- [X] T022 [P] [US2] Testar node e contrato HTTP de cancelamento em `tests/integration/test_medical_chat_endpoint.py`
- [X] T023 [US2] Implementar busca e remoção segura em `src/langchain_intro/appointment.py`
- [X] T024 [US2] Implementar node de cancelamento em `src/langchain_intro/graph.py`
- [X] T025 [US2] Implementar mensagens de confirmação e não encontrado em `src/langchain_intro/graph.py`
- [X] T026 [US2] Integrar cancelamento ao `POST /chat` em `src/langchain_intro/app.py`

## Phase 5: User Story 3 — Identificar e rotear intenção (P1)

- [X] T027 [P] [US3] Testar schedule, cancel, unknown, acentos e conflitos em `tests/unit/test_medical_intent.py`
- [X] T028 [P] [US3] Testar extração/validação médica em `tests/unit/test_medical_graph.py`
- [X] T029 [P] [US3] Testar topologia e edges condicionais em `tests/contract/test_langgraph_cli.py`
- [X] T030 [P] [US3] Testar unknown e validação HTTP em `tests/integration/test_medical_chat_endpoint.py`
- [X] T031 [US3] Implementar identificação e extração no estado médico em `src/langchain_intro/graph.py`
- [X] T032 [US3] Implementar START, nodes, edges e roteamento condicional em `src/langchain_intro/graph.py`
- [X] T033 [US3] Implementar node convergente de resposta LangChain em `src/langchain_intro/graph.py`
- [X] T034 [US3] Publicar o grafo médico compilado em `src/langchain_intro/graph.py` e `langgraph.json`
- [X] T035 [US3] Adaptar `POST /chat` sem contrato textual legado em `src/langchain_intro/app.py`

## Phase 6: Polish — documentação e validação

- [X] T036 [P] Atualizar README com objetivo, fluxo, contrato e distinção template/domínio em `README.md`
- [X] T037 [P] Registrar equivalências TypeScript → Python em `specs/003-medical-appointment-intent/research.md`
- [X] T038 [P] Atualizar quickstart sem referências funcionais ao Módulo 2 em `specs/003-medical-appointment-intent/quickstart.md`
- [X] T039 Executar suíte unitária, HTTP e CLI sem credenciais em `tests/`
- [X] T040 Confirmar escopo médico, infraestrutura herdada e referência TypeScript intacta em `specs/003-medical-appointment-intent/`

## Dependencies and Strategy

T001–T005 precedem T006–T010; a fundação precede as três histórias. US1 é o MVP, US2 reutiliza o
catálogo e US3 integra o roteamento. Testes de cada história podem ser preparados em paralelo.
Após US3, atualizar documentação, executar a suíte e validar o escopo.
