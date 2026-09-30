# Angel R4 Telemetry Contract

R4 telemetry describes actual execution. It must not infer correctness from response text after the fact.

## Required response telemetry

- `response_source`: `deterministic_no_evidence`, `deterministic_error`, `deterministic_conflict`, `ebr_validated`, `llm_generated`, or `tool_generated`.
- `model_invoked`: true only when the Ollama/model branch was actually invoked.
- `model_name`: the model used when `model_invoked` is true; otherwise null.
- `rag_state_history`: ordered retrieval state transitions.
- `terminal_state`: terminal EBR state for the request.
- `response_hash`: SHA-256 of the exact response text.
- `response_preview`: first 200 characters of the exact response text.

## Required state examples

Missing evidence:
`SEARCHING -> NO_EVIDENCE`

Known evidence:
`SEARCHING -> HIT -> HIT_VALIDATED -> INJECTED`

Conflict fixture:
`SEARCHING -> HIT -> CONFLICT_FOUND`

Retrieval failure fixture:
`SEARCHING -> ERROR`

## Context integrity

Ordinary local conversational continuity suppresses unrelated indexed knowledge when the active topic is clearly a short-lived conversational thread such as a sale/nap/buyer discussion. Short acknowledgements also suppress background retrieval. This is a deterministic context-continuity guard, not a new memory store.

## Test fixtures

The controlled R4 endpoints are available only when `TEST_MODE=true`:

- `POST /api/test/ebr/conflict`
- `POST /api/test/ebr/fail-next-retrieval`

These affect only the next EBR retrieval and do not modify authoritative evidence.
