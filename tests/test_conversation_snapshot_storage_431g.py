from pathlib import Path


def test_conversation_storage_uses_per_conversation_snapshots():
    source = Path("angel_platform/webui/server.py").read_text(encoding="utf-8")
    assert 'CONVERSATIONS_DIR = DATA / "conversations"' in source
    assert 'return CONVERSATIONS_DIR / f"{safe_id}.json"' in source
    assert '_write_conversation_snapshot(conversation_id)' in source
    assert 'message_id = _CONVERSATIONS.append(conversation_id, role, content, metadata)' in source
    # Normal message writes must not append to the legacy aggregate JSON file.
    block_start = source.index("def append_history(record):")
    block_end = source.index("\ndef _migrate_modules_to_user_storage", block_start)
    block = source[block_start:block_end]
    assert 'save_json(HISTORY, records)' not in block
