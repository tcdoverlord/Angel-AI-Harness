from angel_platform.storage.database import AngelDatabase
from angel_platform.engineering.lifecycle import KnowledgeEngineeringLifecycle


def test_project_workspace_persists_and_can_own_conversation(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    project = db.create_project("project_demo", "Angel Nexus", "Focused workspace")
    conversation = db.create_conversation("conv_demo", "RAG work")
    db.set_conversation_project(conversation["id"], project["id"])
    loaded = db.get_conversation(conversation["id"])
    assert loaded["project_id"] == project["id"]
    assert db.list_projects()[0]["conversation_count"] == 1


def test_rag_answer_update_and_evidence_are_inspectable(tmp_path):
    lifecycle = KnowledgeEngineeringLifecycle()
    lifecycle.store.path = tmp_path / "engineering.sqlite3"
    lifecycle.store._init()
    run = lifecycle.record_rag_run(
        "How does Angel retrieve knowledge?",
        {"project": {"id": "project_demo", "name": "Angel Nexus"}, "override_applied": False},
        {"conversation_id": "conv_demo", "candidate_count": 2},
        "index_demo",
    )
    lifecycle.store.update_rag_run_answer(run["id"], "Angel retrieves bounded knowledge context.")
    evidence = lifecycle.record_evidence(run["id"], {"retrieved": True, "token_count": 100})
    loaded = lifecycle.store.get_rag_run(run["id"])
    assert loaded["answer"] == "Angel retrieves bounded knowledge context."
    assert lifecycle.store.list_evidence(run["id"])[0]["id"] == evidence["id"]
