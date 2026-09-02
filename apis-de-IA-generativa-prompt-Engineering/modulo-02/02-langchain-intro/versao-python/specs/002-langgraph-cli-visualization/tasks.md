---

description: "Task list for LangGraph CLI support and graph visualization"
---

# Tasks: Suporte ao LangGraph CLI e visualização do grafo

**Input**: Design documents from `specs/002-langgraph-cli-visualization/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Included because the feature specification and user explicitly require validation of CLI loading, graph structure, behavior, FastAPI continuity, dependency compatibility, and unchanged TypeScript reference.

**Organization**: Tasks are grouped by user story. Shared setup/foundation tasks precede story work; each story has an independent test and checkpoint.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing baseline and prepare Poetry-managed CLI support without changing the graph or the TypeScript reference.

- [X] T001 Inventory the baseline entrypoint, graph object, FastAPI route, tests, Python pin, and current dependency constraints in `src/langchain_intro/graph.py`, `src/langchain_intro/app.py`, `tests/`, `.python-version`, and `pyproject.toml` (FR-003, FR-005, FR-015, FR-022)
- [X] T002 Add the current compatible `langgraph-cli[inmem]` dependency to the Poetry development dependency declaration in `pyproject.toml` and regenerate `poetry.lock` without adding an LLM provider or direct LangSmith dependency (FR-001, FR-004, FR-014; AC-001, AC-013)
- [X] T003 Validate the resolved dependency set with Python 3.13.12 selected by pyenv and Poetry using `.python-version`, `pyproject.toml`, and `poetry.lock`; record any compatibility constraint in `specs/002-langgraph-cli-visualization/research.md` (FR-005; AC-001, AC-003)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared CLI configuration and reusable validation helpers before story-specific verification.

**⚠️ CRITICAL**: User story tasks depend on this phase.

- [X] T004 Create the root `langgraph.json` with the official current `dependencies`, `graphs`, and environment configuration, mapping a stable graph name to `./src/langchain_intro/graph.py:graph` and avoiding provider credentials (FR-002, FR-003, FR-014; AC-001, AC-002, AC-013)
- [X] T005 [P] Add shared configuration/entrypoint assertions in `tests/contract/test_langgraph_cli.py` for valid JSON, required keys, the exact existing graph path, and absence of LLM/provider/API-key/LangSmith requirements (FR-002, FR-003, FR-014, FR-021; AC-001, AC-002, AC-013)

**Checkpoint**: `langgraph.json` and the Poetry dependency are defined; story validation can begin.

---

## Phase 3: User Story 1 - Iniciar e visualizar o grafo (Priority: P1) 🎯 MVP

**Goal**: Allow a student to start LangGraph Dev, load the existing compiled graph, and inspect the workflow through the official development interface.

**Independent Test**: From a Poetry-installed Python 3.13.12 environment, run `poetry run langgraph dev`, verify startup has no configuration error, and confirm the loaded graph exposes the expected workflow structure.

### Tests for User Story 1

- [X] T006 [P] [US1] Add graph-loading and node-structure tests in `tests/contract/test_langgraph_cli.py` that import the configured entrypoint, confirm it is the existing compiled graph, and assert `identify_intent`, `uppercase`, `lowercase`, `fallback`, and `append_response` are represented (FR-007, FR-008; AC-002, AC-005)
- [X] T007 [P] [US1] Add a controlled CLI startup test in `tests/integration/test_langgraph_dev.py` that launches `poetry run langgraph dev`, waits for the documented local readiness signal with a timeout, captures configuration errors, and terminates the process safely (FR-006, FR-021; AC-003, AC-004)

### Implementation and validation for User Story 1

- [X] T008 [US1] Implement the minimum `langgraph.json`/Poetry integration required for the tests in `langgraph.json`, `pyproject.toml`, and `poetry.lock`, preserving `src/langchain_intro/graph.py:graph` as the sole entrypoint (FR-003, FR-004, FR-006, FR-007)
- [X] T009 [P] [US1] Document installation, `poetry run langgraph dev`, the official development URL/interface, `langgraph.json` graph discovery, and the visual correspondence between Python nodes/edges and the workflow in `README.md` (FR-016, FR-017, FR-018, FR-019, FR-020; AC-004, AC-012)
- [X] T010 [US1] Run the independent User Story 1 validation from `tests/contract/test_langgraph_cli.py`, `tests/integration/test_langgraph_dev.py`, and `specs/002-langgraph-cli-visualization/quickstart.md`; confirm the five nodes and conditional branches are visible/loadable without LLM credentials (FR-008, FR-009, FR-014; AC-004, AC-005, AC-006, AC-013)

**Checkpoint**: `poetry run langgraph dev` starts and loads the same five-node workflow documented in the code.

---

## Phase 4: User Story 2 - Explorar os caminhos do workflow (Priority: P1)

**Goal**: Demonstrate the conditional routing and preserve uppercase, lowercase, and fallback behavior when executed through the development environment.

**Independent Test**: Execute representative uppercase, lowercase, and unknown inputs against the loaded graph, inspect the visited paths, and compare final outputs with direct baseline `graph.invoke()` results.

### Tests for User Story 2

- [X] T011 [P] [US2] Add conditional-edge structure assertions in `tests/contract/test_langgraph_cli.py` for `identify_intent` routing to uppercase, lowercase, and fallback, with each branch converging on `append_response` and then `END` (FR-009, FR-021; AC-006)
- [X] T012 [P] [US2] Add deterministic execution comparisons in `tests/integration/test_langgraph_dev.py` for uppercase, lowercase, and fallback inputs, including the exact fallback message and parity with `graph.invoke(create_initial_state(...))` (FR-010, FR-011, FR-012, FR-013; AC-007, AC-008, AC-009)

### Implementation and validation for User Story 2

- [X] T013 [US2] Exercise the configured graph execution path through the LangGraph Dev validation flow without modifying `src/langchain_intro/graph.py`; preserve the existing node names, routing map, transformations, and fallback constant (FR-007, FR-009, FR-010, FR-011, FR-012, FR-013)
- [X] T014 [US2] Run the three-path validation documented in `specs/002-langgraph-cli-visualization/quickstart.md` and record expected node paths and outputs in `tests/integration/test_langgraph_dev.py` (FR-010, FR-011, FR-012, FR-013; AC-006, AC-007, AC-008, AC-009)

**Checkpoint**: All three conditional paths produce the same results through LangGraph Dev and direct baseline invocation.

---

## Phase 5: User Story 3 - Continuar usando a aplicação existente (Priority: P1)

**Goal**: Preserve FastAPI and `POST /chat` as an independent application mode while LangGraph Dev remains complementary.

**Independent Test**: Run the existing HTTP integration suite with LangGraph Dev stopped, then run both local processes separately and confirm the endpoint contract remains unchanged.

### Tests for User Story 3

- [X] T015 [P] [US3] Add an independence regression test in `tests/integration/test_chat_endpoint.py` or a focused companion test that starts FastAPI without `langgraph dev` and verifies `POST /chat` still returns uppercase, lowercase, fallback, validation, and error-contract results (FR-015, FR-021, FR-022; AC-010, AC-011)
- [X] T016 [P] [US3] Add a compatibility/static regression test in `tests/contract/test_langgraph_cli.py` that confirms no graph implementation changes are required by the CLI and no source under `../versao-typescript` is modified (FR-007, FR-022; AC-002, AC-010)

### Implementation and validation for User Story 3

- [X] T017 [US3] Update `README.md` to clearly separate FastAPI/Uvicorn as the HTTP application mode from LangGraph Dev as the graph development/visualization mode, including independent startup commands and `POST /chat` examples (FR-015, FR-017, FR-020; AC-011, AC-012)
- [X] T018 [US3] Execute the pre-existing unit and integration tests in `tests/unit/` and `tests/integration/test_chat_endpoint.py` unchanged, and resolve only compatibility issues caused by the new CLI dependency without altering existing API behavior (FR-010, FR-015, FR-022; AC-010, AC-011)

**Checkpoint**: FastAPI remains independently operational and the existing test suite passes with the CLI installed.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Complete documentation, verify exclusions, and perform the required final constitutional review.

- [X] T019 [P] Run the complete validation sequence from `specs/002-langgraph-cli-visualization/quickstart.md`, including Python/pyenv/Poetry compatibility, `poetry run pytest`, `poetry run langgraph dev`, graph loading, visual inspection, and the three execution paths (FR-005, FR-006, FR-016, FR-021; AC-003, AC-004, AC-010, AC-012)
- [X] T020 [P] Verify with `pyproject.toml`, `poetry.lock`, `langgraph.json`, and the source tree that no mandatory LLM, provider, API key, direct LangSmith, RAG, agent, tool, persistent-memory, database, or uv dependency was introduced (FR-014; AC-013)
- [X] T021 [P] Verify the TypeScript reference remains unchanged by comparing the working tree/content under `../versao-typescript` before and after implementation, and document the result in `specs/002-langgraph-cli-visualization/quickstart.md` or the implementation handoff (FR-022)
- [X] T022 Perform the final constitutional validation against `.specify/memory/constitution.md`, `specs/002-langgraph-cli-visualization/spec.md`, and `specs/002-langgraph-cli-visualization/plan.md`; explicitly confirm principles I–XVII, scope control, testability, documentation, Poetry, Python, FastAPI preservation, and no TypeScript changes before marking the feature complete (FR-004, FR-005, FR-015, FR-022; AC-010, AC-011, AC-012)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately; T002 depends on T001, and T003 depends on T002.
- **Phase 2 (Foundational)**: T004 depends on T002/T003; T005 can be prepared after T001 but must pass after T004.
- **Phase 3 (US1 MVP)**: depends on T004 and T005; T006/T007 are tests-first and T008/T009 implement/configure what they verify; T010 is the story checkpoint.
- **Phase 4 (US2)**: depends on US1 loading success, especially T010; T011/T012 precede T013/T014.
- **Phase 5 (US3)**: functionally independent of US1/US2 after Foundation; T015/T016 precede T017/T018 where applicable.
- **Phase 6 (Polish)**: depends on all desired story checkpoints, T010, T014, and T018.

### User Story Dependencies

- **US1 (P1)**: no dependency on another story after Foundation; it is the MVP.
- **US2 (P1)**: depends on US1 because it validates execution through the loaded CLI graph.
- **US3 (P1)**: functionally independent of US1/US2; it depends only on the shared baseline and can run in parallel after Foundation.

### Parallel Opportunities

- After T001, T005 can be drafted in parallel with T002, but its final assertions depend on T004.
- T006 and T007 can run in parallel because they target separate test concerns.
- T009 can run in parallel with T006/T007 after the configuration contract is agreed.
- T011 and T012 can run in parallel after US1 loading is available.
- T015 and T016 can run in parallel with US2 work because they validate separate files/contracts.
- T019, T020, and T021 can run in parallel after implementation; T022 is the final gate after their results are available.

### Dependency Graph

```text
T001 → T002 → T003 → T004 → T005
                         ├── T006 ─┐
                         ├── T007 ─┼→ T008/T009 → T010
                         └────────┘       │
                                          └→ T011/T012 → T013 → T014
                         └→ T015/T016 → T017/T018
