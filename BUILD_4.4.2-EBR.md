# Angel Platform 4.4.2 — EBR Prototype Build

## Release

**Angel Platform 4.4.2-EBR-PROTOTYPE**

Branch: `feature/evidence-backed-reasoning-v1`
Baseline: `Angel Platform 4.3.1-G`

## Build status

**READY FOR EXPERIMENTAL TESTING**

## Implemented

- `ENABLE_PROVENANCE_V1`, default `false`
- SQLite `evidence_claims`
- SQLite `claim_sources`
- Required provenance indexes
- Deterministic `conversation.test_phrase` extraction
- Source linkage to the original user message
- Claim rebuild for conversation-scoped derived claims
- Exact-key evidence retrieval
- Conversation scope enforcement
- Source/quote provenance validation
- Structured `[SUPPORTED EVIDENCE]`, `[INFERENCES]`, `[UNKNOWNS]` context blocks
- RAG diagnostic states including `HIT_VALIDATED`, `NO_EVIDENCE`, `ERROR`, `INJECTED`, and `OFF`
- EBR prompt/retrieval trace metadata
- Claim audit endpoint
- Previous-answer evidence audit endpoint
- Level 3 schema rollback SQL

## Safety boundaries

The EBR feature is disabled unless `ENABLE_PROVENANCE_V1` is enabled. The
existing 4.3.1-G deterministic recall path remains available when EBR is off.

SQLite messages remain authoritative. EBR claims and provenance links are
rebuildable derived data and cannot delete source messages.

RAG is diagnostic/context infrastructure, not an action authority. Existing
proposal → approval → execution → verification behavior remains unchanged.

## Validation

- Focused EBR + context integrity tests: **10/10 PASS**
- Full regression suite: **96/96 PASS**
- Feature-enabled end-to-end EBR smoke: **PASS**
- Level 3 rollback smoke: **PASS**

## Canonical test

`ANGEL-TEST-7429`

Expected EBR path:

`HIT → scope validation → provenance validation → HIT_VALIDATED → INJECTED`

## Known limitation

This is still an experimental provenance prototype. It does not introduce a
vector database, graph database, cloud memory service, model replacement, or
second authoritative memory store.
