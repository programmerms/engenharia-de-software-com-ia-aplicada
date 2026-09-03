# Feature Specification: Medical Appointment com LLM

**Feature Branch**: `004-medical-appointment-llm`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Evoluir o projeto Python atual de Medical Appointment para incorporar os conceitos de IA da nova aula, com integração real a LLM, OpenRouter, Structured Output, identificação de intenção, fluxo LangGraph e documentação didática."

## Clarifications

### Session 2026-09-03

- **Q:** Quais dados são necessários para cada operação de domínio? **A:** `schedule` exige `professionalId`, `datetime` e `patientName`; `reason` é opcional. `cancel` exige os mesmos três campos para localizar a consulta. A falta de qualquer campo impede a chamada ao domínio, mantém a intenção identificada e produz `actionSuccess=false` com `actionError` descrevendo os campos ausentes.
- **Q:** Qual provider deve ser usado? **A:** OpenRouter é o único gateway desta feature, acessado por LangChain. API key, modelo, temperatura, timeout e configurações OpenRouter aplicáveis vêm do ambiente; não haverá abstração genérica de múltiplos providers nem fallback automático.
- **Q:** Como tratar indisponibilidade do LLM? **A:** `LLM_TIMEOUT_SECONDS` tem default 30 e pode ser sobrescrito. O serviço captura timeout, a identificação retorna `intent="unknown"` com erro, o domínio não é executado e a geração de mensagem usa fallback determinístico.
- **Q:** Qual nomenclatura orienta a implementação? **A:** Nodes `identify_intent`, `schedule`, `cancel` e `message`; arquivos `identify_intent.py`, `scheduler.py`, `canceller.py`, `message.py`; serviços `llm_service.py` e `appointment_service.py`; graph `graph.py` e `factory.py`; router `router.py`; modelos `models.py`; estado `state.py`.
- **Q:** Qual documentação é obrigatória? **A:** Classes, métodos e funções devem ter docstrings em português; os pontos de LangChain, OpenRouter, Structured Output, Pydantic, GraphState, StateGraph, nodes, router, conditional edges, DI, serviços e erros devem conter comentários que expliquem decisões e motivos.
- **Q:** FR-013 e SC-004 são duplicados? **A:** Não. FR-013 define o comportamento funcional de não executar o domínio com dados inválidos; SC-004 mede, por testes, que chamadas ao domínio não ocorreram nesses cenários.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agendar consulta por linguagem natural (Priority: P1)

Como paciente, quero solicitar um agendamento em linguagem natural para que o sistema interprete minha intenção, extraia os dados necessários e confirme a operação.

**Why this priority**: O agendamento é o fluxo principal do domínio e demonstra a cadeia completa de interpretação, roteamento, regra de negócio e resposta ao usuário.

**Independent Test**: Enviar uma solicitação contendo paciente, profissional, data, horário e motivo; verificar que a consulta é criada e que a resposta confirma os dados relevantes.

**Acceptance Scenarios**:

1. **Given** um profissional existente e um horário futuro livre, **When** o usuário solicitar uma consulta usando uma formulação natural de agendamento, **Then** o sistema deve classificar a intenção como `schedule`, extrair os dados estruturados, executar o agendamento e retornar confirmação.
2. **Given** um horário já ocupado, **When** o usuário solicitar esse agendamento, **Then** o sistema deve encaminhar a operação ao serviço de domínio, rejeitar o conflito e retornar uma mensagem compreensível sem criar uma segunda consulta.
3. **Given** uma solicitação de agendamento sem um dado obrigatório, **When** o fluxo for executado, **Then** o sistema deve manter a operação sem efeito e explicar quais informações são necessárias.

### User Story 2 - Cancelar consulta por linguagem natural (Priority: P1)

Como paciente, quero cancelar uma consulta informando seus dados em linguagem natural para que o sistema encontre o agendamento correto e confirme o cancelamento.

**Why this priority**: O cancelamento é o segundo fluxo de negócio obrigatório e comprova que o mesmo resultado estruturado pode direcionar o grafo para outro caminho.

**Independent Test**: Criar uma consulta em memória, enviar uma solicitação de cancelamento e verificar que apenas a consulta correspondente é removida.

**Acceptance Scenarios**:

