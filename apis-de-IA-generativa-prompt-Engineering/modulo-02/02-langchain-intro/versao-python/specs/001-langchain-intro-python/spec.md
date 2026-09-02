# Feature Specification: LangChain Intro Python

**Feature Branch**: `001-langchain-intro-python`

**Created**: 2026-08-30

**Status**: Draft

**Input**: User description: "Criar a especificação da primeira implementação Python do projeto LangChain Intro, com base na análise de ../versao-typescript, preservando intenção didática, conceitos e comportamentos relevantes, sem implementar código nesta etapa."

## Visão geral

Esta especificação define a baseline Python da aplicação didática do Módulo 02,
Projeto 02 — LangChain Intro. A aplicação recebe uma pergunta textual, identifica
um comando simples de transformação e devolve o texto transformado ou uma orientação
para comandos desconhecidos.

A referência TypeScript demonstra um fluxo de grafo com estado de mensagens, seleção
condicional de caminho e nós separados para identificação, transformação e resposta.
A implementação-alvo deve preservar esses conceitos, usando as abstrações atuais e
idiomáticas do ecossistema Python, sem exigir a reprodução da estrutura ou dos nomes
da referência.

## Contexto

A aplicação original expõe um único fluxo de conversa por HTTP. O corpo da requisição
contém `question`; o fluxo identifica a intenção pela presença, sem distinção de
maiúsculas e minúsculas, de `upper` ou `lower`; transforma a pergunta inteira quando
encontra um comando; e retorna uma mensagem fixa para comandos não reconhecidos.

A análise do projeto de referência identificou:

- servidor HTTP com operação `POST /chat`;
- validação de `question` como texto com pelo menos cinco caracteres;
- estado de grafo contendo mensagens, comando identificado e saída;
- roteamento condicional para uppercase, lowercase ou fallback;
- conversão integral do texto para maiúsculas ou minúsculas;
- mensagem final adicionada ao histórico conceitual de mensagens;
- testes de integração para os três caminhos principais;
- configuração de execução local e de um grafo nomeado para desenvolvimento;
- nenhuma chamada efetiva a modelo de linguagem;
- nenhuma dependência ou configuração efetiva de LangSmith/tracing no fluxo analisado.

## Objetivo

Disponibilizar uma primeira implementação Python executável localmente que ensine,
por meio de um exemplo pequeno e verificável, como uma entrada atravessa um grafo
com estado, identificação de intenção, roteamento condicional, transformação e
resposta.

## Escopo

A versão 1 inclui:

- uma interface HTTP para envio de uma pergunta textual;
- validação da entrada obrigatória;
- identificação dos comandos `upper` e `lower` sem distinção de caixa;
- prioridade determinística para `upper` quando os dois termos aparecem;
- transformação da pergunta completa;
- fallback determinístico para comandos desconhecidos;
- fluxo de grafo com estado de mensagens, comando e saída;
- execução local documentada;
- testes dos caminhos de sucesso e de validação;
- configuração de credenciais somente quando exigida pelo ambiente, sem credenciais
  reais no repositório.

A versão 1 não exige um provedor de LLM, pois a referência não realiza chamadas a
modelos. LangChain e LangGraph Python podem ser usados para preservar os conceitos
de mensagens e grafo, mas a especificação não fixa APIs, classes ou organização de
arquivos específicas.

## Usuários e atores

### Usuário da aplicação

Pessoa que envia uma pergunta textual e espera receber a transformação correspondente
ou uma orientação de uso.

### Desenvolvedor ou estudante

Pessoa que executa o projeto localmente, observa o fluxo e usa os testes para estudar
estado, nós, roteamento condicional e integração HTTP.

## User Scenarios & Testing

### User Story 1 - Transformar texto para maiúsculas (Priority: P1)

Como usuário, quero enviar uma pergunta contendo o comando `upper` para receber o
mesmo texto integralmente em maiúsculas.

**Why this priority**: É o caminho principal de transformação demonstrado no projeto.

**Independent Test**: Enviar uma requisição válida com `upper` e comparar a resposta
com a versão em maiúsculas do texto enviado.

**Acceptance Scenarios**:

1. **Given** uma requisição válida cujo `question` contém `upper`, **When** a
   aplicação processa a requisição, **Then** responde com status de sucesso e o texto
   completo convertido para maiúsculas.
