from pathlib import Path

APP = Path(__file__).parents[1] / "angel_platform" / "webui" / "app.js"
CSS = Path(__file__).parents[1] / "angel_platform" / "webui" / "styles.css"

def test_destructive_dialog_focuses_cancel_and_traps_focus():
    s = APP.read_text(encoding="utf-8")
    assert "role=\"dialog\" aria-modal=\"true\"" in s
    assert "cancel.focus();" in s
    assert "if(e.key==='Escape')" in s
    assert "if(e.key==='Tab')" in s
    assert "e.shiftKey&&document.activeElement===first" in s
    assert "document.activeElement===last" in s


def test_destructive_actions_use_accessible_dialog_not_native_confirm():
    s = APP.read_text(encoding="utf-8")
    assert "confirmDestructive({title:'Delete Chat?'" in s
    assert "confirmDestructive({title:'Remove Knowledge Pack?'" in s
    assert "confirmDestructive({title:'Delete Knowledge Document?'" in s
    assert "if(!confirm('Delete this conversation permanently?'))" not in s
    assert "if(!confirm('Delete this knowledge document permanently?" not in s


def test_dialog_has_visible_focus_and_reduced_motion_support():
    s = CSS.read_text(encoding="utf-8")
    assert ".confirm-actions [data-dialog-cancel]:focus-visible" in s
    assert ".dialog-backdrop" in s
    assert "prefers-reduced-motion:reduce" in s
