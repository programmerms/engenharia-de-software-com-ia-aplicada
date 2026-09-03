# Implementation Plan: Medical Appointment com LLM

**Branch**: `004-medical-appointment-llm` | **Date**: 2026-09-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-medical-appointment-llm/spec.md`

## Summary

A evolução substituirá a classificação e a mensagem determinísticas por dois usos controlados de LLM: extração de intenção/dados e geração da resposta final. O LLM será encapsulado em serviço próprio, configurado por ambiente para usar OpenRouter, e suas respostas serão validadas por modelos Pydantic. O LangGraph continuará sendo a orquestração: o resultado estruturado será gravado no `GraphState`, um router escolherá `scheduler`, `canceller` ou `message`, e o serviço de domínio continuará responsável pelos efeitos em memória. Doubles injetáveis manterão os testes locais determinísticos.

## Technical Context

**Language/Version**: Python 3.13.12, compatível com Python 3.13.x

**Primary Dependencies**: Poetry, FastAPI, Uvicorn, LangChain Core, integração LangChain OpenAI, LangGraph, Pydantic, pytest, HTTPX e LangGraph CLI. A integração OpenAI-compatible será adicionada somente se ainda não estiver disponível.

**Storage**: Catálogo de consultas em memória, sem banco de dados ou persistência entre processos.

**Testing**: pytest para unidades, contratos e integração determinística; HTTPX/TestClient para FastAPI; teste do provider real separado e opt-in por variável de ambiente.

**Target Platform**: Serviço Python executado localmente com Poetry; servidor FastAPI e LangGraph CLI.

**Project Type**: Serviço web didático com grafo executável também pelo LangGraph CLI.

**Performance Goals**: Responder dentro do timeout configurado do provider; testes determinísticos sem latência de rede.

**Constraints**: Sem API key ou rede nos testes padrão; segredos somente em ambiente; falha de parsing/provider não pode executar domínio; sem alteração em `../versao-typescript`; documentação em português.

**Scale/Scope**: Uma API `/chat`, três intenções controladas, dois fluxos de domínio e duas chamadas estruturadas de LLM por execução quando aplicável.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates aprovados antes da pesquisa:

- **Princípios I, II, VI e XIII**: desenho incremental, didático e idiomático em Python; não copia a estrutura TypeScript.
- **Princípios III, IV, V e VII**: preserva Poetry, FastAPI, LangChain/LangGraph e prevê documentação atual antes da implementação.
- **Princípios VIII, XV e XVI**: não inclui banco, RAG ou novas funcionalidades e mantém `../versao-typescript` como referência somente leitura.
- **Princípios X e XI**: usa ambiente para credenciais e mantém testes determinísticos e isolados.
- **Princípios XII, XIV e XVII**: exige documentação das diferenças, dependências declaradas, configuração, testes e validação final.

Não há violação constitucional que exija exceção.

## Project Structure

### Documentation (this feature)

```text
specs/004-medical-appointment-llm/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── chat.md
│   └── llm.md
└── tasks.md                 # criado posteriormente por $speckit-tasks
```

### Source Code (repository root)

```text
src/
└── langchain_intro/
    ├── __init__.py
    ├── app.py                 # API FastAPI e contrato HTTP
    ├── config.py              # configuração de ambiente e modelo
    ├── models.py              # schemas Pydantic e contratos estruturados
    ├── state.py               # GraphState e tipos do fluxo
    ├── llm_service.py         # protocolo e serviço LangChain/OpenRouter
    ├── prompts/
    │   └── v1/
    │       ├── identify_intent.py
    │       └── message.py
    ├── nodes/
    │   ├── __init__.py
    │   ├── identify_intent.py
    │   ├── scheduler.py
    │   ├── canceller.py
    │   └── message.py
    ├── graph.py               # grafo compilado publicado
    ├── factory.py              # composição e compilação
    ├── router.py               # roteamento condicional seguro
    ├── appointment_service.py  # domínio em memória
    ├── messages.py            # histórico LangChain
    └── run.py

