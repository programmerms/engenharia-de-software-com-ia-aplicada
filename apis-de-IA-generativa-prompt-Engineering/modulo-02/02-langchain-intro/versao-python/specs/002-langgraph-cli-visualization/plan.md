# Implementation Plan: Suporte ao LangGraph CLI e visualização do grafo

**Branch**: `002-langgraph-cli-visualization` | **Date**: 2026-08-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-langgraph-cli-visualization/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Adicionar ao projeto existente o suporte local do LangGraph CLI, apontando a
configuração para o objeto compilado `graph` já exportado por
`src/langchain_intro/graph.py`. A evolução incluirá a dependência do CLI gerenciada
por Poetry, `langgraph.json`, documentação didática dos dois modos de execução e
testes que comprovem carregamento, estrutura, roteamento e equivalência funcional,
sem modificar o grafo nem substituir a aplicação FastAPI.

## Technical Context

**Language/Version**: Python 3.13.12, selecionado por pyenv e fixado no Poetry

**Primary Dependencies**: FastAPI, Uvicorn, LangGraph, LangChain Core e LangGraph CLI
com o extra oficial para desenvolvimento local em memória

**Storage**: N/A; estado efêmero por execução e arquivos de configuração versionados

**Testing**: pytest; testes unitários existentes, integração HTTP existente e novos
testes de contrato/configuração e carregamento do grafo pelo CLI

**Target Platform**: desenvolvimento local em ambiente suportado pelo Poetry, com
servidor FastAPI e servidor LangGraph Dev independentes

**Project Type**: serviço web Python didático com ambiente de desenvolvimento de grafo

**Performance Goals**: iniciar o ambiente local sem erro de configuração e completar
as execuções determinísticas de validação em até 10 segundos após o servidor estar
disponível; não há meta de produção

**Constraints**: sem LLM, provider, API key, LangSmith direto, rede externa para os
cenários determinísticos, persistência, banco ou alteração da versão TypeScript;
preservar Poetry, pyenv, Python 3.13.12, FastAPI e contratos da baseline

**Scale/Scope**: uma configuração CLI, um grafo existente, cinco nodes, três destinos
condicionais, uma rota HTTP preservada, README atualizado e testes complementares

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Aprendizado e simplicidade**: PASS. A configuração expõe o mesmo grafo e mantém
  nomes, estado e caminhos observáveis; não adiciona camadas de abstração.
- **Python, Poetry e stack existente**: PASS. A dependência do CLI será declarada no
  Poetry, mantendo Python 3.13.12, FastAPI, LangGraph e LangChain Core.
- **APIs atuais e documentação oficial**: PASS. O formato de `langgraph.json`, o
  extra de instalação e `langgraph dev` foram confirmados na documentação oficial
  atual; decisões estão em [research.md](./research.md).
- **Evolução incremental e escopo controlado**: PASS. O objeto `graph` da baseline
  será reutilizado; LLM, providers, RAG, agentes, ferramentas, memória e deploy
  permanecem fora do escopo.
- **Testabilidade**: PASS. Serão preservados os testes existentes e adicionados
  testes de configuração, estrutura, equivalência funcional e independência de LLM.
- **Integridade e transparência**: PASS. README, quickstart, contratos e pesquisa
  explicarão a relação entre FastAPI, LangGraph Dev, configuração e código.
- **Gate result**: PASS antes da pesquisa; PASS após o design.

## Project Structure

### Documentation (this feature)

```text
specs/002-langgraph-cli-visualization/
├── plan.md              # This file ($speckit-plan command output)
├── research.md          # Phase 0 output ($speckit-plan command)
├── data-model.md        # Phase 1 output ($speckit-plan command)
├── quickstart.md        # Phase 1 output ($speckit-plan command)
├── contracts/           # Phase 1 output ($speckit-plan command)
└── tasks.md             # Phase 2 output ($speckit-tasks command - NOT created by $speckit-plan)
```

### Source Code (repository root)