2. **Given** uma pergunta com `UPPER` em qualquer combinação de caixa, **When** ela
   é processada, **Then** o comando é reconhecido e o resultado é equivalente à
   conversão para maiúsculas.

---

### User Story 2 - Transformar texto para minúsculas (Priority: P1)

Como usuário, quero enviar uma pergunta contendo o comando `lower` para receber o
mesmo texto integralmente em minúsculas.

**Why this priority**: É o segundo caminho funcional explícito da referência.

**Independent Test**: Enviar uma requisição válida com `lower` e comparar a resposta
com a versão em minúsculas do texto enviado.

**Acceptance Scenarios**:

1. **Given** uma requisição válida cujo `question` contém `lower`, **When** a
   aplicação processa a requisição, **Then** responde com status de sucesso e o texto
   completo convertido para minúsculas.
2. **Given** uma pergunta com `LOWER` em qualquer combinação de caixa, **When** ela
   é processada, **Then** o comando é reconhecido e o resultado é equivalente à
   conversão para minúsculas.

---

### User Story 3 - Orientar comandos desconhecidos (Priority: P1)

Como usuário, quero receber uma orientação quando minha pergunta não contém um
comando reconhecido.

**Why this priority**: O fallback é um caminho observável e coberto pela referência.

**Independent Test**: Enviar uma pergunta válida sem `upper` nem `lower` e comparar
a resposta com a mensagem de fallback definida.

**Acceptance Scenarios**:

1. **Given** uma pergunta válida sem os termos `upper` e `lower`, **When** ela é
   processada, **Then** responde com status de sucesso e exatamente a mensagem:
   `Unknown command. Try 'make this uppercase' or 'convert to lowercase'`.
2. **Given** uma pergunta que contém os termos `upper` e `lower`, **When** ela é
   processada, **Then** o caminho `upper` prevalece e o texto é convertido para
   maiúsculas.

### Edge Cases

- Corpo sem o campo `question`: a requisição deve ser rejeitada como entrada inválida.
- `question` não textual: a requisição deve ser rejeitada como entrada inválida.
- `question` textual com menos de cinco caracteres: a requisição deve ser rejeitada
  como entrada inválida.
- `question` com exatamente cinco caracteres: a requisição é válida e segue o fluxo
  normal.
- `question` com espaços, pontuação ou acentos: esses caracteres devem ser preservados
  durante a transformação, exceto a alteração de caixa.
- `question` vazia ou somente composta por espaços: deve ser rejeitada pela regra de
  tamanho mínimo, quando tiver menos de cinco caracteres; caso tenha cinco ou mais,
  não deve ser tratada como comando conhecido.
- Erro inesperado durante o processamento: a interface deve retornar erro HTTP 500 sem
  expor credenciais ou detalhes sensíveis.

## Requirements

### Functional Requirements

- **FR-001**: A aplicação MUST disponibilizar uma operação HTTP `POST /chat`.
- **FR-002**: A operação MUST exigir um corpo com o campo `question`.
- **FR-003**: `question` MUST ser textual e conter pelo menos cinco caracteres.
- **FR-004**: A aplicação MUST reconhecer `upper` quando o termo aparecer na
  pergunta, sem distinção de maiúsculas e minúsculas.
- **FR-005**: A aplicação MUST reconhecer `lower` quando o termo aparecer na
  pergunta, sem distinção de maiúsculas e minúsculas.
- **FR-006**: Quando `upper` for reconhecido, a aplicação MUST converter a pergunta
  completa para maiúsculas, preservando conteúdo não relacionado a caixa.
- **FR-007**: Quando `lower` for reconhecido e `upper` não for reconhecido, a
  aplicação MUST converter a pergunta completa para minúsculas, preservando conteúdo
  não relacionado a caixa.
- **FR-008**: Quando nenhum comando for reconhecido, a aplicação MUST retornar
  exatamente `Unknown command. Try 'make this uppercase' or 'convert to lowercase'`.
- **FR-009**: A aplicação MUST aplicar a precedência de `upper` quando os dois termos
  aparecem na mesma pergunta.
- **FR-010**: O fluxo MUST representar conceitualmente um estado com mensagens,
  comando identificado e saída produzida.
