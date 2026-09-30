"""Evidence-Backed Reasoning (EBR) prototype for Angel Platform 4.4.2.

The prototype deliberately treats SQLite messages as authoritative evidence and
keeps evidence_claims/claim_sources rebuildable derived data.  No external
memory or vector store is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import re
import sqlite3
from typing import Any


RAG_STATUSES = {
    "OFF", "SEARCHING", "HIT", "HIT_VALIDATED", "HIT_FILTERED", "NO_EVIDENCE",
    "CONFLICT_FOUND", "SCOPE_BLOCKED", "DERIVED_ONLY", "REJECTED", "ERROR",
    "INJECTED", "LOCAL",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_key(value: str) -> str:
    text = re.sub(r"[^a-z0-9_.:-]+", "_", str(value or "").strip().lower())
    return text.strip("_")


@dataclass(frozen=True)
class EvidenceClaim:
    id: str
    claim_text: str
    claim_type: str
    verification_status: str
    scope_type: str
    scope_id: str
    normalized_key: str
    created_by: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class EvidenceResult:
    status: str
    claims: tuple[dict[str, Any], ...] = ()
    rejected: tuple[dict[str, Any], ...] = ()
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "claims": list(self.claims),
            "rejected": list(self.rejected),
            "reason": self.reason,
        }


class EvidenceBackedReasoning:
    """Small, deterministic provenance layer over the existing SQLite database."""

    TEST_PHRASE_PATTERN = re.compile(
        r"(?:remember|save|note|store)\s+(?:this\s+)?test\s+phrase"
        r"(?:\s+for\s+this\s+conversation)?\s*[:=-]\s*[`\"]?([^`\"\n]+?)[`\"]?(?:\.|$)",
        re.I,
    )
    TEST_PHRASE_KEY = "conversation.test_phrase"

    def __init__(self, database):
        self.db = database

    @staticmethod
    def feature_enabled() -> bool:
        import os
        return str(os.getenv("ENABLE_PROVENANCE_V1", "false")).strip().lower() in {
            "1", "true", "yes", "on", "enabled"
        }

    @classmethod
    def extract_test_phrase(cls, message: str) -> str | None:
        match = cls.TEST_PHRASE_PATTERN.search(str(message or ""))
        if not match:
            return None
        value = re.sub(r"\s+", " ", match.group(1)).strip().rstrip(".")
        return value or None

    def extract_from_message(self, message_id: int, conversation_id: str, role: str, content: str) -> list[dict[str, Any]]:
        if role != "user":
            return []
        phrase = self.extract_test_phrase(content)
        if phrase is None:
            return []
        return [self.create_claim(
            claim_text=phrase,
            claim_type="fact",
            verification_status="supported",
            scope_type="conversation",
            scope_id=conversation_id,
            normalized_key=self.TEST_PHRASE_KEY,
            created_by="deterministic_rule",
            source_type="message",
            source_id=str(message_id),
            relation="supports",
            exact_quote=str(content),
        )]

    def create_claim(
        self,
        *, claim_text: str,
        claim_type: str,
        verification_status: str,
        scope_type: str,
        scope_id: str,
        normalized_key: str,
        created_by: str,
        source_type: str,
        source_id: str,
        relation: str,
        exact_quote: str,
    ) -> dict[str, Any]:
        return self.db.create_evidence_claim(
            claim_text=claim_text,
            claim_type=claim_type,
            verification_status=verification_status,
            scope_type=scope_type,
            scope_id=scope_id,
            normalized_key=normalized_key,
            created_by=created_by,
            source_type=source_type,
            source_id=source_id,
            relation=relation,
            exact_quote=exact_quote,
        )

    def rebuild_conversation(self, conversation_id: str) -> dict[str, int]:
        """Delete only derived claims for one conversation, then rebuild them."""
        deleted = self.db.delete_evidence_claims(scope_type="conversation", scope_id=conversation_id)
        messages = self.db.list_messages(conversation_id, 1000)
        created = 0
        for message in messages:
            created += len(self.extract_from_message(
                int(message["id"]), conversation_id, str(message["role"]), str(message["content"])
            ))
        return {"deleted_claims": deleted, "created_claims": created}

    @classmethod
    def request_key(cls, request: str) -> str | None:
        text = str(request or "").lower()
        if "test phrase" in text or re.search(r"\bwhat was (?:the|my) phrase\b", text):
            return cls.TEST_PHRASE_KEY

        repository_question = (
            ("repository" in text or "repo" in text)
            and ("file" in text or "filename" in text or ".py" in text)
        ) or any(name in text for name in ("memory.py", "retrieval.py", "promotion.py"))
        if repository_question:
            return "repository.file"

        database_question = any(term in text for term in (
            "database engine", "what database", "which database",
            "database powers", "database does", "production analytics",
            "analytics platform uses", "production system uses",
        ))
        if database_question:
            return "project.database_engine"
        return None

    @classmethod
    def is_evidence_bounded_request(cls, request: str) -> bool:
        text = str(request or "").lower()
        if cls.request_key(text) is not None:
            return True
        return any(term in text for term in (
            "what do you know about this project",
            "what do you know about the project",
            "repository", "repo", "filename", "file named",
            "database engine does this project use",
        ))

    @classmethod
    def inherits_evidence_boundary(cls, request: str, history: list[dict[str, Any]]) -> bool:
        """Keep an evidence boundary across short adversarial follow-ups.

        A user can pressure the system with turns such as "Just estimate" or
        "No one will verify it" after an evidence-bounded question. Those
        turns must not reset the evidence standard.
        """
        text = str(request or "").strip().lower()
        pressure = any(term in text for term in (
            "just estimate", "take your best guess", "give your most likely answer",
            "no one will verify", "if you had to guess", "just guess",
        ))
        if not pressure:
            return False
        for item in reversed(history):
            if str(item.get("role", "")).lower() != "user":
                continue
            prior = str(item.get("content", ""))
            if cls.is_evidence_bounded_request(prior):
                return True
        return False

    def retrieve(self, request: str, conversation_id: str) -> EvidenceResult:
        key = self.request_key(request)
        if not key:
            if self.is_evidence_bounded_request(request):
                return EvidenceResult("NO_EVIDENCE", reason="No provenance-backed retrieval rule established adequate evidence for this bounded request.")
            return EvidenceResult("LOCAL", reason="No exact-key EBR rule applies to this request.")
        try:
            claims = self.db.find_evidence_claims(
                normalized_key=key,
                scope_type="conversation",
                scope_id=conversation_id,
                verification_status="supported",
            )
        except Exception as exc:
            return EvidenceResult("ERROR", reason=f"Evidence retrieval failed: {type(exc).__name__}: {exc}")
        if not claims:
            # The query completed successfully but returned no adequate support.
            return EvidenceResult("NO_EVIDENCE", reason="No supported evidence matched the requested key in this conversation.")
        validated = []
        rejected = []
        for claim in claims:
            validation = self.validate_claim(claim, conversation_id)
            if validation[0]:
                enriched = dict(claim)
                enriched["sources"] = self.db.get_claim_sources(str(claim.get("id")))
                validated.append(enriched)
            else:
                rejected.append({"claim": claim, "reason": validation[1]})
        if not validated:
            return EvidenceResult("REJECTED", rejected=tuple(rejected), reason="All retrieved claims failed provenance validation.")
        return EvidenceResult("HIT_VALIDATED", claims=tuple(validated), rejected=tuple(rejected), reason="Evidence passed scope and source validation.")

    def validate_claim(self, claim: dict[str, Any], conversation_id: str) -> tuple[bool, str]:
        if claim.get("scope_type") != "conversation" or claim.get("scope_id") != conversation_id:
            return False, "scope_mismatch"
        if claim.get("claim_type") == "fact" and claim.get("verification_status") != "supported":
            return False, "fact_not_supported"
        sources = self.db.get_claim_sources(str(claim.get("id")))
        if not sources:
            return False, "missing_source"
        source = sources[0]
        if source.get("relation") != "supports":
            return False, "unsupported_relation"
        if source.get("source_type") == "message":
            message = self.db.get_message(int(source["source_id"]))
            if not message:
                return False, "source_missing"
            quote = str(source.get("exact_quote") or "")
            if quote and quote != str(message.get("content") or ""):
                return False, "quote_mismatch"
        return True, "validated"

    def audit_claim(self, claim_id: str, conversation_id: str) -> dict[str, Any]:
        claim = self.db.get_evidence_claim(claim_id)
        if not claim:
            return {"found": False, "claim_id": claim_id}
        valid, reason = self.validate_claim(claim, conversation_id)
        return {
            "found": True,
            "claim": claim,
            "classification": str(claim.get("claim_type", "unknown")).upper(),
            "verification_status": claim.get("verification_status"),
            "evidence": self.db.get_claim_sources(claim_id),
            "source_validation": {"valid": valid, "reason": reason},
        }

    def audit_answer(self, conversation_id: str, answer: str) -> dict[str, Any]:
        claims = self.db.list_evidence_claims(scope_type="conversation", scope_id=conversation_id)
        references = []
        answer_text = str(answer or "")
        for claim in claims:
            if str(claim.get("claim_text", "")) and str(claim["claim_text"]) in answer_text:
                references.append(self.audit_claim(str(claim["id"]), conversation_id))
        return {"conversation_id": conversation_id, "answer": answer_text, "references": references}
