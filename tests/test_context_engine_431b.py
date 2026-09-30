from angel_platform.context_engine import ContextAssembler


def make_assembler(project=None, knowledge=None):
    return ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: knowledge,
        project_context=lambda project_id: project if project_id else None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )


def test_context_assembler_centralizes_required_context():
    assembler = make_assembler()
    result = assembler.assemble(
        request="What is Angel doing?",
        history=[{"role": "user", "content": "Earlier"}, {"role": "assistant", "content": "Answer"}],
        model="test-model",
        lane="conversation",
    )

    assert result.messages[0]["role"] == "system"
    assert "CAPABILITY REPORT" in result.messages[0]["content"]
    assert "Current objective:" in result.messages[0]["content"]
    assert "What is Angel doing?" in result.messages[0]["content"]
    assert result.messages[-2:] == [
        {"role": "user", "content": "Earlier"},
        {"role": "assistant", "content": "Answer"},
    ]
    assert result.trace["context_order"][:3] == ["system_rules", "current_objective", "current_request"]
    assert result.token_estimates["total"] >= result.token_estimates["system"]


def test_context_assembler_conditionally_adds_project_and_knowledge():
    project = {
        "project": {"id": "p1", "name": "Demo"},
        "resolved_scope": {"knowledge": "project knowledge"},
        "scope_fingerprint": "abc123",
    }
    assembler = make_assembler(project=project, knowledge="Relevant knowledge")
    result = assembler.assemble(
        request="Explain this",
        history=[],
        model="test-model",
        lane="conversation",
        project_id="p1",
        knowledge_hits=[{"title": "one"}],
    )
    names = [b["name"] for b in result.trace["context_blocks"]]
    assert "project_context" in names
    assert "relevant_knowledge" in names
    assert result.trace["exact_model_messages"] == result.messages


def test_context_assembler_records_history_truncation():
    assembler = make_assembler()
    history = [{"role": "user", "content": str(i)} for i in range(25)]
    result = assembler.assemble(
        request="latest",
        history=history,
        model="test-model",
        lane="conversation",
    )
    assert len(result.messages) == 21  # one system message + 20 history messages
    assert result.truncation_events == ["conversation_history_limit_20"]
    assert result.trace["truncation_events"] == result.truncation_events
