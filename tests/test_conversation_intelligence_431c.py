from angel_platform.conversation_intelligence import ConversationIntelligence
from angel_platform.context_engine import ContextAssembler


def test_objective_tracking_has_three_explicit_fields():
    state = ConversationIntelligence.analyze("Build the next release", [])
    assert state.current_objective == "Build the next release"
    assert state.current_task
    assert state.current_deliverable


def test_follow_up_change_that_resolves_previous_context():
    history = [
        {"role": "user", "content": "Use the blue design for the dashboard."},
        {"role": "assistant", "content": "The dashboard is using the blue design."},
    ]
    state = ConversationIntelligence.analyze("Change that", history)
    assert "Reference resolved to" in state.resolved_request
    assert "blue design" in state.resolved_request
    assert "change that" in state.references


def test_common_follow_ups_are_recognized():
    history = [{"role": "assistant", "content": "The previous build is 4.3.1-B."}]
    for request in ("Use PostgreSQL", "Do it again", "Use the same design", "Use the previous version"):
        state = ConversationIntelligence.analyze(request, history)
        assert state.current_objective
        assert state.current_task
        assert state.current_deliverable
    assert "4.3.1-B" in ConversationIntelligence.analyze("Use the previous version", history).resolved_request


def test_reference_terms_resolve():
    history = [{"role": "user", "content": "the current project is Angel Platform"}]
    for request in ("it", "that", "this", "those", "previous design", "last build", "current project"):
        state = ConversationIntelligence.analyze(request, history)
        assert state.references
        assert "Reference resolved to" in state.resolved_request


def test_context_assembler_includes_conversation_state():
    assembler = ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: None,
        project_context=lambda project_id: None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )
    state = ConversationIntelligence.analyze("Use PostgreSQL", [])
    result = assembler.assemble(
        request="Use PostgreSQL",
        history=[],
        model="test-model",
        lane="conversation",
        conversation_state=state.as_dict(),
    )
    content = result.messages[0]["content"]
    assert "Current objective: Use PostgreSQL" in content
    assert "Current task:" in content
    assert "Current deliverable:" in content
