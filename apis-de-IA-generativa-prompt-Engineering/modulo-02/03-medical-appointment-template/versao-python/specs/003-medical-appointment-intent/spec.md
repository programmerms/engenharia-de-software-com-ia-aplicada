# Feature Specification: Medical Appointment Intent Flow

**Feature Branch**: `003-medical-appointment-intent`
**Created**: 2026-08-31
**Status**: Refined

## Objective and Evolution Boundary

Esta feature cria a implementação funcional do Módulo 3 a partir de `../versao-typescript`.
O projeto Python existente é apenas o ponto de partida técnico:

```text
template técnico do Módulo 2 + domínio médico do Módulo 3 = projeto Python do Módulo 3
```

O template técnico herdado inclui Python 3.13.12, pyenv, Poetry, `.venv` local independente,
FastAPI, LangChain, LangGraph, LangGraph CLI, `langgraph.json`, `src/`, testes e práticas de
execução/configuração. Esses elementos devem ser preservados ou evoluídos quando forem úteis.

O domínio funcional do Módulo 2 não é um contrato desta feature. Uppercase, lowercase, fallback,
comandos de transformação, nodes, estados, respostas HTTP e testes que existiam exclusivamente
para aquele exercício podem ser removidos ou substituídos. Não deve ser criada compatibilidade
artificial para mantê-los.

`../versao-typescript` é somente leitura e permanece intacto.

## Reference Analysis

A referência possui `POST /chat`, estado de consulta, intenções `schedule`, `cancel` e `unknown`,
roteamento condicional, nodes de identificação/agendamento/cancelamento/mensagem, catálogo de
profissionais e serviço de consultas em memória. Seus testes E2E verificam principalmente o
status HTTP. A referência declara configuração OpenRouter e prompts, mas os nodes executados não
invocam efetivamente um LLM, não usam structured output e não importam os helpers de prompt.

Assim, o comportamento funcional desta etapa é o fluxo médico observável. A implementação Python
deve preservar os conceitos e resultados relevantes, mas pode reorganizar nomes e APIs. LLM real
ou provider externo não é requisito quando não houver evidência de uso executável na referência.

## User Scenarios & Testing

### User Story 1 - Agendar consulta (Priority: P1)

Como paciente, quero informar os dados de uma consulta para receber confirmação ou uma explicação
clara quando o agendamento não puder ser realizado.

**Independent Test**: Executar o grafo e `POST /chat` com horário livre, horário ocupado,
profissional inexistente e dados incompletos.

**Acceptance Scenarios**:

1. **Given** profissional existente e horário livre, **When** o paciente informa nome,
   profissional, data/hora e motivo, **Then** a consulta é criada e a resposta confirma os dados.
2. **Given** horário ocupado, **When** o paciente solicita o mesmo horário, **Then** nenhuma nova
   consulta é criada e a resposta informa a indisponibilidade.
3. **Given** profissional inexistente ou dado obrigatório ausente, **When** o paciente solicita o
   agendamento, **Then** nenhuma consulta é criada e a resposta informa o problema.

### User Story 2 - Cancelar consulta (Priority: P1)

Como paciente, quero cancelar uma consulta existente informando os dados necessários.

**Independent Test**: Criar uma consulta em teste, cancelá-la pelo grafo e por HTTP, e repetir o
cancelamento para verificar o resultado de não encontrado.

**Acceptance Scenarios**:

1. **Given** correspondência exata de profissional, paciente e data/hora, **When** o paciente pede
   cancelamento, **Then** a consulta é removida e a resposta confirma a ação.
2. **Given** nenhuma correspondência, **When** o paciente pede cancelamento, **Then** nada é
   removido e a resposta explica que não foi encontrada.

### User Story 3 - Identificar e rotear intenção (Priority: P1)

Como usuário, quero que uma mensagem de agendamento, cancelamento ou assunto não suportado seja
encaminhada ao caminho médico correspondente.

**Independent Test**: Invocar o grafo com mensagens representativas das três intenções e verificar
intenção, estado final, ramo percorrido e resposta.

**Acceptance Scenarios**:

1. Mensagem de agendamento produz `schedule` e segue o ramo de agendamento.
2. Mensagem de cancelamento produz `cancel` e segue o ramo de cancelamento.
3. Mensagem sem intenção reconhecida produz `unknown` e segue o ramo de orientação.
4. Mensagem com evidência conflitante produz `unknown` e pede esclarecimento.

## Functional Requirements

- **FR-001**: O sistema MUST identificar `schedule`, `cancel` ou `unknown` a partir da mensagem.
- **FR-002**: O estado MUST preservar mensagens, intenção, dados extraídos, resultado, erro e
  resposta da execução médica, permanecendo isolado por invocação.
- **FR-003**: O fluxo de agendamento MUST validar paciente, profissional, data/hora e motivo.
- **FR-004**: O catálogo MUST fornecer profissionais determinísticos com id, nome e especialidade.
- **FR-005**: O domínio MUST verificar existência, disponibilidade e conflito de horário antes de
  criar uma consulta.
