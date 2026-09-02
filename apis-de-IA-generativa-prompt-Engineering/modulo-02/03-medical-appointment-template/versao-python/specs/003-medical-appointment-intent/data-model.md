# Data Model: Medical Appointment Intent Flow

## Professional

`id` (positive stable identifier), `name` (non-empty display name), and `specialty` (non-empty
specialty). The catalog contains deterministic examples. One professional can have many appointments.

## Appointment

`professional_id`, `professional_name`, `patient_name`, `datetime`, and `reason`. All required
values are non-empty; the professional must exist; datetime is normalized, valid, and not past.
The `(professional_id, datetime)` pair is unique. Cancellation additionally matches patient name.

## Conversation State

The medical state contains `messages`, `output`, `intent` (`schedule`, `cancel`, `unknown`),
patient/professional data, normalized datetime, reason, action success/error, appointment data and
processing error. It is ephemeral per invocation; nodes return partial updates and the final response
is appended to the message history. No state field is retained solely for the Módulo 2 exercise.

## Transitions

```text
received → identified(schedule|cancel|unknown)
identified(schedule) → scheduled(success|failure) → answered
identified(cancel) → cancelled(success|failure) → answered
identified(unknown|error) → answered
```

HTTP validation occurs before graph execution. Domain failures remain in state and produce a
user-facing response without mutating data incorrectly.
