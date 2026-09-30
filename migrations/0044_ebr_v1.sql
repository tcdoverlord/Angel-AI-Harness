-- Angel Platform 4.4.2 EBR prototype migration.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS evidence_claims (
    id TEXT PRIMARY KEY,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL CHECK(claim_type IN ('fact','inference')),
    verification_status TEXT NOT NULL DEFAULT 'supported'
        CHECK(verification_status IN ('supported','unverified','disputed','retracted')),
    scope_type TEXT NOT NULL DEFAULT 'conversation'
        CHECK(scope_type IN ('conversation','user','project','global')),
    scope_id TEXT NOT NULL,
    normalized_key TEXT NOT NULL,
    created_by TEXT NOT NULL DEFAULT 'deterministic_rule'
        CHECK(created_by IN ('deterministic_rule','model','user','import')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claim_sources (
    id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    source_type TEXT NOT NULL
        CHECK(source_type IN ('message','document','document_chunk','tool_event','decision','claim')),
    source_id TEXT NOT NULL,
    relation TEXT NOT NULL
        CHECK(relation IN ('supports','contradicts','derived_from')),
    exact_quote TEXT NOT NULL DEFAULT '',
    source_start INTEGER,
    source_end INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(claim_id) REFERENCES evidence_claims(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_claims_scope ON evidence_claims(scope_type, scope_id);
CREATE INDEX IF NOT EXISTS idx_claims_normalized_key ON evidence_claims(normalized_key);
CREATE INDEX IF NOT EXISTS idx_claims_type_status ON evidence_claims(claim_type, verification_status);
CREATE INDEX IF NOT EXISTS idx_claim_sources_claim ON claim_sources(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_sources_source ON claim_sources(source_type, source_id);
