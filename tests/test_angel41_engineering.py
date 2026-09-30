from pathlib import Path
from angel_platform.engineering.store import EngineeringStore
from angel_platform.engineering.lifecycle import KnowledgeEngineeringLifecycle

def test_project_context_is_preserved(tmp_path):
    store = EngineeringStore(tmp_path / "angel41.sqlite3")
    lifecycle = KnowledgeEngineeringLifecycle(store)
    context = {
        "project": {"id": "project_demo", "name": "Demo"},
        "resolved_scope": {"scope_fingerprint": "scope_1"},
        "override_applied": False,
    }
    run = lifecycle.record_rag_run(
        "How does Angel retrieve knowledge?",
        context,
        {"profile": "default", "max_knowledge_tokens": 2000},
        "index_1",
    )
    loaded = store.get_rag_run(run["id"])
    assert loaded["project_context"] == context
    assert loaded["index_fingerprint"] == "index_1"

def test_recommendation_requires_evidence(tmp_path):
    lifecycle = KnowledgeEngineeringLifecycle(EngineeringStore(tmp_path / "db.sqlite3"))
    try:
        lifecycle.recommend("weak retrieval", "improve ranking", [])
    except ValueError:
        pass
    else:
        raise AssertionError("Recommendation without evidence must fail")

def test_full_lifecycle(tmp_path):
    store = EngineeringStore(tmp_path / "db.sqlite3")
    lifecycle = KnowledgeEngineeringLifecycle(store)
    run = lifecycle.record_rag_run("test", None, {}, "idx_a")
    ev = lifecycle.evaluate(run["id"], {"classification": "SUCCESSFUL"}, "eval_v1")
    evidence = lifecycle.record_evidence(run["id"], {"chunks": ["chunk_1"]}, ev["id"])
    measurement = lifecycle.measure(
        "retrieval_success", 1.0, "evaluated", [evidence["id"]], ev["id"], 1, 1, "1"
    )
    snapshot = lifecycle.snapshot(
        {"knowledge_health": 1.0, "retrieval_health": 1.0},
        {"evidence_count": 1},
        "idx_a",
        "eval_v1",
    )
    recommendation = lifecycle.recommend(
        "none", "continue validation", [evidence["id"]]
    )
    change = lifecycle.authorize_change(None, [])
    index = lifecycle.build_index(change["id"], "idx_a", "idx_b")

    assert run["id"].startswith("rag_")
    assert ev["id"].startswith("eval_")
    assert evidence["id"].startswith("evidence_")
    assert measurement["status"] == "evaluated"
    assert snapshot["id"].startswith("snapshot_")
    assert recommendation["status"] == "proposed"
    assert change["status"] == "proposed"
    assert index["status"] == "completed"
