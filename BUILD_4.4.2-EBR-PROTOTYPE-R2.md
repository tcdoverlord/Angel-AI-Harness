# Angel Platform 4.4.2-EBR-PROTOTYPE-R2

## Grounding Boundary Fix

This revision preserves the 4.4.2 EBR architecture while fixing a critical boundary defect found during live testing.

### Defect

Legacy knowledge retrieval was still being injected into the context for project/repository-bounded requests. This allowed unsupported repository filenames and database-engine guesses despite EBR being enabled.

### Fix

When `ENABLE_PROVENANCE_V1=true`, evidence-bounded project/repository requests now:

- suppress background knowledge retrieval
- retrieve through the EBR path
- return `NO_EVIDENCE` when no provenance-backed claim exists
- inject an explicit unknown/insufficient-evidence section
- never label legacy knowledge chunks as verified evidence

The feature-off path remains unchanged.

## Validation

- Focused EBR/context tests: 17/17 PASS
- Full regression suite: 98/98 PASS

## Critical invariant

`NO_EVIDENCE` means retrieval completed but adequate provenance-backed evidence was not found.

It must never be converted into a fabricated fact, filename, database engine, or source.
