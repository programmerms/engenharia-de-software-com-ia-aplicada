# Contract: HTTP Chat

## Endpoint

`POST /chat`

### Request

```json
{
  "question": "Sou Maria Santos e quero agendar uma consulta com Dr. Alicio da Silva amanhã às 16h para check-up"
}
```

Rules:

- `question` é obrigatório.
- Deve ser texto com pelo menos 10 caracteres.
- Pode usar diferentes formulações naturais de agendamento ou cancelamento.

Para executar `schedule`, a extração precisa conter `professionalId`, `datetime` e `patientName`; `reason` é opcional. Para executar `cancel`, os três mesmos campos são necessários. Dados ausentes produzem falha de ação (`success=false`) sem chamada ao domínio e não transformam automaticamente a intenção em `unknown`.

### Successful response

```json
{
  "intent": "schedule",
  "success": true,
  "message": "Sua consulta foi confirmada.",
  "appointment": {
    "professional_id": 1,
    "professional_name": "Dr. Alicio da Silva",
    "patient_name": "Maria Santos",
    "datetime": "2026-09-04T16:00:00+00:00",
    "reason": "check-up"
  }
}
```

### Business failure response

Status `200`, mantendo o contrato do fluxo:

```json
{
  "intent": "cancel",
  "success": false,
  "message": "Não foi possível processar sua solicitação.",
  "error": "Consulta não encontrada para cancelamento"
}
```

### Validation and unexpected failure

- Entrada inválida: status `422`, conforme contrato HTTP.
- Falha inesperada: status `500` com mensagem genérica, sem detalhes internos ou segredos.
