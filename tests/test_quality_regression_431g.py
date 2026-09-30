from __future__ import annotations

import time

from angel_platform.context_engine import ContextAssembler
from angel_platform.conversation_intelligence import ConversationIntelligence
from angel_platform.conversation_summary import ConversationSummaryService
from angel_platform.evidence_confidence import EvidenceConfidence


def make_assembler(project=None, knowledge=None):
    return ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: knowledge,
        project_context=lambda project_id: project if project_id else None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )


def history(count: int):
    return [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"message {i} about Angel project continuity"}
        for i in range(count)
    ]


def test_long_prompts_2000_and_5000_words_are_preserved_as_current_request():
    assembler = make_assembler()
    for words in (2000, 5000):
        request = " ".join([f"word{i}" for i in range(words)])
        result = assembler.assemble(request=request, history=[], model="qa-model", lane="conversation")
        current = next(x for x in result.trace["context_blocks"] if x["name"] == "current_request")
        assert current["text"] == request
        assert not result.truncation_events
        assert request in result.messages[0]["content"]


def test_multi_message_continuation_and_long_conversations_remain_bounded():
    assembler = make_assembler()
    for count in (100, 250, 500):
        result = assembler.assemble(
            request="Continue the current task",
            history=history(count),
            model="qa-model",
            lane="conversation",
        )
        assert result.trace["history_messages_included"] == 20
        assert "conversation_history_limit_20" in result.truncation_events
        assert result.messages[-1]["content"] == f"message {count - 1} about Angel project continuity"


def test_follow_up_regression_suite():
    prior = [
        {"role": "user", "content": "Use the PostgreSQL architecture and the same blue dashboard design."},
        {"role": "assistant", "content": "The current project uses the PostgreSQL architecture and blue dashboard design."},
    ]
    for request in ("Change that", "Do it again", "Use PostgreSQL", "Use the same design"):
        state = ConversationIntelligence.analyze(request, prior)
        assert state.current_objective
        assert state.current_task
        assert state.current_deliverable
        if request in {"Change that", "Do it again", "Use the same design"}:
            assert state.references
            assert "Reference resolved to" in state.resolved_request


def test_context_retention_project_knowledge_objective_and_evidence():
    project = {
        "project": {"id": "p1", "name": "Angel Nexus"},
        "resolved_scope": {"knowledge": "project knowledge"},
        "scope_fingerprint": "scope-123",
    }
    state = ConversationIntelligence.analyze("Build the next Angel release", [])
    assembler = make_assembler(project=project, knowledge="SQLite is authoritative storage.")
    evidence = [{"source": "storage-review", "content": "SQLite remains canonical for Angel conversations."}]
    confidence = EvidenceConfidence.assess("SQLite remains canonical", evidence).as_dict()
    result = assembler.assemble(
        request="Build the next Angel release",
        history=history(4),
        model="qa-model",
        lane="conversation",
        project_id="p1",
        conversation_state=state.as_dict(),
        evidence=evidence,
        confidence=confidence,
    )
    content = result.messages[0]["content"]
    assert "Angel Nexus" in content
    assert "SQLite is authoritative storage." in content
    assert "Current objective: Build the next Angel release" in content
    assert "Verified evidence:" in content
    assert "Evidence confidence:" in content


def test_unsupported_claims_are_marked_unknown_and_conflicts_are_exposed():
    unknown = EvidenceConfidence.assess("Did the migration complete?", []).as_dict()
    assert unknown["level"] == "Unknown"
    assert unknown["open_questions"]

    conflicting = EvidenceConfidence.assess(
        "migration complete",
        [
            {"source": "A", "content": "migration complete"},
            {"source": "B", "content": "migration not complete"},
        ],
    ).as_dict()
    assert conflicting["conflicts_detected"] >= 1
    assert conflicting["level"] == "Low"


def test_summary_supports_long_context_without_destructive_compression():
    messages = history(500)
    messages.extend([
        {"role": "user", "content": "Decision: keep SQLite canonical."},
        {"role": "assistant", "content": "Action: preserve the complete transcript."},
        {"role": "user", "content": "Open question: should compatibility JSON be retired?"},
    ])
    summary = ConversationSummaryService.generate("qa-500", messages, "2026-09-29T00:00:00+00:00")
    assert summary.message_count == 503
    rendered = summary.render()
    assert "Decisions:" in rendered
    assert "Actions:" in rendered
    assert "Open Questions:" in rendered
    assert "Project Status:" in rendered
    assert "Important Context:" in rendered
    assert "SQLite canonical" in rendered
    assert "preserve the complete transcript" in rendered


def test_context_assembly_performance_is_bounded_for_500_messages():
    assembler = make_assembler()
    start = time.perf_counter()
    result = assembler.assemble(
        request="Continue the current task",
        history=history(500),
        model="qa-model",
        lane="conversation",
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.trace["history_messages_included"] == 20
    # Conservative local regression ceiling; this is a guard against accidental
    # quadratic work, not a hardware-independent latency promise.
    assert elapsed_ms < 250
