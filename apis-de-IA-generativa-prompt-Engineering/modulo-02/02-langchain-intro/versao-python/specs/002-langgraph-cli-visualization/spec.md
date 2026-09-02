# Feature Specification: Suporte ao LangGraph CLI e visualização do grafo

**Feature Branch**: `002-langgraph-cli-visualization`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Evoluir o projeto 001-langchain-intro-python adicionando suporte ao ambiente de desenvolvimento do LangGraph CLI, permitindo iniciar o grafo localmente e visualizá-lo através das ferramentas oficiais de desenvolvimento do LangGraph."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Iniciar e visualizar o grafo (Priority: P1)

Como estudante, quero iniciar o ambiente de desenvolvimento local e visualizar o workflow para relacionar o código Python à representação gráfica do grafo.

**Why this priority**: É o objetivo central da evolução e permite validar a configuração do CLI de forma independente.

**Independent Test**: Com as dependências instaladas pelo Poetry, executar `poetry run langgraph dev`, abrir a URL de desenvolvimento informada pelo comando e confirmar que o workflow é carregado e visualizável.

**Acceptance Scenarios**:

1. **Given** o projeto está na raiz e suas dependências estão instaladas, **When** o estudante executa `poetry run langgraph dev`, **Then** o servidor de desenvolvimento inicia sem erro de configuração.
2. **Given** o servidor de desenvolvimento está em execução, **When** o estudante acessa a interface oficial de desenvolvimento, **Then** o workflow do grafo existente é apresentado para inspeção e execução.
3. **Given** a configuração do projeto, **When** o CLI procura o arquivo de configuração, **Then** encontra `langgraph.json` na raiz e identifica o objeto `graph` existente em `src/langchain_intro/graph.py`.

### User Story 2 - Explorar os caminhos do workflow (Priority: P1)

Como estudante, quero executar entradas que percorram os caminhos uppercase, lowercase e fallback para observar o roteamento condicional e comparar os resultados com a aplicação atual.

**Why this priority**: A visualização só entrega o valor didático esperado quando preserva o comportamento observável do grafo.

**Independent Test**: Executar no ambiente de desenvolvimento uma entrada para cada comando suportado e uma entrada desconhecida, verificando nós visitados e saída final.

**Acceptance Scenarios**:

1. **Given** uma entrada que solicita conversão para maiúsculas, **When** ela é executada no ambiente de desenvolvimento, **Then** o caminho passa por `identify_intent` e `uppercase`, segue para `append_response` e converte integralmente a entrada para maiúsculas.
2. **Given** uma entrada que solicita conversão para minúsculas, **When** ela é executada no ambiente de desenvolvimento, **Then** o caminho passa por `identify_intent` e `lowercase`, segue para `append_response` e converte integralmente a entrada para minúsculas.
3. **Given** uma entrada que não corresponde aos comandos conhecidos, **When** ela é executada no ambiente de desenvolvimento, **Then** o caminho passa por `identify_intent` e `fallback`, segue para `append_response` e retorna exatamente `Unknown command. Try 'make this uppercase' or 'convert to lowercase'`.
4. **Given** o workflow carregado, **When** o estudante inspeciona sua representação, **Then** identifica `identify_intent`, `uppercase`, `lowercase`, `fallback` e `append_response`, além das transições condicionais para os três caminhos.

### User Story 3 - Continuar usando a aplicação existente (Priority: P1)

Como desenvolvedor, quero que o novo ambiente de desenvolvimento seja complementar à aplicação HTTP existente para continuar usando e testando o endpoint sem alteração de contrato.

**Why this priority**: A feature é uma evolução do projeto e não pode interromper a baseline nem misturar os papéis dos dois ambientes.

**Independent Test**: Iniciar a aplicação FastAPI pelo procedimento existente, enviar requisições a `POST /chat` e confirmar os mesmos resultados de `graph.invoke()` enquanto a configuração do CLI permanece disponível.