```text
langgraph.json                  # configuração do CLI e entrypoint do grafo
pyproject.toml                  # dependência do CLI gerenciada por Poetry
README.md                       # instalação, dois modos e fluxo didático
src/
└── langchain_intro/
    ├── app.py                  # FastAPI e POST /chat, preservados
    ├── graph.py                # grafo existente, sem alteração funcional
    └── messages.py             # mensagens da baseline, preservadas

tests/
├── unit/                       # baseline preservada
├── integration/                # FastAPI preservado + CLI
└── contract/                   # configuração/estrutura, se necessário
```

**Structure Decision**: Single project Python existente. A configuração fica na raiz,
pois o CLI a procura no diretório atual; o entrypoint referencia o módulo empacotado
sob `src/`. O grafo e a aplicação continuam nos arquivos atuais. Os novos testes
serão colocados nas suítes existentes, sem camada de integração paralela.

## Design Decisions

### Configuração do LangGraph CLI

`langgraph.json` terá as chaves oficiais `dependencies`, `graphs` e `env`. O mapa
`graphs` usará um nome estável, como `langchain_intro`, apontando para
`./src/langchain_intro/graph.py:graph`. `dependencies` declarará o projeto local
(`.`) para resolver o pacote sob `src/`; `env` será usado somente conforme o formato
atual e não conterá credenciais. Como o grafo é determinístico, nenhum provider será
adicionado.

O extra oficial `langgraph-cli[inmem]` será adicionado às dependências de desenvolvimento
do Poetry na forma compatível com a versão resolvida no lockfile. A implementação
deve confirmar a versão compatível com Python 3.13.12 e atualizar o lockfile de forma
reprodutível.

### Reuso do grafo e separação de processos

Não haverá factory, wrapper ou grafo alternativo: o entrypoint importará o mesmo
objeto `graph = build_graph()` exportado atualmente. FastAPI continuará importando
esse objeto para `POST /chat`; `langgraph dev` será um servidor/interface local
complementar, sem ser iniciado pela aplicação HTTP nem depender dela.

### Testes planejados

- Validar JSON, chaves obrigatórias e entrypoint textual de `langgraph.json`.
- Importar o entrypoint e confirmar carregamento sem API key ou provider.
- Inspecionar nodes e conexões condicionais do grafo compilado.
- Executar uppercase, lowercase e fallback e comparar com `graph.invoke` da baseline.
- Iniciar o CLI em subprocesso com timeout, confirmar ausência de erro de configuração
  e encerrar o processo; não depender da UI ou de serviços externos.
- Executar a suíte atual do pytest e manter os testes de `POST /chat` inalterados.

## Phase 0: Research

As decisões estão consolidadas em [research.md](./research.md), incluindo formato do
arquivo, pacote/extra, comando de desenvolvimento e estratégia de reuso. Não há
questões técnicas pendentes.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) descreve configuração, estado e execução.
- [contracts/langgraph-cli.md](./contracts/langgraph-cli.md) define o contrato do CLI.
- [contracts/chat.md](./contracts/chat.md) registra o contrato preservado de `POST /chat`.
- [quickstart.md](./quickstart.md) fornece a validação ponta a ponta dos dois modos.

## Constitution Check — pós-design

- **Aprendizado e clareza**: PASS; o grafo explícito e a relação código/visualização
  permanecem centrais.
- **Evolução incremental**: PASS; somente CLI, configuração, docs e testes são
  adicionados.
- **Dependências e segredos**: PASS; sem LLM, provider, API key ou LangSmith direto.
- **FastAPI e Poetry**: PASS; ambos permanecem mecanismos e contratos da baseline.
- **Testabilidade**: PASS; subprocesso controlado, testes de comportamento e HTTP.
- **Referência TypeScript**: PASS; nenhum arquivo fora da versão Python será tocado.
- **Resultado final**: PASS; os critérios de aceitação estão mapeados para artefatos.

## Complexity Tracking

Nenhuma violação da Constitution requer justificativa.
