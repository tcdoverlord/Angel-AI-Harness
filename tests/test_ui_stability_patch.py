from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_chat_stability_contract():
    app = (ROOT / "angel_platform" / "webui" / "app.js").read_text(encoding="utf-8")
    assert "window.angelConversationId=null;" in app
    assert "Fresh conversation started" not in app
    assert "Welcome to Just Chat" not in app
    assert "addMessage('Me',text)" in app
    assert "who==='Me'?'M':'🪽'" in app
    assert "currently opened chat blank" in app


def test_history_append_is_serialized():
    server = (ROOT / "angel_platform" / "webui" / "server.py").read_text(encoding="utf-8")
    assert "_HISTORY_LOCK = threading.RLock()" in server
    assert "with _HISTORY_LOCK:" in server
    assert "_CONTEXT_ASSEMBLER.assemble(" in server
    assert "knowledge_context=context_for" in server


def test_modules_use_user_owned_storage():
    server = (ROOT / "angel_platform" / "webui" / "server.py").read_text(encoding="utf-8")
    assert 'USER_DATA = Path.home() / "Angel_Platform"' in server
    assert 'MODULES_DIR = USER_DATA / "modules"' in server
    assert 'GITHUB_MODULES_DIR = MODULES_DIR / "github_modules"' in server
    assert 'MODULES_DIR = PROJECT / "modules"' not in server
    assert 'GITHUB_MODULES_DIR = MODULES_DIR / "github_modules"' in server


def test_legacy_module_migration_is_conservative():
    server = (ROOT / "angel_platform" / "webui" / "server.py").read_text(encoding="utf-8")
    assert 'shutil.move(str(legacy), str(target))' in server
    assert 'Never delete a legacy copy automatically' in server
    assert 'if target.exists() and target.is_dir():' in server