**Acceptance Scenarios**:

1. **Given** a aplicação existente configurada, **When** o cliente envia uma requisição válida a `POST /chat`, **Then** a resposta continua sendo produzida pelo mesmo grafo e mantém o contrato funcional atual.
2. **Given** o ambiente de desenvolvimento do LangGraph não está em execução, **When** a aplicação FastAPI é iniciada, **Then** o endpoint continua funcionando de forma independente.
3. **Given** o servidor de desenvolvimento está em execução, **When** a aplicação FastAPI é iniciada separadamente, **Then** os dois ambientes coexistem sem substituir um ao outro.

### Edge Cases

- O CLI deve apresentar erro claro de configuração se o arquivo de configuração estiver inválido ou se o objeto de grafo indicado não puder ser importado; a feature não deve criar um grafo alternativo para mascarar esse erro.
- A execução de uma entrada desconhecida deve seguir o caminho `fallback` e preservar a mensagem exata, sem exigir modelo, provider, credencial ou API key.
- A ausência de variáveis de ambiente de provedores de LLM não deve impedir o carregamento nem a execução do grafo determinístico.
- O funcionamento do endpoint `POST /chat` não deve depender de o processo `langgraph dev` estar ativo.
- Dependências já usadas pela aplicação e pelos testes devem continuar instaláveis pelo Poetry junto com o CLI.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O projeto MUST disponibilizar configuração compatível com a versão atual do LangGraph CLI documentada para desenvolvimento local.
- **FR-002**: O projeto MUST possuir um arquivo `langgraph.json` válido na raiz do projeto.
- **FR-003**: O arquivo `langgraph.json` MUST identificar o grafo executável existente em `src/langchain_intro/graph.py:graph`, sem criar uma implementação paralela.
- **FR-004**: O projeto MUST continuar utilizando Poetry para declarar e instalar suas dependências.
- **FR-005**: A configuração MUST preservar Python 3.13.12 e o uso de pyenv definido pela baseline.
- **FR-006**: O projeto MUST permitir iniciar o ambiente local por meio de `poetry run langgraph dev` sem erro de configuração.
- **FR-007**: O ambiente MUST carregar o grafo existente sem alterar sua implementação funcional.
- **FR-008**: A representação visual MUST permitir identificar os nodes `identify_intent`, `uppercase`, `lowercase`, `fallback` e `append_response`.
- **FR-009**: A representação e a execução MUST preservar o roteamento condicional de `identify_intent` para `uppercase`, `lowercase` e `fallback`, com todos os caminhos convergindo em `append_response` antes de `END`.
- **FR-010**: As execuções pelo ambiente de desenvolvimento MUST produzir os mesmos resultados funcionais definidos pela baseline de `graph.invoke()`.
- **FR-011**: O caminho `uppercase` MUST converter integralmente a entrada para maiúsculas.
- **FR-012**: O caminho `lowercase` MUST converter integralmente a entrada para minúsculas.
- **FR-013**: O caminho `fallback` MUST retornar exatamente `Unknown command. Try 'make this uppercase' or 'convert to lowercase'`.
- **FR-014**: A configuração MUST permitir carregar e executar o grafo sem LLM, provider de LLM ou API key.
- **FR-015**: A aplicação FastAPI existente e seu endpoint `POST /chat` MUST continuar funcionando independentemente do ambiente de desenvolvimento do LangGraph.
- **FR-016**: A documentação MUST explicar como instalar dependências e iniciar o LangGraph Dev usando Poetry.
- **FR-017**: A documentação MUST diferenciar FastAPI como servidor HTTP da aplicação e LangGraph Dev como ambiente de desenvolvimento, visualização e execução do workflow.
- **FR-018**: A documentação MUST explicar como `langgraph.json` identifica e carrega o grafo Python existente.
- **FR-019**: A documentação MUST apresentar os conceitos State, Node, Edge, Conditional Edge, StateGraph, `compile()`, `invoke()`, `langgraph.json`, LangGraph CLI e `langgraph dev`.
- **FR-020**: A documentação MUST apresentar o fluxo `START → identify_intent → conditional routing → (uppercase | lowercase | fallback) → append_response → END` e explicar que a interface representa graficamente nodes e edges definidos no código.
- **FR-021**: Os testes automatizados MUST cobrir carregamento pelo CLI, nodes esperados, roteamento condicional, os três caminhos, ausência de dependência de LLM e a continuidade do FastAPI e do `POST /chat`.
- **FR-022**: A evolução MUST preservar os testes existentes e MUST NOT modificar `../versao-typescript`.