1. **Given** uma consulta existente que corresponde ao paciente, profissional e horário informados, **When** o usuário solicitar seu cancelamento, **Then** a intenção deve ser `cancel`, a consulta deve ser removida e a resposta deve confirmar o cancelamento.
2. **Given** que não existe consulta correspondente, **When** o usuário solicitar o cancelamento, **Then** nenhuma consulta deve ser removida e a resposta deve informar que o agendamento não foi encontrado.
3. **Given** uma solicitação com dados insuficientes, **When** o fluxo for executado, **Then** o sistema deve evitar uma tentativa ambígua de cancelamento e orientar o usuário sobre os dados necessários.

### User Story 3 - Receber orientação para solicitações desconhecidas (Priority: P1)

Como usuário, quero receber uma orientação quando minha mensagem não for relacionada a agendamento ou cancelamento para entender quais solicitações o sistema atende.

**Why this priority**: O caminho `unknown` garante comportamento seguro para entradas fora do domínio e completa o contrato controlado de intenções.

**Independent Test**: Enviar uma mensagem não relacionada a consultas e verificar que nenhuma regra de agendamento ou cancelamento é executada.

**Acceptance Scenarios**:

1. **Given** uma mensagem sem intenção médica de agendar ou cancelar, **When** o sistema a processar, **Then** a intenção deve ser `unknown`, o fluxo deve ir diretamente para a geração de mensagem e nenhuma alteração no catálogo deve ocorrer.
2. **Given** uma falha de comunicação ou de interpretação estruturada do LLM, **When** o fluxo tratar a falha, **Then** ele deve seguir pelo caminho seguro de erro/mensagem e não executar uma operação de domínio por inferência parcial.

### User Story 4 - Aprender o fluxo de IA através do código (Priority: P2)

Como estudante, quero acompanhar as responsabilidades de configuração, prompts, LLM, saída estruturada, estado e nós para compreender a integração entre LangChain e LangGraph.

**Why this priority**: A finalidade principal da feature é didática; a organização e a documentação são parte do valor entregue, embora dependam dos fluxos funcionais.

**Independent Test**: Revisar a documentação do código e executar testes determinísticos que demonstrem a passagem entrada → LLM estruturado → estado → roteamento → domínio → resposta.

**Acceptance Scenarios**:

1. **Given** o código da feature, **When** um estudante consultar as classes, funções e nós modificados, **Then** encontrará docstrings em português explicando responsabilidade, parâmetros, retornos e erros relevantes.
2. **Given** o fluxo do grafo, **When** um estudante acompanhar seus pontos principais, **Then** encontrará comentários explicando o porquê das decisões de integração, Structured Output, estado, router, conditional edges e injeção de dependências.

### Edge Cases

