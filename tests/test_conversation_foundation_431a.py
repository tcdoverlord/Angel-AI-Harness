import json
from pathlib import Path

from angel_platform.storage.conversation_store import ConversationStore
from angel_platform.storage.database import AngelDatabase


def test_conversation_store_routes_to_existing_sqlite(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    store = ConversationStore(db)
    created = store.create("c1", "Test")
    assert created["id"] == "c1"
    message_id = store.append("c1", "user", "Hello", {"test": True})
    assert message_id > 0
    assert store.get("c1")["title"] == "Test"
    assert store.messages("c1")[0]["content"] == "Hello"
    assert store.stats()["conversations"] == 1
    assert store.stats()["messages"] == 1


def test_conversation_store_preserves_project_relationship(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    store = ConversationStore(db)
    db.create_project("p1", "Project")
    store.create("c1", "Test")
    store.set_project("c1", "p1")
    assert store.get("c1")["project_id"] == "p1"


def test_legacy_migration_remains_supported(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    store = ConversationStore(db)
    history = tmp_path / "chat_history.json"
    history.write_text(json.dumps([
        {"role": "user", "content": "Legacy", "conversation_id": "legacy-c"},
        {"role": "assistant", "content": "Reply", "conversation_id": "legacy-c"},
    ]), encoding="utf-8")
    assert store.migrate_legacy_history(history) == 2
    assert [m["content"] for m in store.messages("legacy-c")] == ["Legacy", "Reply"]
