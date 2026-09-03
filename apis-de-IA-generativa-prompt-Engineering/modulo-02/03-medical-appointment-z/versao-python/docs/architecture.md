# Arquitetura permanente do template Python

Este projeto é a base evolutiva dos próximos módulos. Novas aulas devem adicionar conceitos dentro
das responsabilidades existentes, preservando o fluxo e evitando uma segunda arquitetura.

## Camadas

```text
API → Graph → Nodes → Services → LangChain/LLM → Provider
```

- `api/` contém apenas FastAPI, validação de entrada e serialização HTTP.
- `config/` carrega variáveis de ambiente e não contém regras de negócio.
- `domain/models/` contém entidades e contratos do domínio.
- `domain/services/` contém efeitos e validações determinísticas do negócio.
- `graph/` contém `GraphState`, router, nodes e definição do `StateGraph`.
- `llm/` contém contratos Pydantic, a abstração `MedicalLLM` e integrações.
- `prompts/` contém templates versionados e independentes da orquestração.
- `factory/` é o Composition Root: cria, conecta e injeta as dependências.

## Regras para as próximas aulas

1. `GraphState` transporta dados; não carrega serviços ou regras de negócio.
2. Nodes têm responsabilidade única e dependem de abstrações injetadas.
3. O LLM interpreta e estrutura dados; serviços Python decidem e executam regras.
4. Structured Output deve ser validado com Pydantic antes de chegar ao router ou domínio.
5. O LangGraph é o orquestrador do fluxo; conditional edges devem ser explícitas.
6. OpenRouter e outras integrações externas ficam atrás de interfaces substituíveis.
7. Testes unitários usam fakes e não dependem de rede, credenciais ou provider externo.
8. Segredos vêm exclusivamente do ambiente; `.env.example` nunca contém credenciais reais.
9. Classes, funções e métodos novos ou modificados possuem docstrings em português.
10. Comentários explicam conceitos e decisões arquiteturais, não linhas óbvias.
11. Componentes existentes devem ser evoluídos antes de criar duplicações.
12. O TypeScript permanece referência somente leitura.

## Compatibilidade durante a evolução

Os módulos históricos diretamente em `src/app/` são fachadas quando a
responsabilidade já possui um pacote canônico. Eles não devem receber novas
regras: servem apenas para que exemplos anteriores continuem funcionando
durante a migração gradual do template.

## Composição e substituição

```text
Factory
 ├── LLMConfig → OpenRouterMedicalLLM | FakeMedicalLLM | OfflineMedicalLLM
 ├── AppointmentService
 ├── nodes
 └── StateGraph compilado
```

A troca do LLM não deve exigir alterações nos nodes. A troca do serviço de domínio não deve exigir
alterações no router. Essa propriedade é validada por testes determinísticos.
