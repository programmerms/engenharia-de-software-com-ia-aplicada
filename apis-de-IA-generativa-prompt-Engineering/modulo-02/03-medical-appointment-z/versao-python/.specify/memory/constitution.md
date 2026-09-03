<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: none; initial constitution adopted with Principles I–XVII
- Added sections: Context, Scope, Stage Completion Criteria and Template Python Architectural Standard
- Removed sections: none
- Follow-up TODOs: confirm the original ratification date
-->

# Jornada IA com Python Constitution

## Core Principles

### I. Aprendizado orienta a implementação

A implementação MUST priorizar a compreensão dos conceitos apresentados na aula. O código MUST
ser suficientemente simples e explícito para estudo. Abstrações, padrões e otimizações MUST NOT
ser introduzidos sem justificativa relacionada ao projeto ou ao conteúdo estudado.

### II. Python como linguagem principal

Todos os projetos MUST utilizar Python como linguagem principal, seguindo práticas idiomáticas,
clareza, legibilidade e simplicidade. A implementação MUST NOT reproduzir artificialmente
estruturas específicas do TypeScript.

### III. Stack tecnológica

Python, FastAPI, Poetry, LangChain, LangGraph e LangSmith constituem a stack base e MUST ser
utilizados quando pertinentes ao projeto e à aula. Dependências adicionais MUST possuir
necessidade real e justificável.

### IV. Poetry como gerenciamento de projeto

Poetry MUST gerenciar dependências, ambiente, metadados e versões. As dependências MUST ser
declaradas no `pyproject.toml`. Múltiplos mecanismos de gerenciamento MUST NOT ser usados sem
justificativa explícita.

### V. FastAPI

FastAPI MUST ser usado quando o projeto necessitar de interface web ou API. Exemplos didáticos
sem essa necessidade MUST NOT ser expostos artificialmente como endpoints.

### VI. Reconstrução conceitual, não tradução literal

A implementação Python MUST preservar intenção, conceitos, comportamento, fluxo, entradas,
saídas e objetivos didáticos da referência TypeScript. Ela MAY alterar diretórios, nomes,
interfaces, padrões e APIs para utilizar abordagens idiomáticas e atuais de Python.

### VII. APIs atuais e documentação oficial

Antes de implementar componentes de LangChain, LangGraph ou LangSmith, a documentação oficial
atual MUST ser consultada. APIs deprecated MUST NOT ser usadas apenas para reproduzir a
referência; diferenças relevantes MUST ser registradas para o aprendizado.

### VIII. Evolução incremental

Cada etapa MUST preservar componentes relevantes anteriores e adicionar somente os conceitos
necessários à etapa atual. Funcionalidades futuras, incluindo RAG, bancos vetoriais, Neo4j,
safeguards, prompt injection e análise de documentos, MUST permanecer fora do escopo até serem
apresentadas ou exigidas.

### IX. Projeto original como referência

O projeto TypeScript da disciplina MUST ser analisado antes da implementação Python. A análise
MUST identificar conceitos, comportamento, fluxo, componentes, dependências, testes,
configurações e integrações, servindo de base para a especificação Python.

### X. Configuração e segredos

API keys, credenciais e outras informações sensíveis MUST ser obtidas por variáveis de ambiente
ou `.env` quando apropriado. Segredos reais MUST NOT ser versionados. Quando necessário,
`.env.example` MUST conter somente nomes de variáveis e valores fictícios ou vazios.

### XI. Testabilidade

Funcionalidades relevantes MUST possuir testes automatizados quando tecnicamente aplicável.
Testes MUST validar comportamento, não detalhes internos desnecessários, e MUST NOT ser removidos
sem justificativa.

### XII. Transparência das decisões

Decisões relevantes e diferenças significativas em relação ao TypeScript MUST ser documentadas,
registrando o comportamento original, a implementação Python, a razão da diferença e o conceito
equivalente preservado.

### XIII. Código didático antes de código excessivamente abstrato

Clareza didática MUST prevalecer sobre abstrações prematuras. O projeto MUST evitar frameworks,
camadas, padrões e generalizações sem benefício demonstrável para a etapa atual.

### XIV. Integridade da evolução