T010 + T014 + T018 → T019/T020/T021 → T022
```

---

## Traceability Matrix

| Requirement/AC group | Tasks |
|---|---|
| CLI dependency, Poetry, Python, pyenv: FR-001, FR-004, FR-005; AC-001, AC-003 | T001–T003, T019 |
| Root configuration and existing graph entrypoint: FR-002, FR-003, FR-007; AC-001, AC-002 | T004–T008, T010 |
| CLI startup and visualization: FR-006, FR-008, FR-016, FR-018–FR-020; AC-003–AC-005, AC-012 | T006–T010, T017, T019 |
| Conditional routing and functional parity: FR-009–FR-013; AC-006–AC-009 | T011–T014, T019 |
| No LLM/provider/API key/LangSmith: FR-014; AC-013 | T002, T005, T006, T020 |
| FastAPI and `POST /chat`: FR-015; AC-011 | T015, T017, T018, T019 |
| Existing tests and TypeScript preservation: FR-021, FR-022; AC-010 | T015, T016, T018, T021 |
| Final constitutional validation | T022 |

---

## Parallel Example: MVP / User Story 1

```text
After T004 is available:
  Worker A: T006 graph-loading and node-structure tests
  Worker B: T007 CLI startup subprocess test
  Worker C: T009 README LangGraph Dev documentation

Then:
  Worker A/B: T008 configuration/dependency implementation adjustments
  Coordinator: T010 independent MVP validation
```

## Parallel Example: Remaining Stories

```text
After T010:
  Worker A: T011 conditional-edge assertions
  Worker B: T012 execution parity tests
  Worker C: T015 FastAPI independence regression
  Worker D: T016 TypeScript/source-boundary regression
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundation (T001–T005).
2. Complete US1 (T006–T010).
3. Stop and validate `poetry run langgraph dev`, graph loading, five nodes, and visual workflow.

### Incremental Delivery

1. Add US2 and validate the three routes against direct `graph.invoke()`.
2. Add US3 and confirm FastAPI/`POST /chat` regression safety.
3. Run cross-cutting exclusions, quickstart, and constitutional validation.

### Notes

- Every task uses the required checklist format: checkbox, sequential ID, optional `[P]`, story label in story phases, and an explicit file path.
- No implementation is performed by this task-generation step; `tasks.md` only defines work for the later implementation phase.
- The task list deliberately does not include modifications to `../versao-typescript`.