- **FR-006**: O domínio MUST criar uma consulta válida e retornar confirmação com seus dados.
- **FR-007**: O fluxo de cancelamento MUST localizar por profissional, paciente e data/hora e só
  remover uma consulta quando houver correspondência.
- **FR-008**: O grafo MUST conter identificação, roteamento condicional, agendamento, cancelamento
  e resposta convergente; erro e `unknown` devem chegar ao caminho de resposta.
- **FR-009**: As respostas MUST informar sucesso ou falha de modo claro, sem detalhes internos.
- **FR-010**: `POST /chat` MUST aceitar `{"question": "..."}`, validar a entrada, executar o
  grafo médico e devolver resposta estruturada com intenção, sucesso, mensagem e dados da consulta
  ou erro quando aplicável.
- **FR-011**: Entrada inválida MUST resultar em erro HTTP de validação sem executar o grafo; falha
  inesperada MUST resultar em erro HTTP de servidor sem stack trace ou segredo.
- **FR-012**: `langgraph.json` MUST carregar e expor o novo grafo compilado, sem segundo aplicativo.
- **FR-013**: A implementação MUST documentar equivalências TypeScript → Python, manter a
  referência intacta e declarar apenas dependências/configuração necessárias.

## Key Entities

- **Mensagem**: conteúdo e papel na execução.
- **Intenção**: `schedule`, `cancel` ou `unknown` usada no roteamento.
- **Profissional**: id, nome e especialidade.
- **Consulta**: profissional, paciente, data/hora e motivo.
- **Estado médico**: mensagens, intenção, dados extraídos, resultado, erro e saída efêmera.

## API Contract

O endpoint é `POST /chat` com JSON contendo `question`. O contrato médico é estruturado:

```json
{"intent":"schedule","success":true,"message":"Sua consulta foi confirmada.","appointment":{"professional_id":2,"patient_name":"Maria Santos","datetime":"2026-09-01T14:00:00","reason":"avaliação"}}
```

Falha de domínio e intenção desconhecida usam o mesmo formato, com `success: false` e `error`
quando houver uma categoria útil. O formato textual do exercício do Módulo 2 não é obrigatório.

## Edge Cases

- Corpo ausente, `question` não textual ou abaixo do mínimo definido pelo contrato: erro 422.
- Caixa variável, acentos, pontuação e espaços não devem impedir identificação ou extração.
- Evidências simultâneas de agendamento e cancelamento: `unknown` e pedido de esclarecimento.
- Data/hora inválida, passada ou ambígua: não operar e informar a correção necessária.
- Profissional inexistente, consulta não encontrada e horário ocupado: falha sem mutação indevida.
- Execuções concorrentes do mesmo horário: no máximo uma criação confirmada.

## External Dependencies and Configuration

O núcleo usa catálogo em memória e não exige rede, banco, API key ou provider. A referência contém
configuração OpenRouter, mas ela não é usada pelos nodes executáveis observados e não será requisito
obrigatório. Segredos, se necessários em evolução posterior, virão de variáveis de ambiente.

## Non-Functional Requirements

- **NFR-001**: O fluxo médico local deve ser determinístico e responder em até 1 segundo em teste
  isolado, sem chamada externa.
- **NFR-002**: Testes de domínio, grafo, API e CLI devem executar sem credenciais reais.
- **NFR-003**: A implementação deve ser idiomática, legível e simples para estudo.
- **NFR-004**: O ambiente/template técnico herdado deve continuar reproduzível por Poetry e CLI.

## Success Criteria

- **SC-001**: Todos os cenários de agendamento e cancelamento possuem testes determinísticos.
- **SC-002**: As três intenções possuem testes de classificação, roteamento e resposta.
- **SC-003**: O catálogo impede duplicidade e não sofre mutação em falhas de domínio.
- **SC-004**: `POST /chat` e `langgraph.json` carregam o novo fluxo pelos comandos documentados.
- **SC-005**: A suíte relevante da feature passa sem credenciais ou rede externa.
- **SC-006**: O README permite executar, inspecionar e testar o fluxo médico.

## Assumptions

- O catálogo é didático e em memória; não há persistência, autenticação, calendário real ou
  notificações.
- Datas relativas usam relógio injetável/configurável nos testes.
- A implementação pode substituir estado e nodes do Módulo 2 quando necessário.
- O TypeScript é referência somente leitura.
- A ausência de chamada efetiva de LLM na referência torna o fluxo determinístico o caminho
  principal; não se presume responsabilidade sem evidência executável.

## Out of Scope

- Preservação funcional de uppercase, lowercase, fallback, comandos, nodes, estados ou respostas
  HTTP do Módulo 2.
- Compatibilidade artificial com testes exclusivos da transformação textual.
- Banco, autenticação, calendário real, notificações, pagamentos, prontuário, triagem clínica,
  RAG, memória persistente, agentes e ferramentas externas.
- Tradução literal de classes, arquivos, diretórios ou APIs TypeScript.
- Provider LLM real obrigatório, structured output obrigatório ou chamadas externas na suíte padrão.
- Alteração ou sincronização automática de `../versao-typescript`.
