# Data Model: Medical Appointment com LLM

## IntentExtraction

Resultado estruturado da primeira chamada ao LLM.

| Campo | Tipo conceitual | Obrigatório | Regras |
|---|---|---:|---|
| `intent` | enum | sim | Somente `schedule`, `cancel` ou `unknown`. |
| `professionalId` (`professional_id` em Python) | inteiro | não | Deve corresponder a profissional existente quando informado. |
| `professional_name` | texto | não | Nome reconhecido/apresentado ao usuário. |
| `patientName` (`patient_name` em Python) | texto | não | Nome extraído, sem assumir identidade quando ausente. |
| `datetime` | data/hora normalizada | não | Validada quanto a formato, fuso e futuro antes do domínio. |
| `reason` | texto | não | Usado principalmente no agendamento. |

Saída inválida ou não parseável resulta em falha segura/`unknown`. Uma extração pode ser estruturalmente válida e ainda estar incompleta para uma ação; nesse caso a intenção permanece `schedule` ou `cancel`, o node correspondente não chama o domínio e registra `actionSuccess=false` com os campos ausentes.

## Campos necessários por intenção

| Intenção | Campos obrigatórios para executar o domínio | Campos opcionais |
|---|---|---|
| `schedule` | `professionalId`, `datetime`, `patientName` | `reason` |
| `cancel` | `professionalId`, `datetime`, `patientName` | nenhum necessário |

Os nomes acima são os nomes do contrato semântico/Structured Output; o código Python pode usar `snake_case`. A ausência de qualquer campo obrigatório não deve ser convertida em `intent="unknown"`. `unknown` é reservado principalmente para intenção não identificada, ambiguidade ou falha na identificação.

## MessageGeneration

Resultado estruturado da chamada de geração final.

| Campo | Tipo conceitual | Obrigatório | Regras |
|---|---|---:|---|
| `message` | texto | sim | Não vazio, preferencialmente em português e coerente com cenário/resultado. |

## GraphState

Estado efêmero de uma invocação.

| Campo | Tipo conceitual | Origem/uso |
|---|---|---|
| `messages` | lista de mensagens | Entrada humana e resposta de IA; combinada pelo reducer de mensagens. |
| `visited` | lista de nomes | Rastreabilidade didática e testes de caminho. |
| `output` | texto | Resposta final normalizada para a API. |
| `intent` | enum opcional | Resultado de `identify_intent` e entrada do router. |
| `patient_name` | texto opcional | Extração para domínio. |
| `professional_id` | inteiro opcional | Extração/validação para domínio. |
| `professional_name` | texto opcional | Contexto da operação e da mensagem. |
| `datetime` | data/hora opcional | Dado normalizado para domínio. |
| `reason` | texto opcional | Motivo do agendamento. |
| `action_success` | booleano opcional | Resultado de scheduler/canceller. |
| `action_error` | texto opcional | Erro de regra de negócio ou dados ausentes. |
| `appointment_data` | objeto opcional | Consulta criada/removida serializável para a API. |
| `error` | texto opcional | Erro de interpretação/provider/validação. |
| `catalog` | serviço de domínio | Dependência em memória isolada por invocação/teste. |

## LLMConfig

Configuração exclusiva do gateway OpenRouter: API key, modelo, base URL, headers, temperatura, `LLM_TIMEOUT_SECONDS` e configurações OpenRouter aplicáveis. O timeout padrão é 30 segundos e pode ser sobrescrito por ambiente. Não há mecanismo genérico de múltiplos providers, fallback entre providers ou ordenação adicional de modelos. A API key nunca deve aparecer em logs, modelos serializados ou arquivos versionados.

## Entidades de domínio

`Professional` identifica o profissional e sua especialidade. `Appointment` associa profissional, paciente, data/hora e motivo. `AppointmentCatalog` mantém as entidades em memória e aplica existência, data futura, disponibilidade e correspondência de cancelamento.

## State transitions

```text
initial → identify_intent → schedule | cancel | message → message → final
```

O router só aceita `schedule`, `cancel` ou `message`. Erro de identificação produz `intent="unknown"` e vai para `message`; ausência de campos necessários após uma intenção identificada não altera a intenção, e scheduler/canceller registram `actionSuccess=false` e `actionError` sem chamar o domínio.