tests/
├── contract/
├── integration/
└── unit/

.env.example
langgraph.json
pyproject.toml
```

**Structure Decision**: Manter o pacote `langchain_intro` e a API existentes, introduzindo módulos explícitos para modelos, estado, router, prompts, nodes e serviços. `factory.py` concentra composição/DI e `graph.py` publica o grafo compilado; `appointment_service.py` permanece independente do LLM. Essa organização torna visível o caminho didático e permite substituir o LLM real por um fake sem alterar regras de domínio.

### Nomenclatura canônica

| Papel | Arquivo | Função, classe ou node canônico |
|---|---|---|
| Node de identificação | `nodes/identify_intent.py` | `identify_intent` |
| Node de agendamento | `nodes/scheduler.py` | `schedule` |
| Node de cancelamento | `nodes/canceller.py` | `cancel` |
| Node de mensagem | `nodes/message.py` | `message` |
| Serviço de LLM | `llm_service.py` | `MedicalLLM` e implementação OpenRouter |
| Serviço de domínio | `appointment_service.py` | `AppointmentCatalog` |
| Grafo | `graph.py` | grafo compilado exportado |
| Factory | `factory.py` | construção/injeção do `StateGraph` |
| Router | `router.py` | `route_medical` |
| Modelos | `models.py` | `IntentExtraction`, `MessageGeneration` |
| Estado | `state.py` | `GraphState` |

## Component Design

### Configuration

`config.py` terá um modelo de configuração exclusivo do OpenRouter contendo API key, modelo, endpoint, headers opcionais, temperatura e `LLM_TIMEOUT_SECONDS`, cujo default será 30. O carregamento lerá `.env`/ambiente sem valores secretos versionados. Não haverá mecanismo genérico de múltiplos providers nem fallback automático. Testes determinísticos poderão construir configuração/fake sem API key; o cliente real exigirá a chave somente quando for usado.

### LLM service and schemas

`llm_service.py` manterá um protocolo pequeno (`extract_intent` e `generate_message`) para injeção. O serviço real usará LangChain para acessar exclusivamente o modelo compatível com OpenAI apontado para OpenRouter e criará duas interfaces de Structured Output com Pydantic. `IntentExtraction` usará enum/literal para as três intenções e campos extraídos; `MessageGeneration` exigirá mensagem não vazia. Timeout, transporte e parsing serão tratados sem permitir execução com dado parcial.

### Prompts

`prompts/v1/identify_intent.py` e `prompts/v1/message.py` fornecerão templates em português, com instruções de intenção permitida, profissionais, data de referência, campos de saída e regras de segurança. Serão funções puras ou templates sem dependência de LangGraph para teste isolado.

### GraphState and factory

`state.py` definirá `GraphState` como `TypedDict` com `messages` usando `add_messages`, intenção controlada, dados extraídos, status da ação, erro, resposta, catálogo e rastreamento opcional de nodes. `factory.py` receberá `MedicalLLM` e `AppointmentCatalog`, registrará os quatro nodes, ligará `START` a `identify_intent`, usará `router.py` para conditional edges e compilará o grafo. `graph.py` exportará uma instância padrão para FastAPI/CLI e uma função de construção para testes.

### Nodes and routing

- `identify_intent`: chama o LLM, valida/normaliza a saída e grava o resultado no estado; timeout/falha de identificação produz `unknown` com erro e segue para `message`.
- `scheduler`: valida `professionalId`, `datetime` e `patientName`; `reason` é opcional. Dados ausentes geram falha de ação sem chamar o catálogo.
- `canceller`: valida `professionalId`, `datetime` e `patientName`; dados ausentes geram falha de ação sem chamar o catálogo.
- `message`: monta o cenário e chama o LLM para mensagem estruturada; usa fallback seguro se a geração falhar.
- `route_medical`: retorna somente `schedule`, `cancel` ou `message`, impedindo que valores do modelo sejam usados como nome arbitrário de node.

### Dependency injection

Nodes receberão dependências por factory/construtor ou closure explícita. Testes fornecerão fake com respostas determinísticas de `IntentExtraction` e `MessageGeneration`, além de catálogos com relógio controlado. Endpoint e CLI usarão o factory padrão; nenhum teste dependerá de monkeypatch de rede.

### API and CLI compatibility

`app.py` preservará `POST /chat`, validação mínima de `question`, modelo de resposta e status 422/500. O estado será normalizado no contrato HTTP sem expor histórico ou detalhes do provider. `langgraph.json` continuará apontando para `src/langchain_intro/graph.py:graph`; o grafo deverá ser compilado e invocável sem iniciar FastAPI.

### Testing strategy

- Unitários: schemas, configuração sem segredos, prompts, fake LLM, domínio, nodes, router e fallback. A avaliação de identificação usará o conjunto fechado `INT-001` a `INT-010` definido no `spec.md`.
- Integração determinística: grafo completo para schedule/cancel/unknown/erro usando fake e catálogo em memória.
- Contrato HTTP: respostas 200/422/500, normalização e independência do processo LangGraph Dev.
- Contrato CLI: configuração, nodes, conditional edges e invocação do grafo publicado.
- Provider real: teste separado, condicionado por `RUN_LLM_INTEGRATION_TESTS` e credenciais; valida conectividade e parsing mínimo, nunca é requisito da suíte padrão.
- Timeout: testes determinísticos devem inspecionar a configuração quando `LLM_TIMEOUT_SECONDS` estiver ausente (30 segundos) e quando estiver definida (por exemplo, 10 segundos), sem esperar. Valores inválidos devem verificar o `ValueError` previsto no contrato.

### Provider, timeout e dados incompletos

O serviço configura exclusivamente OpenRouter por ambiente e usa LangChain como fronteira de comunicação. `LLM_TIMEOUT_SECONDS` terá default 30; o fake de testes lançará a exceção imediatamente para verificar o tratamento sem espera real. Falha/timeout durante `identify_intent` grava `unknown` e erro no `GraphState`, roteia para `message` e não chama `AppointmentCatalog`. Se a intenção for válida, mas faltar `professionalId`, `datetime` ou `patientName`, o node `schedule`/`cancel` mantém a intenção, registra `actionSuccess=false` e enumera os campos ausentes, sem invocar o domínio.

### Didactic documentation acceptance

Cada classe, método e função criada ou modificada deve possuir docstring em português com responsabilidade, parâmetros, retorno e erros aplicáveis. Comentários conceituais devem explicar o porquê da configuração LangChain/OpenRouter, Structured Output/Pydantic, GraphState, StateGraph, nodes, router, conditional edges, DI, serviços e tratamento de erros. A verificação deve privilegiar os pontos de decisão e evitar comentários sobre operações óbvias.

## Phase 0: Research Findings

Decisões detalhadas e referências estão em [research.md](./research.md). As APIs atuais consultadas orientam o uso de `with_structured_output` com Pydantic, captura de erro de parsing, `StateGraph` compilado com conditional edges e endpoint OpenRouter compatível com OpenAI.

## Phase 1: Design Artifacts

- [data-model.md](./data-model.md): entidades, schemas, estado e transições.
- [contracts/chat.md](./contracts/chat.md): contrato externo do endpoint HTTP.
- [contracts/llm.md](./contracts/llm.md): contrato do serviço de LLM e saídas estruturadas.
- [quickstart.md](./quickstart.md): validação local determinística, CLI e provider opt-in.

## Post-Design Constitution Check

Postura aprovada: o desenho mantém escopo controlado, preserva o domínio em memória, separa referência e implementação, torna o provider substituível em testes e documenta as decisões necessárias para a próxima fase. Não foram introduzidas dependências ou funcionalidades fora da necessidade da aula.

## Complexity Tracking

Nenhuma violação constitucional ou complexidade excepcional requer justificativa adicional.
