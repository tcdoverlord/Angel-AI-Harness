from pathlib import Path

from angel_platform.conversation_summary import ConversationSummaryService
from angel_platform.storage.database import AngelDatabase
from angel_platform.context_engine import ContextAssembler


def test_summary_contains_required_sections_and_preserves_count():
    messages = []
    for i in range(220):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": f"Decision {i}: build release. Action {i}: implement and test. Open question {i}?"})
    summary = ConversationSummaryService.generate("c1", messages, "2026-09-29T00:00:00+00:00")
    rendered = summary.render()
    assert summary.message_count == 220
    for heading in ("Decisions:", "Actions:", "Open Questions:", "Project Status:", "Important Context:"):
        assert heading in rendered


def test_summary_storage_is_non_destructive(tmp_path: Path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    db.ensure_conversation("c1")
    for i in range(500):
        db.record_message("user" if i % 2 == 0 else "assistant", f"Original transcript message {i}", "c1")
    messages = db.list_messages("c1", 1000)
    summary = ConversationSummaryService.generate("c1", messages, "2026-09-29T00:00:00+00:00")
    db.save_conversation_summary("c1", len(messages), summary.as_dict())
    stored = db.get_conversation_summary("c1")
    assert stored["message_count"] == 500
    assert len(db.list_messages("c1", 1000)) == 500


def test_summary_integrates_with_context_without_replacing_recent_history():
    assembler = ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: None,
        project_context=lambda project_id: None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )
    result = assembler.assemble(
        request="Continue",
        history=[{"role": "user", "content": "Recent original"}],
        model="test-model",
        lane="conversation",
        conversation_summary="Conversation summary (500 messages):\nDecisions:\n- Keep SQLite\nActions:\n- Test release",
    )
    names = [x["name"] for x in result.trace["context_blocks"]]
    assert "conversation_summary" in names
    assert "Recent original" in result.messages[-1]["content"]
    assert "Keep SQLite" in result.messages[0]["content"]