- O LLM pode retornar uma intenção fora do conjunto permitido; o sistema deve normalizá-la ou tratá-la como `unknown`.
- O LLM pode retornar saída inválida, incompleta ou não parseável; nenhuma ação de domínio deve ser executada.
- A pergunta pode conter simultaneamente sinais de agendamento e cancelamento; o resultado deve ser tratado como ambíguo/`unknown`.
- O profissional informado pode não existir no catálogo.
- A data pode estar no passado, ser inválida ou não conter horário suficiente para a operação.
- O horário solicitado pode estar ocupado.
- O cancelamento pode não encontrar correspondência exata de profissional, paciente e data/hora.
- A chave do provider pode estar ausente, inválida ou indisponível; o erro deve ser seguro e compreensível.
- A geração da mensagem final pode falhar depois que uma operação de domínio já tiver sido concluída; o sistema deve preservar o resultado da operação e usar uma resposta de fallback adequada.
- A chamada ao LLM pode exceder `LLM_TIMEOUT_SECONDS`; o serviço deve capturar o timeout, preservar o processo, evitar o domínio quando ocorrer na identificação e usar fallback determinístico na mensagem.
- O teste de integração real pode ser executado sem rede, credencial ou cota; ele deve ser opt-in e não bloquear a suíte determinística.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST aceitar uma mensagem do usuário e iniciar um fluxo de atendimento de consultas médicas.
- **FR-002**: O sistema MUST interpretar a mensagem usando um LLM através da camada de integração definida para a feature.
- **FR-003**: A interpretação MUST produzir Structured Output validado por um schema Pydantic.
- **FR-004**: O resultado de intenção MUST utilizar somente `schedule`, `cancel` ou `unknown`.
- **FR-005**: O Structured Output MUST representar `professionalId`, `datetime` e `patientName` como campos necessários para `schedule` e `cancel`; `reason` é opcional para `schedule` e não é necessário para `cancel`. A representação interna Python pode usar `professional_id`, `patient_name` e demais nomes idiomáticos, desde que preserve o contrato semântico.
- **FR-006**: O sistema MUST colocar o resultado estruturado no estado da execução antes de decidir o próximo passo.
- **FR-007**: O fluxo MUST direcionar `schedule` ao nó de agendamento, `cancel` ao nó de cancelamento e `unknown` ou erro ao nó de mensagem.
- **FR-008**: O nó de agendamento MUST delegar a criação da consulta ao serviço de domínio em memória.
- **FR-009**: O nó de cancelamento MUST delegar a remoção da consulta ao mesmo serviço de domínio em memória.
- **FR-010**: O serviço de domínio MUST preservar as regras de profissional existente, data futura, disponibilidade e correspondência para cancelamento.
- **FR-011**: O nó de geração de mensagem MUST utilizar o LLM para produzir uma resposta natural baseada na intenção e no resultado da operação.
- **FR-012**: A resposta estruturada do nó de mensagem MUST conter uma mensagem não vazia e adequada ao cenário de sucesso, erro ou intenção desconhecida.
- **FR-013**: Dados inválidos ou incompletos MUST NOT resultar em chamada ao serviço de domínio. O node responsável MUST registrar `actionSuccess=false` e `actionError` com os campos ausentes ou inválidos; isso define o comportamento funcional, enquanto SC-004 define sua comprovação mensurável por testes.
- **FR-014**: OpenRouter MUST ser o único gateway/provider desta feature, acessado através de LangChain. API key, modelo, temperatura e configurações OpenRouter aplicáveis MUST vir de variáveis de ambiente, sem credenciais no código ou em arquivos versionados. Não haverá mecanismo genérico de múltiplos providers, fallback automático entre providers ou ordenação adicional de modelos.
- **FR-015**: A integração MUST encapsular o acesso LangChain → OpenRouter em um serviço de LLM dedicado.
- **FR-016**: A construção do grafo MUST separar configuração, serviço de LLM, prompts, estado, nós, composição do grafo e serviço de domínio.
- **FR-017**: Os componentes que dependem do LLM ou do serviço de domínio MUST permitir injeção de dependências quando isso for necessário para testes e demonstrações didáticas.
- **FR-018**: A API MUST manter respostas estruturadas para sucesso, erro de domínio, entrada inválida e falha inesperada, sem expor detalhes sensíveis.
- **FR-019**: A suíte determinística MUST testar os fluxos de agendamento, cancelamento, intenção desconhecida, erros, roteamento, schemas e fallback sem exigir chamadas reais ao LLM.
- **FR-020**: Deve existir teste opcional e isolado para o provider real, executável somente quando explicitamente habilitado e configurado.
- **FR-021**: Como obrigação funcional de documentação do código, toda classe criada ou modificada MUST possuir docstring em português com responsabilidade, papel arquitetural e participação no fluxo.
- **FR-022**: Como obrigação funcional de documentação do código, toda função ou método criado ou modificado MUST possuir docstring em português com finalidade, parâmetros, retorno e possíveis erros aplicáveis.
- **FR-023**: Os pontos conceituais de LangChain, LLM, OpenRouter, Structured Output, Pydantic, GraphState, StateGraph, nodes, router, conditional edges, DI, serviços e tratamento de erros MUST possuir comentários didáticos em português explicando o porquê das decisões, sem comentar linhas óbvias.
- **FR-024**: A implementação MUST transpor os conceitos para convenções idiomáticas de Python e MUST NOT modificar arquivos da referência TypeScript.

### Non-Functional Requirements

- **NFR-001**: A execução padrão dos testes MUST funcionar sem API key, rede externa ou provider real.
- **NFR-002**: Falhas do LLM MUST ser tratadas sem vazar API keys, prompts privados ou detalhes internos desnecessários para o usuário.
- **NFR-003**: O armazenamento de consultas MUST permanecer em memória e não exigir banco de dados.
- **NFR-004**: A configuração do projeto MUST continuar compatível com Python 3.13.x, Poetry, FastAPI, LangChain e LangGraph já adotados.
- **NFR-005**: A documentação do código MUST permanecer em português e ser suficiente para que um estudante acompanhe o fluxo completo da feature.
- **NFR-006**: A solução MUST preservar a finalidade didática, priorizando clareza, rastreabilidade do fluxo e simplicidade sobre abstrações prematuras.
- **NFR-007**: O comportamento da API MUST permanecer determinístico nos testes que usam doubles/fakes do LLM e do serviço de domínio.
- **NFR-008**: A integração real MUST usar `LLM_TIMEOUT_SECONDS=30` quando a variável estiver ausente e MUST usar o valor numérico configurado quando ela estiver presente (por exemplo, `10` resulta em timeout de 10 segundos). Valores inválidos devem seguir o erro de configuração já definido no contrato, sem chamada ao provider. O serviço MUST capturar timeout sem derrubar o processo, converter falha de identificação para `unknown` com erro, impedir domínio após essa falha e usar fallback determinístico na mensagem.
- **NFR-009**: Como requisito de qualidade e finalidade didática, a documentação em português MUST cobrir responsabilidade, parâmetros, retornos e erros de classes, métodos e funções, além de explicar o fluxo conceitual para estudantes de pós-graduação.

