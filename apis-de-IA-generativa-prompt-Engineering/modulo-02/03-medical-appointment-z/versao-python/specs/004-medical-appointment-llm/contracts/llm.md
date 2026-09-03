# Contract: LLM Service

## Intent extraction

Entrada: mensagem do usuário e contexto não sensível necessário ao prompt, como profissionais disponíveis e data de referência.

Saída aceita:

```text
IntentExtraction(
  intent="schedule" | "cancel" | "unknown",
  professionalId?: int,
  professional_name?: str,
  patientName?: str,
  datetime?: normalized datetime,
  reason?: str,
)
```

Parsing inválido, erro de transporte, timeout ou intenção fora do enum deve ser reportado como falha segura (`intent="unknown"` e erro); nunca como comando de node. A ausência de `professionalId`, `datetime` ou `patientName` em uma intenção já identificada é tratada pelo node de domínio, não como `unknown`.

Para `schedule`, `professionalId`, `datetime` e `patientName` são obrigatórios para executar; `reason` é opcional. Para `cancel`, os três primeiros são obrigatórios para localizar e cancelar.

## Message generation

Entrada: cenário (`schedule_success`, `schedule_error`, `cancel_success`, `cancel_error` ou `unknown`) e detalhes já validados.

Saída aceita:

```text
MessageGeneration(message: non-empty str)
```

## Configuration contract

- `OPENROUTER_API_KEY`: obrigatória somente para cliente real.
- `OPENROUTER_MODEL`: modelo selecionado.
- `OPENROUTER_BASE_URL`: default do endpoint OpenRouter.
- `OPENROUTER_HTTP_REFERER`: header opcional.
- `OPENROUTER_X_TITLE`: header opcional.
- `LLM_TEMPERATURE`: temperatura opcional.
- `LLM_TIMEOUT_SECONDS`: timeout em segundos, default `30`.
- `RUN_LLM_INTEGRATION_TESTS`: habilita teste real opt-in.

## Timeout determinístico

- Sem `LLM_TIMEOUT_SECONDS`, `LLMConfig.timeout` deve ser `30`.
- Com `LLM_TIMEOUT_SECONDS=10`, `LLMConfig.timeout` deve ser `10`.
- Um valor não numérico deve seguir o erro de configuração existente (`ValueError`); não deve iniciar chamada ao provider.
- Os testes devem validar esses casos por inspeção da configuração ou doubles, sem aguardar o timeout real.

## Provider e indisponibilidade

O caminho didático é exclusivamente `Python → LangChain → OpenRouter → LLM`. `OPENROUTER_API_KEY` é exigida apenas pelo cliente real. Não existe seleção genérica de providers, fallback automático entre providers ou estratégia própria de ordenação de modelos além das opções explicitamente configuradas no OpenRouter.

Quando o timeout é excedido, o serviço captura a exceção e mantém o processo ativo. A identificação retorna `unknown` com erro; o domínio não é chamado. Se a geração da mensagem falhar, o node usa uma mensagem determinística não vazia.