### Key Entities

- **Grafo executável**: O workflow determinístico já existente, identificado pelo nome `graph`, que contém estado, nodes, edges e resultado compilado.
- **Configuração do ambiente de desenvolvimento**: O arquivo na raiz que associa um nome de grafo ao módulo Python e declara as dependências necessárias para carregá-lo localmente.
- **Execução do workflow**: Uma entrada submetida ao grafo, com o caminho condicional percorrido e o estado/resultado final observável.
- **Aplicação HTTP**: A aplicação FastAPI existente que expõe `POST /chat` e permanece independente do servidor de desenvolvimento do grafo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um desenvolvedor com Python 3.13.12, pyenv e Poetry configurados consegue instalar as dependências e iniciar o ambiente de desenvolvimento com um único comando documentado, `poetry run langgraph dev`, sem editar código-fonte.
- **SC-002**: Em 100% das execuções de validação, o ambiente de desenvolvimento carrega o grafo existente e apresenta os cinco nodes esperados e seus três caminhos condicionais.
- **SC-003**: Em 100% dos casos de teste de uppercase, lowercase e fallback, os resultados do ambiente de desenvolvimento são idênticos aos resultados de referência obtidos pela aplicação existente.
- **SC-004**: Em 100% dos casos de teste da baseline, a aplicação HTTP e o endpoint `POST /chat` continuam operacionais sem que o servidor de desenvolvimento do grafo esteja ativo.
- **SC-005**: Um estudante consegue, seguindo apenas o README, distinguir os dois modos de execução e identificar a relação entre cada node visualizado e o código correspondente em até 10 minutos.
- **SC-006**: Nenhuma execução dos cenários determinísticos de validação solicita credenciais, API keys ou configuração de provider de LLM.

## Assumptions

- A baseline do projeto já contém o objeto compilado `graph` em `src/langchain_intro/graph.py` e seus contratos de entrada e saída permanecerão inalterados.
- O CLI será instalado como dependência gerenciada pelo Poetry, usando o extra recomendado pela documentação oficial atual para o servidor local em memória.
- O formato de configuração adotado seguirá a documentação oficial atual: `langgraph.json` declarará as dependências locais, o mapeamento de nome para `módulo:objeto` e, quando necessário, o arquivo de ambiente sem incluir segredos.
- O ambiente local será usado para desenvolvimento e visualização; publicação, hospedagem remota, autenticação, observabilidade avançada e colaboração multiusuário estão fora desta etapa.
- A interface oficial disponibilizada pelo comando poderá evoluir independentemente do projeto; a obrigação desta feature é entregar configuração válida, carregamento, visualização e execução local pelos meios oficiais.
- Os testes serão executados em ambiente com dependências instaláveis e sem exigir acesso a serviços externos de LLM.

## Out of Scope

- Adicionar LLM, provider, API key, LangSmith como dependência direta, RAG, agentes, ferramentas, memória persistente ou banco de dados.
- Substituir Poetry por uv ou substituir FastAPI.
- Reescrever, duplicar ou alterar funcionalmente o grafo da baseline.
- Alterar qualquer arquivo da versão TypeScript.
- Implementar publicação, deploy remoto ou funcionalidades de etapas posteriores da jornada.
