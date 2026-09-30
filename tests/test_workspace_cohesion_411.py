from pathlib import Path

from angel_platform.storage.database import AngelDatabase
import angel_platform.knowledge.library as library


def test_new_chat_can_remain_global_after_project_selection(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    project = db.create_project("project_a", "Project A")
    global_chat = db.create_conversation("global_chat", "Global Chat")
    project_chat = db.create_conversation("project_chat", "Project Chat")
    db.set_conversation_project(project_chat["id"], project["id"])

    assert db.get_conversation(global_chat["id"])["project_id"] == ""
    assert db.get_conversation(project_chat["id"])["project_id"] == project["id"]


def test_pack_documents_can_be_written_and_pack_deleted_without_history_loss(tmp_path, monkeypatch):
    root = tmp_path / "knowledge"
    packs = root / "packs"
    files = root / "files"
    index = root / "index"
    for path in (packs, files, index):
        path.mkdir(parents=True)
    monkeypatch.setattr(library, "USER_KNOWLEDGE", root)
    monkeypatch.setattr(library, "PACKS_DIR", packs)
    monkeypatch.setattr(library, "FILES_DIR", files)
    monkeypatch.setattr(library, "INDEX_DIR", index)
    monkeypatch.setattr(library, "INDEX_FILE", index / "index.json")

    pack = packs / "pack-a"
    (pack / "knowledge").mkdir(parents=True)
    (pack / "manifest.json").write_text('{"name":"Pack A","version":"1.0.0"}', encoding="utf-8")
    doc = pack / "knowledge" / "guide.md"
    doc.write_text("# Pack A\n\nUnique retrieval text.", encoding="utf-8")

    assert library.read_user_document("packs/pack-a/knowledge/guide.md")["content"].startswith("# Pack A")
    library.write_user_document("packs/pack-a/knowledge/guide.md", "# Pack A Updated\n\nNew text.")
    assert "Updated" in library.read_user_document("packs/pack-a/knowledge/guide.md")["content"]
    assert any(x["path"] == "packs/pack-a/knowledge/guide.md" for x in library._load_user_index()["chunks_data"])

    result = library.delete_knowledge_pack("pack-a")
    assert result["deleted"] == "pack-a"
    assert not pack.exists()
    assert not any(x.get("pack") == "pack-a" for x in library._load_user_index()["chunks_data"])


def test_ui_contract_enforces_workspace_and_exact_pack_selection():
    app = Path(__file__).parents[1] / "angel_platform" / "webui" / "app.js"
    source = app.read_text(encoding="utf-8")
    assert "createServerConversation(text.slice(0,70),'')" in source
    assert "body:JSON.stringify({message:text,model:$('#model').value,conversation_id:window.angelConversationId})" in source
    assert "selectedPackId=el.dataset.pack" in source
    assert "selectedDocumentPath=null;renderKnowledge()" in source
    assert "/api/knowledge/pack" in source


def test_backend_chat_uses_persisted_conversation_scope():
    server = Path(__file__).parents[1] / "angel_platform" / "webui" / "server.py"
    source = server.read_text(encoding="utf-8")
    assert 'project_id = str((persisted_conversation or {}).get("project_id", "") or "").strip()' in source
    assert "_DATABASE.set_conversation_project(conversation_id, project_id)" not in source[source.index('if self.path == "/api/chat":'):source.index('lane = choose_ai_lane', source.index('if self.path == "/api/chat":'))]


def test_project_delete_preserves_conversations_as_global_history(tmp_path):
    db = AngelDatabase(tmp_path / "angel.sqlite3")
    project = db.create_project("project_delete", "Delete Me")
    conversation = db.create_conversation("project_chat", "Project Chat")
    db.set_conversation_project(conversation["id"], project["id"])

    deleted = db.delete_project(project["id"])

    assert deleted["id"] == project["id"]
    assert deleted["conversation_count"] == 1
    assert db.get_project(project["id"]) is None
    assert db.get_conversation(conversation["id"])["project_id"] == ""


def test_project_delete_ui_contract():
    root = Path(__file__).parents[1]
    app = (root / "angel_platform" / "webui" / "app.js").read_text(encoding="utf-8")
    server = (root / "angel_platform" / "webui" / "server.py").read_text(encoding="utf-8")
    assert 'data-delete-project' in app
    assert "confirmDestructive({title:'Delete Project?'" in app
    assert "/api/projects/'+encodeURIComponent(p.id)+'/delete" in app
    assert "await refreshConversationHistory();renderProjects();" in app
    assert 'self.path.startswith("/api/projects/") and self.path.endswith("/delete")' in server
    assert '_DATABASE.delete_project(project_id)' in server