- **FR-011**: O fluxo MUST separar conceitualmente identificação, roteamento, execução
  do comando e produção da resposta final.
- **FR-012**: Respostas bem-sucedidas MUST retornar a saída textual do fluxo, sem exigir
  que o consumidor conheça o estado interno do grafo.
- **FR-013**: Entradas inválidas MUST produzir resposta HTTP de erro sem executar uma
  transformação válida.
- **FR-014**: A execução local MUST ser documentada com as variáveis de ambiente
  necessárias, quando houver, e exemplos de requisição.
- **FR-015**: O projeto MUST manter a referência TypeScript intacta e a implementação
  Python independente.

### Key Entities

- **Pergunta**: texto enviado pelo usuário; contém a entrada a ser analisada e, quando
  aplicável, transformada.
- **Estado do fluxo**: representação conceitual das mensagens, do comando identificado
  e da saída intermediária/final.
- **Comando**: classificação entre `uppercase`, `lowercase` e `unknown`.
- **Resposta**: texto final devolvido ao usuário, seja transformação ou fallback.

## Requisitos não funcionais

- **NFR-001**: O comportamento MUST ser determinístico para a mesma entrada.
- **NFR-002**: A solução MUST permanecer simples e didática, sem introduzir
  persistência, autenticação ou dependências não necessárias ao fluxo.
- **NFR-003**: A aplicação MUST permitir execução local repetível a partir da documentação.
- **NFR-004**: Os testes MUST poder validar o fluxo sem depender de uma API externa de
  LLM.
- **NFR-005**: Mensagens de erro MUST ser compreensíveis e não revelar segredos.
- **NFR-006**: A implementação MUST seguir as decisões de governança da jornada,
  incluindo gerenciamento de dependências por Poetry e uso idiomático de Python.

## Conceitos de IA e integração demonstrados

- Mensagens humanas e de resposta como representação conceitual de uma conversa.
- Estado compartilhado entre etapas de um fluxo.
- Nós com responsabilidades pequenas e explícitas.
- Roteamento condicional baseado em uma intenção identificada.
- Compilação/execução de um grafo de processamento.
- Separação entre lógica de classificação, transformação e resposta.

A referência não demonstra inferência por LLM, prompt template, memória persistente,
ferramentas, RAG ou agentes. Esses conceitos não devem ser simulados apenas para
aumentar a complexidade da baseline.

## Configuração

- A execução local MUST documentar o endereço e a porta utilizados pela aplicação.
- A configuração MUST ser fornecida por ambiente quando o runtime precisar de valores
  externos.
- Nenhuma API key ou credencial real MUST ser necessária para os três fluxos funcionais
  desta especificação.
- Caso o ambiente de execução ofereça integração opcional de observabilidade, seus
  nomes de variáveis e valores fictícios podem ser documentados sem incluir segredos.
- A configuração da referência para desenvolvimento de grafo é apenas uma pista de
  compatibilidade conceitual; a implementação Python não precisa reproduzir seu arquivo
  ou formato.

## Observabilidade

O código TypeScript analisado não configura LangSmith nem produz tracing explícito.
Consequentemente, tracing externo não é requisito funcional desta baseline.

A execução deve, contudo, permitir observar e testar os resultados dos três caminhos
principais: comando uppercase, comando lowercase e fallback. Se a implementação usar
um mecanismo de tracing compatível durante o desenvolvimento, ele deve registrar
somente o fluxo, o comando identificado e o resultado, sem conteúdo sensível além do
necessário para o estudo; isso não cria uma dependência obrigatória da versão 1.

## Testabilidade

Os testes devem cobrir:

- transformação para maiúsculas;
- transformação para minúsculas;
- fallback para comando desconhecido;
- reconhecimento sem distinção de caixa;
- precedência de `upper`;
- validação de campo ausente, tipo inválido e tamanho mínimo;
- preservação de pontuação, espaços e acentos nas transformações;
- retorno de erro para falha inesperada, sem exigir acesso a LLM externo.

Os testes devem verificar status HTTP e conteúdo observável da resposta. Não devem exigir
nomes de funções, classes, módulos ou detalhes internos específicos.

## Fora do escopo

