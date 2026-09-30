from angel_platform.conversation_intelligence import ConversationIntelligence
from angel_platform.context_engine import ContextAssembler


def test_context_recall_request_is_detected():
    assert ConversationIntelligence.is_context_recall_request("What was the test phrase I gave you?")
    assert ConversationIntelligence.is_context_recall_request("What did I tell you earlier?")
    assert ConversationIntelligence.is_context_recall_request("Do you remember what I said?")
    assert not ConversationIntelligence.is_context_recall_request("Explain SQLite.")
    assert not ConversationIntelligence.is_context_recall_request("Analyze this repository.")


def test_context_recall_keeps_transcript_primary():
    assembler = ContextAssembler(
        capability_report=lambda: "CAPABILITY REPORT",
        knowledge_context=lambda request, limit: "UNRELATED BACKGROUND KNOWLEDGE",
        project_context=lambda project_id: None,
        estimate_tokens=lambda text: (len(str(text)) + 3) // 4,
    )
    history = [
        {"role": "user", "content": "Remember this test phrase: ANGEL-TEST-7429."},
        {"role": "assistant", "content": "I will remember it for this conversation."},
    ]
    result = assembler.assemble(
        request="What was the test phrase I gave you?",
        history=history,
        model="test-model",
        lane="conversation",
    )
    system = result.messages[0]["content"]
    transcript = "\n".join(x["content"] for x in result.messages[1:])
    assert "ANGEL-TEST-7429" in transcript
    assert "UNRELATED BACKGROUND KNOWLEDGE" not in system
    assert result.trace["knowledge_retrieval_suppressed"] is True



def test_deterministic_phrase_recall_extracts_exact_user_phrase():
    history = [
        {"role": "user", "content": "Remember this test phrase for this conversation: ANGEL-TEST-7429. Do not do anything with it yet."},
        {"role": "assistant", "content": "I've noted the test phrase."},
        {"role": "user", "content": "What was the test phrase I gave you?"},
    ]
    assert ConversationIntelligence.deterministic_phrase_recall(history[-1]["content"], history) == "ANGEL-TEST-7429"


def test_deterministic_phrase_recall_does_not_invent_missing_phrase():
    history = [{"role": "user", "content": "Tell me about this project."}]
    assert ConversationIntelligence.deterministic_phrase_recall("What was the test phrase I gave you?", history) is None