### Key Entities

- **IntentExtraction**: Resultado estruturado da interpretação da mensagem, contendo intenção controlada e dados de consulta extraídos.
- **MessageGeneration**: Resultado estruturado da geração da resposta final, contendo uma mensagem não vazia.
- **GraphState**: Estado efêmero que transporta mensagens, intenção, dados extraídos, resultado da operação, erros e resposta ao longo do grafo.
- **Professional**: Profissional disponível no catálogo, identificado por nome, identificador e especialidade.
- **Appointment**: Consulta em memória, associando paciente, profissional, data/hora e motivo.
- **AppointmentCatalog**: Serviço de domínio que consulta profissionais, verifica disponibilidade, agenda e cancela consultas.
- **LLM Service**: Serviço dedicado que encapsula configuração, comunicação com provider e respostas estruturadas do modelo.
- **Prompt Template**: Instruções versionadas usadas para classificação/extração e geração da mensagem final.

## Scope

### In Scope

- Evolução do fluxo médico Python para consumir LLM em identificação de intenção e geração de mensagem.
- Integração configurável com OpenRouter.
- Saída estruturada validada por Pydantic.
- Intenções `schedule`, `cancel` e `unknown`.
- Extração dos dados necessários para agendamento e cancelamento.
- Roteamento condicional do LangGraph.
- Agendamento e cancelamento usando o serviço em memória existente/evoluído.
- Prompts versionados e separados da lógica dos nós.
- Configuração por ambiente e arquivo de exemplo sem segredos reais.
- Testes determinísticos e teste real opt-in do provider.
- Documentação didática em português no código e nas decisões relevantes.

### Out of Scope

- Banco de dados, persistência entre processos ou histórico permanente de pacientes.
- Autenticação, autorização, multiusuário ou controle de acesso.
- RAG, busca na web, prontuário eletrônico ou aconselhamento médico.
- Novos fluxos além de agendar, cancelar e responder a intenção desconhecida.
- Alteração de qualquer arquivo em `../versao-typescript`.
- Reprodução literal de diretórios, APIs ou nomes TypeScript.
- Retry complexo, observabilidade avançada, filas ou escalabilidade de produção.
- Garantia de disponibilidade, precisão clínica ou uso em ambiente médico real.

## Assumptions

- O catálogo didático de profissionais e consultas continuará sendo fornecido em memória e poderá ser reinicializado entre execuções.
- OpenRouter será o único gateway/provider; o nome do modelo, API key, temperatura, timeout e configurações específicas aplicáveis serão configuráveis por ambiente, sem fallback genérico ou entre providers.
- `LLM_TIMEOUT_SECONDS` terá valor padrão `30` e poderá ser sobrescrito por ambiente.
- Serão adotados nomes de ambiente equivalentes a `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_HTTP_REFERER`, `OPENROUTER_X_TITLE` e configurações opcionais de temperatura/timeout.
- O idioma preferencial das mensagens será português, mesmo quando o usuário empregar variações de linguagem natural.
- Datas e horários extraídos pelo LLM serão validados e normalizados antes de chegar ao serviço de domínio.
- O teste real do provider será marcado/configurado como opcional e não será executado na validação padrão sem credenciais.
- O contrato externo atual da API, com intenção, sucesso, mensagem, consulta opcional e erro opcional, será preservado sempre que compatível com a nova aula.

## Risks and Decisions

### Riscos

- Respostas de LLM podem ser inconsistentes, incompletas ou incompatíveis com o schema.
- O provider pode apresentar indisponibilidade, latência, limites de uso ou alterações de modelo.
- A interpretação de datas relativas pode depender do horário de referência e do fuso adotado.
- A geração de mensagem pode falhar após uma alteração bem-sucedida no catálogo.
- A dependência de um provider real pode tornar o aprendizado e os testes instáveis se não houver isolamento.

### Decisões relevantes

