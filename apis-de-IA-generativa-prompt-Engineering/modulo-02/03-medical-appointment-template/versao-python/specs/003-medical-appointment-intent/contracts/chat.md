# Contract: POST /chat

## Request

```json
{"question":"Olá, quero agendar uma consulta com a Dra. Ana Pereira amanhã às 14h para avaliação."}
```

`question` is required and textual. Invalid or too-short bodies return `422` without graph execution.

## Medical responses

```json
{"intent":"schedule","success":true,"message":"Sua consulta foi confirmada.","appointment":{"professional_id":2,"professional_name":"Dra. Ana Pereira","patient_name":"Maria Santos","datetime":"2026-09-01T14:00:00Z","reason":"avaliação"}}
```

```json
{"intent":"schedule","success":false,"message":"Esse horário está indisponível.","error":"slot_unavailable"}
```

```json
{"intent":"unknown","success":false,"message":"Posso ajudar a agendar ou cancelar consultas médicas."}
```

Cancellation success uses `intent: "cancel"`, `success: true`; a missing appointment fails without
deletion. Unexpected failures return `500` with a stable public message and no stack trace,
credentials or provider payload. The textual transformation contract from the Módulo 2 exercise is
not part of this endpoint contract.
