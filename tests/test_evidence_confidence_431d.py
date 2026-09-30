from angel_platform.evidence_confidence import EvidenceConfidence
from angel_platform.context_engine import ContextAssembler


def test_no_evidence_is_unknown():
    result = EvidenceConfidence.assess("What is the current status?", [])
    assert result.level == "Unknown"
    assert result.evidence_count == 0
    assert result.source_count == 0


def test_single_relevant_source_is_medium():
    result = EvidenceConfidence.assess(
        "PostgreSQL migration",
        [{"title": "DB Guide", "source": "db.md", "content": "PostgreSQL migration procedure."}],
    )
    assert result.level == "Medium"
    assert result.evidence_count == 1
    assert result.source_count == 1
    assert result.support_strength == "partial"


def test_multiple_relevant_sources_can_be_high():
    result = EvidenceConfidence.assess(
        "PostgreSQL migration",
        [
            {"title": "DB Guide", "source": "db.md", "content": "PostgreSQL migration procedure."},
            {"title": "Release Guide", "source": "release.md", "content": "PostgreSQL migration validation."},
        ],
    )
    assert result.level == "High"
    assert result.source_count == 2
    assert result.support_strength == "strong"


def test_context_assembler_exposes_confidence_and_response_structure():
    assembler = ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: None,
        project_context=lambda project_id: None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )
    confidence = EvidenceConfidence.assess("PostgreSQL", [{"title": "DB", "source": "db.md", "content": "PostgreSQL is documented."}])
    result = assembler.assemble(
        request="PostgreSQL",
        history=[],
        model="test-model",
        lane="conversation",
        confidence=confidence.as_dict(),
    )
    content = result.messages[0]["content"]
    assert "Facts" in content
    assert "Open Questions" in content
    assert "Recommendations" in content
    assert "Evidence confidence:" in content