- Chamadas a modelos de linguagem ou seleção de provider.
- Prompts, prompt templates ou geração de texto por LLM.
- RAG, embeddings, bancos vetoriais e recuperação de documentos.
- Neo4j ou qualquer banco de dados.
- Agentes, ferramentas, memória persistente ou arquiteturas multiagente.
- Prompt injection, safeguards, moderação ou políticas de segurança de conteúdo.
- Autenticação, autorização, usuários persistentes ou interface gráfica.
- Streaming, histórico persistente, sessões e respostas multimodais.
- Deploy em nuvem, containers e escalabilidade de produção.
- Tracing obrigatório, dashboards ou métricas de produção no LangSmith.
- Tradução literal de nomes, APIs, diretórios ou interfaces do projeto TypeScript.
- Alterações no diretório `../versao-typescript`.
- Funcionalidades dos próximos projetos que não sejam necessárias à baseline.

## Critérios de aceitação

- **AC-001**: Uma requisição válida com `question` contendo `upper` retorna status
  200 e a pergunta completa em maiúsculas.
- **AC-002**: Uma requisição válida com `question` contendo `lower`, sem `upper`,
  retorna status 200 e a pergunta completa em minúsculas.
- **AC-003**: Uma requisição válida sem os termos reconhecidos retorna status 200 e a
  mensagem de fallback exata.
- **AC-004**: Os termos de comando são reconhecidos independentemente da caixa.
- **AC-005**: Quando ambos aparecem, o resultado segue o comando `upper`.
- **AC-006**: Campo ausente, tipo não textual e texto com menos de cinco caracteres
  resultam em erro de validação e não em resposta transformada.
- **AC-007**: Pontuação, espaços e acentos do texto permanecem presentes após a
  transformação, com alteração apenas de caixa.
- **AC-008**: Os três caminhos principais são demonstráveis por testes automatizados sem
  credencial ou serviço externo.
- **AC-009**: A documentação permite iniciar a aplicação localmente e enviar uma
  requisição de exemplo.
- **AC-010**: A implementação mantém a referência TypeScript sem modificações.

## Critérios de sucesso

### Measurable Outcomes

- **SC-001**: 100% dos três caminhos principais da referência (uppercase, lowercase e
  fallback) produzem as respostas esperadas nos testes automatizados.
- **SC-002**: 100% dos casos de validação definidos para campo ausente, tipo inválido e
  tamanho menor que cinco são rejeitados sem transformação.
- **SC-003**: Pelo menos 95% de um grupo de 20 entradas válidas de teste é processado
  em até 1 segundo em execução local; todas as entradas devem produzir uma resposta
  determinística.
- **SC-004**: Uma pessoa que siga a documentação consegue iniciar a aplicação e executar
  uma requisição de cada caminho em até 10 minutos, sem credenciais reais.
- **SC-005**: Todos os testes automatizados relevantes passam em uma execução local
  limpa, e nenhum teste depende de disponibilidade de um provedor de LLM.
- **SC-006**: Uma revisão didática confirma a presença identificável dos conceitos de
  estado, nós, roteamento condicional e resposta, sem exigir funcionalidades fora do
  escopo.

## Assumptions

- O consumidor conhece HTTP básico ou seguirá os exemplos documentados.
- A execução local dispõe de Python e Poetry conforme a Constitution do projeto.
- A porta padrão pode ser definida pela implementação e documentada; o comportamento
  funcional não depende de um número específico de porta.
- A comparação de tamanho considera o texto recebido, antes de qualquer transformação.
- A identificação é baseada na presença textual dos termos, como na referência, e não
  em classificação semântica por modelo.
- A mensagem de fallback é parte do comportamento observável e deve permanecer estável
  nesta etapa.
- LangSmith não é uma dependência obrigatória porque não é usado pela referência
  analisada; sua inclusão futura será uma decisão de evolução, não desta baseline.

## Considerações para evolução futura

A baseline deve manter separadas as responsabilidades conceituais de entrada,
identificação, roteamento, transformação e resposta para permitir que etapas futuras
substituam a identificação textual por um modelo ou adicionem novos caminhos sem
alterar os contratos básicos desnecessariamente.

Qualquer evolução futura deve ser especificada separadamente e respeitar o escopo
da disciplina. A introdução de LLM, LangSmith, persistência, RAG ou novas integrações
deve ocorrer somente quando apresentada pela próxima etapa e acompanhada de requisitos,
configuração, testes e registro das diferenças em relação à baseline.

