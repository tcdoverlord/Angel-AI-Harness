from __future__ import annotations

import pytest

from tests.angel_r4_contract import AngelR4Client, R4Result

SALE_TOPIC_TERMS = {
    "nap", "sleep", "rest", "buyer", "sale", "selling", "message",
    "notification", "alarm", "phone", "available", "awake", "monitor",
    "bicycle", "bike",
}

CONTAMINATION_TERMS = {
    "memory.py", "retrieval.py", "promotion.py", "repository", "source tree",
    "architecture", "novel baker", "cognitive architecture", "glossary",
    "archival rule", "archiving", "digital-content guidelines",
    "presidential debate", "politics", "ebr", "context trace",
    "diagnostics", "database engine",
}


def normalize(text: str) -> str:
    return " ".join((text or "").casefold().split())


def assert_no_contamination(result: R4Result, *, turn: str) -> None:
    response = normalize(result.response_text)
    found = sorted(term for term in CONTAMINATION_TERMS if term in response)
    assert not found, f"{turn}: unrelated topic contamination found: {found}\n{result.response_text}"


def assert_sale_topic_continuity(result: R4Result, *, turn: str) -> None:
    response = normalize(result.response_text)
    matches = sorted(term for term in SALE_TOPIC_TERMS if term in response)
    assert matches, (
        f"{turn}: response did not retain the sale/nap topic.\n"
        f"Response: {result.response_text}"
    )
    assert_no_contamination(result, turn=turn)


def assert_current_conversation_only(result: R4Result, conversation_id: str) -> None:
    diag_id = str(result.diagnostic.get("conversation_id", conversation_id))
    trace_id = str(result.trace.get("conversation_id", conversation_id))
    assert result.conversation_id == conversation_id
    assert diag_id == conversation_id
    assert trace_id == conversation_id


@pytest.mark.r4_acceptance
@pytest.mark.context_integrity
def test_a13_short_acknowledgements_bind_to_immediate_topic(
    angel_r4_client: AngelR4Client,
) -> None:
    cid = angel_r4_client.new_conversation()

    first = angel_r4_client.send(
        cid,
        "Should I take a short nap while I wait for a buyer to message me?",
    )
    assert_sale_topic_continuity(first, turn="A-13 turn 1")
    assert_current_conversation_only(first, cid)

    second = angel_r4_client.send(cid, "Yes I agree with that.")
    assert_sale_topic_continuity(second, turn="A-13 turn 2")
    assert_current_conversation_only(second, cid)

    third = angel_r4_client.send(cid, "I agree that I should stay awake.")
    assert_sale_topic_continuity(third, turn="A-13 turn 3")
    assert_current_conversation_only(third, cid)

    # Acknowledgements must not unexpectedly introduce retrieved background.
    assert second.knowledge_chunks_included == 0
    assert third.knowledge_chunks_included == 0


@pytest.mark.r4_acceptance
@pytest.mark.context_integrity
def test_a14_topic_persists_across_multi_turn_conversation(
    angel_r4_client: AngelR4Client,
) -> None:
    cid = angel_r4_client.new_conversation()
    turns = (
        "I am selling a monitor online.",
        "Should I take a nap?",
        "What if the buyer messages me?",
        "Maybe I should set an alarm.",
        "Good point.",
    )

    results: list[R4Result] = []
    for index, message in enumerate(turns, start=1):
        result = angel_r4_client.send(cid, message)
        results.append(result)
        assert_current_conversation_only(result, cid)
        assert_no_contamination(result, turn=f"A-14 turn {index}")

    # The first statement may receive a simple acknowledgment. Subsequent turns
    # must retain at least one active-topic term.
    for index, result in enumerate(results[1:], start=2):
        assert_sale_topic_continuity(result, turn=f"A-14 turn {index}")

    assert all(result.knowledge_chunks_included == 0 for result in results)


@pytest.mark.r4_acceptance
@pytest.mark.context_integrity
def test_a15_cross_conversation_context_does_not_leak(
    angel_r4_client: AngelR4Client,
) -> None:
    repository_cid = angel_r4_client.new_conversation()

    repo_first = angel_r4_client.send(
        repository_cid,
        "I know the repository contains memory.py. What does it do?",
    )
    repo_second = angel_r4_client.send(
        repository_cid,
        "Compare memory.py and retrieval.py.",
    )

    assert repo_first.rag_status == "NO_EVIDENCE"
    assert repo_second.rag_status == "NO_EVIDENCE"
    assert_current_conversation_only(repo_first, repository_cid)
    assert_current_conversation_only(repo_second, repository_cid)

    sale_cid = angel_r4_client.new_conversation()
    assert sale_cid != repository_cid

    sale = angel_r4_client.send(
        sale_cid,
        "Should I take a nap while waiting for someone to buy my bicycle?",
    )

    assert_current_conversation_only(sale, sale_cid)
    assert_sale_topic_continuity(sale, turn="A-15 sale conversation")
    assert sale.knowledge_chunks_included == 0

    response = normalize(sale.response_text)
    forbidden = {
        "memory.py", "retrieval.py", "repository", "database", "ebr",
        "architecture", "source tree", "diagnostics", "context traces",
    }
    found = sorted(term for term in forbidden if term in response)
    assert not found, f"A-15 cross-conversation leak found: {found}"


@pytest.mark.asyncio
@pytest.mark.r4_acceptance
@pytest.mark.context_integrity
async def test_a15_parallel_conversations_remain_isolated(
    async_angel_r4_client,
) -> None:
    repository_cid = await async_angel_r4_client.new_conversation()
    sale_cid = await async_angel_r4_client.new_conversation()

    results = await async_angel_r4_client.send_many(
        [
            (repository_cid, "Compare memory.py and retrieval.py."),
            (sale_cid, "Should I take a nap while waiting for someone to buy my bicycle?"),
        ],
        max_concurrency=2,
    )

    repository_result, sale_result = results
    assert repository_result.conversation_id == repository_cid
    assert sale_result.conversation_id == sale_cid
    assert repository_result.rag_status == "NO_EVIDENCE"
    assert_sale_topic_continuity(sale_result, turn="A-15 async sale conversation")
    assert "memory.py" not in normalize(sale_result.response_text)
    assert "retrieval.py" not in normalize(sale_result.response_text)
