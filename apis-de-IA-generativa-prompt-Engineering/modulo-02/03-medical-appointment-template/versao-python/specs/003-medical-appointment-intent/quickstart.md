# Quickstart: Medical Appointment Intent Flow

Use pyenv Python 3.13.12 and Poetry. No API key is required for the deterministic path.

```bash
poetry install
poetry run pytest
poetry run uvicorn langchain_intro.app:app --reload
```

Using [contracts/chat.md](contracts/chat.md), verify scheduling success, occupied-slot failure
without duplication, matching cancellation, repeated cancellation failure and unknown guidance.
In a second terminal, run
`poetry run langgraph dev --no-browser --no-reload` and verify the graph, branches and isolated
invocations. The standard flow requires no LLM provider; any future adapter must be tested with a
fake/mock and provider tests remain separate.
