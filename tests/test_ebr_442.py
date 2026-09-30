import os
from pathlib import Path

from angel_platform.storage.database import AngelDatabase
from angel_platform.evidence_backed_reasoning import EvidenceBackedReasoning
from angel_platform.context_engine import ContextAssembler


def make_db(tmp_path):
    return AngelDatabase(tmp_path / "test.sqlite3")


def test_ebr_feature_flag_defaults_off(monkeypatch):
    monkeypatch.delenv("ENABLE_PROVENANCE_V1", raising=False)
    assert EvidenceBackedReasoning.feature_enabled() is False


def test_extract_create_and_retrieve_exact_phrase(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    cid = "conv-a"
    db.create_conversation(cid, "Test")
    message_id = db.record_message(
        "user",
        "Remember this test phrase for this conversation: ANGEL-TEST-7429. Do not do anything with it yet.",
        cid,
    )
    created = ebr.extract_from_message(message_id, cid, "user", "Remember this test phrase for this conversation: ANGEL-TEST-7429. Do not do anything with it yet.")
    assert len(created) == 1
    assert created[0]["normalized_key"] == "conversation.test_phrase"
    result = ebr.retrieve("What was the test phrase I gave you?", cid)
    assert result.status == "HIT_VALIDATED"
    assert result.claims[0]["claim_text"] == "ANGEL-TEST-7429"


def test_cross_conversation_scope_isolated(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    db.create_conversation("a", "A")
    db.create_conversation("b", "B")
    mid = db.record_message("user", "Remember this test phrase: ANGEL-TEST-7429.", "a")
    ebr.extract_from_message(mid, "a", "user", "Remember this test phrase: ANGEL-TEST-7429.")
    assert ebr.retrieve("What was the test phrase I gave you?", "a").status == "HIT_VALIDATED"
    assert ebr.retrieve("What was the test phrase I gave you?", "b").status == "NO_EVIDENCE"


def test_missing_evidence_is_not_retrieval_error(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    db.create_conversation("a", "A")
    result = ebr.retrieve("What was the test phrase I gave you?", "a")
    assert result.status == "NO_EVIDENCE"


def test_rebuild_removes_and_recreates_only_derived_claims(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    db.create_conversation("a", "A")
    mid = db.record_message("user", "Remember this test phrase: ANGEL-TEST-7429.", "a")
    ebr.extract_from_message(mid, "a", "user", "Remember this test phrase: ANGEL-TEST-7429.")
    result = ebr.rebuild_conversation("a")
    assert result["deleted_claims"] == 1
    assert result["created_claims"] == 1
    assert db.get_message(mid)["content"].endswith(".")


def test_context_injects_structured_supported_evidence():
    assembler = ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: None,
        project_context=lambda project_id: None,
        estimate_tokens=lambda text: max(1, len(str(text)) // 4),
    )
    result = assembler.assemble(
        request="What was the test phrase?",
        history=[],
        model="test-model",
        lane="conversation",
        supported_evidence=[{
            "id": "claim-1",
            "claim_text": "ANGEL-TEST-7429",
            "normalized_key": "conversation.test_phrase",
        }],
        unknowns=[],
    )
    system = result.messages[0]["content"]
    assert "[SUPPORTED EVIDENCE]" in system
    assert "ANGEL-TEST-7429" in system
    assert result.trace["context_blocks"][-1]["name"] == "supported_evidence"


def test_project_database_request_is_evidence_bounded(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    db.create_conversation("a", "A")
    request = "What database engine does this project use for its production analytics system?"
    assert ebr.is_evidence_bounded_request(request) is True
    assert ebr.retrieve(request, "a").status == "NO_EVIDENCE"


def test_repository_filename_request_is_evidence_bounded(tmp_path):
    db = make_db(tmp_path)
    ebr = EvidenceBackedReasoning(db)
    db.create_conversation("a", "A")
    request = "List the repository files you know exist that are named memory.py, retrieval.py, and promotion.py."
    assert ebr.is_evidence_bounded_request(request) is True
    assert ebr.retrieve(request, "a").status == "NO_EVIDENCE"
