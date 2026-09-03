# Research: Medical Appointment com LLM

## Decision: Cliente compatível com OpenAI apontado para OpenRouter

**Rationale**: OpenRouter documenta um endpoint compatível com OpenAI, autenticação Bearer e headers opcionais `HTTP-Referer` e `X-Title`. A integração preserva o conceito da referência TypeScript sem acoplar o domínio a um SDK específico do provider.

**Alternatives considered**: SDK dedicado (mais acoplamento); chamada HTTP manual (perde a abstração LangChain); outro provider (não preserva o objetivo da aula).

## Decision: `with_structured_output` com modelos Pydantic

**Rationale**: A documentação atual do LangChain Python apresenta `with_structured_output(Model)` para transformar a resposta em instância Pydantic. `include_raw=True` permite capturar resposta original e erro de parsing. Isso mantém o schema como contrato explícito e didático.

**Alternatives considered**: JSON no prompt com `json.loads` (menos seguro); agente com ferramentas (complexidade sem necessidade); texto livre (não atende Structured Output).

## Decision: `TypedDict` para GraphState e `StateGraph` compilado

**Rationale**: O projeto já usa `TypedDict`, `add_messages`, `START`, `END` e `StateGraph`. A documentação confirma que o grafo deve declarar estado, nodes e edges, ser compilado e usar conditional edges para decisões baseadas no estado.

**Alternatives considered**: agente prebuilt (oculta o fluxo); estado somente em mensagens (dificulta demonstrar extração); router com nomes livres do modelo (risco de caminho inválido).

## Decision: Serviço LLM com protocolo e implementação real separadas

**Rationale**: O protocolo permite fake determinístico, enquanto a implementação real concentra configuração, endpoint, structured output e tratamento de provider. Nodes permanecem responsáveis por orquestração.

**Alternatives considered**: modelo direto em cada node (acoplamento); mock global (menos didático); manter regex (não implementa a feature).

## Decision: Provider real opt-in

**Rationale**: Testes locais devem funcionar sem segredo, rede ou custo. Um teste isolado valida a integração sem tornar a suíte determinística dependente de disponibilidade externa.

**Alternatives considered**: chamadas reais em todos os testes (instáveis); remover teste real (não valida integração); simular endpoint (não comprova provider).

## Decision: Fallback seguro no nó de mensagem

**Rationale**: A operação de domínio pode concluir antes de uma falha na geração. O estado deve preservar o resultado e retornar uma mensagem fixa não vazia, sem relatar falsamente que a operação não ocorreu.

**Alternatives considered**: propagar exceção após agendar (contrato enganoso); mensagem vazia; retry indefinido (fora do escopo).

## Decision: Configuração por ambiente

**Rationale**: `.env.example` documenta nomes sem segredos e o ambiente fornece valores. O grafo deve ser importável em testes sem API key; a validação da chave fica sob demanda do cliente real.

**Alternatives considered**: hardcode (inseguro); exigir provider na importação (quebra testes/CLI); arquivo versionado com valores reais (risco de segredo).

## Documentation references consulted

- LangChain OSS Python: Structured Output com Pydantic e captura de erros de parsing.
- LangGraph Python: `StateGraph`, `TypedDict`, compilação e conditional edges.
- OpenRouter docs: endpoint compatível com OpenAI, autenticação, headers e provider routing.