Cada etapa MUST terminar funcional e compreensível: testes executáveis, dependências declaradas,
documentação e configuração atualizadas, e funcionalidades existentes preservadas salvo mudança
explicitamente justificada.

### XV. Separação entre referência e implementação

`versao-typescript/` é a referência da pós-graduação e `versao-python/` é a implementação
independente. A versão TypeScript MUST NOT ser modificada como parte da implementação Python.

### XVI. Escopo controlado

Cada especificação MUST declarar explicitamente o escopo da etapa. Funcionalidades não exigidas
pelos requisitos atuais MUST permanecer fora da implementação, ainda que sejam tecnicamente
interessantes ou úteis no futuro.

### XVII. Critério de conclusão

Uma etapa MUST ser considerada concluída somente quando os conceitos previstos estiverem
implementados, o comportamento validado, os testes relevantes passando, a configuração
documentada, as diferenças importantes registradas e o projeto preparado para a próxima etapa.

### XVIII. Template Python evolutivo

O template Python MUST evoluir incrementalmente dentro de uma organização coesa por responsabilidade:
`api`, `config`, `domain`, `graph`, `llm`, `prompts` e `factory`. Componentes existentes MUST ser
evoluídos antes da criação de responsabilidades paralelas. A implementação MUST seguir Python
idiomático e manter `State = dados`, `Nodes = etapas de responsabilidade única`, `Services = regras
de negócio` e `Factory = composição e injeção de dependências`.

O LangGraph MUST permanecer o orquestrador do workflow, com routers e conditional edges explícitos.
O LLM MUST interpretar linguagem natural e produzir contratos estruturados validados por Pydantic;
regras de negócio MUST permanecer em serviços Python e texto livre do LLM MUST NOT decidir rotas ou
executar operações de domínio. Integrações externas MUST ficar atrás de abstrações substituíveis,
com testes determinísticos independentes de rede, credenciais e provider.

Segredos MUST vir exclusivamente do ambiente. Código novo ou modificado MUST possuir docstrings em
português para classes, funções e métodos, além de comentários didáticos nos pontos conceituais e
decisões arquiteturais, sem comentários redundantes. `versao-typescript/` MUST permanecer somente
como referência de leitura.

## Contexto, Escopo e Restrições

Este repositório integra uma jornada prática de aprendizado em Inteligência Artificial aplicada
à Engenharia de Software. Os projetos didáticos originalmente fornecidos em TypeScript/JavaScript
serão reconstruídos progressivamente em Python para compreender conceitos e APIs atuais, e não
para realizar uma tradução literal.

Esta Constitution é válida para os projetos Python da jornada. Especificações individuais podem
adicionar requisitos, mas MUST NOT violar estes princípios sem justificar explicitamente a
exceção. A versão TypeScript permanece fora do escopo de alteração.

## Desenvolvimento, Qualidade e Evolução

Antes de cada implementação, a referência original, a especificação e a documentação oficial
pertinente MUST ser consideradas. Durante a execução, decisões e diferenças relevantes MUST ser
registradas. Antes de avançar, testes, dependências, documentação e configuração MUST ser
verificados conforme o critério de conclusão.

Revisões de código e de artefatos MUST verificar aderência a esta Constitution, escopo controlado,
segurança de configuração, testabilidade e clareza didática. Qualquer exceção MUST documentar a
regra afetada, a justificativa, o impacto e, quando aplicável, o plano de retorno ou migração.

## Governance

Esta Constitution prevalece sobre práticas locais conflitantes. Uma alteração MUST ser proposta
como mudança explícita neste arquivo, incluir seu impacto no Sync Impact Report e atualizar a
versão e a data de emenda. A revisão MUST confirmar que princípios continuam declarativos,
testáveis e compatíveis com a evolução incremental da jornada.

Versionamento segue SemVer: MAJOR para remoção ou redefinição incompatível de princípios, MINOR
para novos princípios ou expansão material de orientação, e PATCH para esclarecimentos e
correções não semânticas. Cada implementação, revisão ou planejamento MUST avaliar conformidade;
descumprimentos MUST ser corrigidos ou justificados explicitamente.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): data original de adoção não fornecida | **Last Amended**: 2026-09-03
