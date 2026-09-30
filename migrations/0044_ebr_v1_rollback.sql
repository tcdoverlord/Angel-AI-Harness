-- Level 3 EBR prototype rollback. Source evidence tables are untouched.
PRAGMA foreign_keys=ON;
DROP TABLE IF EXISTS claim_sources;
DROP TABLE IF EXISTS evidence_claims;
