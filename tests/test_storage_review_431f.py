from angel_platform.storage.storage_review import run_storage_review, storage_decision


def test_storage_review_measures_growth_backup_and_recovery():
    review = run_storage_review()
    assert review["production_schema_changed"] is False
    assert [row["messages"] for row in review["growth"]] == [100, 1000, 5000]
    assert all(row["integrity_check"] == "ok" for row in review["growth"])
    assert review["backup"]["backup_ms"] >= 0
    assert review["recovery"]["restored_messages"] == 1000
    assert review["recovery"]["integrity_check"] == "ok"


def test_storage_decision_is_option_b_and_non_speculative():
    decision = storage_decision({})
    assert decision["recommendation"] == "Option B"
    assert "ConversationStore" in decision["title"]
    assert "Per-conversation JSON" in " ".join(decision["rationale"])
