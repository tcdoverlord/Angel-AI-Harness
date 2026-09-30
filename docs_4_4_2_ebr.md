# Angel Platform 4.4.2 — Evidence-Backed Reasoning Prototype

Branch: `feature/evidence-backed-reasoning-v1`
Baseline: Angel Platform 4.3.1-G

## Safety contract

`ENABLE_PROVENANCE_V1=false` by default. With the flag off, the EBR extraction,
retrieval, validation, and context-injection path is not invoked.

SQLite remains authoritative. `evidence_claims` and `claim_sources` are derived
and rebuildable. Deleting prototype claims never deletes messages or other source
evidence.

## Implemented prototype path

SQLite messages → deterministic extraction → evidence_claims → claim_sources →
exact-key retrieval → scope/provenance validation → structured evidence context →
model.

## RAG diagnostics

`OFF`, `SEARCHING`, `HIT`, `HIT_VALIDATED`, `HIT_FILTERED`, `NO_EVIDENCE`,
`CONFLICT_FOUND`, `SCOPE_BLOCKED`, `DERIVED_ONLY`, `REJECTED`, `ERROR`, `INJECTED`,
`LOCAL`.

`ERROR` is never converted to `NO_EVIDENCE`.

## First extraction rule

The deterministic test-phrase rule creates `conversation.test_phrase` from an
explicit user-authored message and links it to the original SQLite message.

## Rollback

1. Feature rollback: `ENABLE_PROVENANCE_V1=false`.
2. Data rollback: delete only `claim_sources` and `evidence_claims` rows.
3. Schema rollback: execute `migrations/0044_ebr_v1_rollback.sql`.

All rollback levels preserve authoritative messages and conversations.