- O LLM interpreta e estrutura a linguagem; o serviço de domínio continua responsável por regras e efeitos de agendamento/cancelamento.
- O estado do grafo será a fronteira explícita entre interpretação, roteamento, operação e resposta.
- `unknown` representará principalmente intenção não identificada ou falha de identificação pelo LLM. Dados ausentes para uma intenção já identificada não serão convertidos automaticamente em `unknown`; o node de domínio registrará `actionSuccess=false` e os campos ausentes.
- Pydantic será usado para validar as saídas estruturadas de intenção e mensagem, mantendo um contrato explícito e legível para estudantes Python.
- O serviço LLM será separado da construção do grafo para permitir doubles determinísticos e um teste real opt-in.
- A solução Python poderá diferir da referência TypeScript em nomes e APIs, desde que preserve o comportamento e os conceitos da aula.
- A documentação didática será considerada parte do resultado da feature, não apenas uma atividade posterior de manutenção.

## Success Criteria *(mandatory)*

### Measurable Outcomes

### Conjunto fechado de cenários de identificação

Os cenários abaixo formam o conjunto fechado usado para calcular SC-001. Um cenário é classificado corretamente quando a intenção estruturada e o resultado esperado da operação coincidem com a tabela.

| ID | Entrada | Intenção esperada | Resultado esperado |
|---|---|---|---|
| INT-001 | `Quero marcar uma consulta` | `schedule` | Roteia para `schedule`; sem execução enquanto faltarem dados obrigatórios. |
| INT-002 | `Gostaria de agendar uma consulta com o Dr. Alicio` | `schedule` | Extrai a intenção e o profissional quando reconhecido. |
| INT-003 | `Preciso consultar um médico` | `schedule` | Roteia para `schedule`; solicita os campos obrigatórios ausentes. |
| INT-004 | `Sou Maria Santos e quero agendar com o Dr. Alicio amanhã às 16h` | `schedule` | Dados estruturados permitem tentativa de agendamento pelo domínio. |
| INT-005 | `Quero cancelar minha consulta` | `cancel` | Roteia para `cancel`; não executa sem os três campos de localização. |
| INT-006 | `Gostaria de desmarcar a consulta da Maria` | `cancel` | Interpreta cancelamento e extrai o paciente quando reconhecido. |
| INT-007 | `Cancele a consulta da Maria com o Dr. Alicio amanhã às 16h` | `cancel` | Dados estruturados permitem tentativa de cancelamento pelo domínio. |
| INT-008 | `Olá, qual é a previsão do tempo?` | `unknown` | Vai diretamente para `message`; nenhum serviço de domínio é chamado. |
| INT-009 | `Quero agendar e cancelar uma consulta` | `unknown` | Trata a mensagem ambígua com resposta segura; nenhum domínio é chamado. |
| INT-010 | `Solicitação não interpretável` com falha de identificação simulada | `unknown` | Registra erro de identificação e usa mensagem de fallback; nenhum domínio é chamado. |

- **SC-001**: A métrica de identificação será calculada como `cenários classificados corretamente / total de cenários avaliados`, usando os 10 cenários `INT-001` a `INT-010`; o resultado MUST ser de pelo menos 90% (no mínimo 9 de 10 cenários).
- **SC-002**: 100% dos testes padrão devem executar sem API key, rede externa ou chamada real ao provider.
- **SC-003**: 100% das saídas aceitas nos testes de Structured Output devem obedecer aos schemas de intenção ou mensagem definidos para a feature.
- **SC-004**: Os testes devem comprovar que, em 100% dos cenários de dados inválidos ou incompletos para `schedule` e `cancel`, o serviço de domínio não é chamado.
- **SC-005**: Usuários devem receber uma resposta final não vazia em 100% dos cenários cobertos, incluindo sucesso, erro de domínio, intenção desconhecida e falha do provider.
- **SC-006**: O fluxo completo deve ser rastreável por seus estágios conceituais — entrada, identificação, estado, roteamento, operação e mensagem — em uma execução de teste.
- **SC-007**: Um estudante familiarizado com Python deve conseguir localizar a responsabilidade de cada camada e explicar o fluxo completo após consultar a documentação dos componentes principais.
- **SC-008**: O teste real do provider, quando habilitado com configuração válida, deve validar a conectividade e a compatibilidade da resposta sem alterar o resultado da suíte determinística.
- **SC-009**: Um fake/mock deve simular timeout sem aguardar 30 segundos reais; o teste deve comprovar `unknown` com erro, ausência de chamada ao domínio e fallback não vazio da mensagem.
