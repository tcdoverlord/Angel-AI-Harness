from pathlib import Path

APP = Path(__file__).parents[1] / "angel_platform" / "webui" / "app.js"


def test_read_aloud_has_single_global_controller():
    text = APP.read_text(encoding="utf-8")
    assert "let activeReader=null;" in text
    assert "function stopReading()" in text
    assert "function startReading(text,button)" in text
    assert "window.speechSynthesis.cancel()" in text


def test_read_aloud_toggles_stop_control():
    text = APP.read_text(encoding="utf-8")
    assert "stopButton.textContent='◼ Stop';" in text
    assert "<span class=\"speak-icon\" aria-hidden=\"true\">🔊</span><span>Read Aloud</span>" in text
    assert "if(activeReader?.button===button){stopReading();return;}" in text
    assert "stopButton.onclick=()=>stopReading();" in text


def test_read_aloud_stops_on_navigation_and_new_message():
    text = APP.read_text(encoding="utf-8")
    assert "async function loadConversation(id){\n stopReading();" in text
    assert "async function startNewChat(){stopReading();" in text
    assert "async function send(){\n stopReading();" in text
    assert "function renderPage(page){\n stopReading();" in text
    assert "window.addEventListener('beforeunload',stopReading);" in text


def test_read_aloud_has_accessible_speaking_indicator_and_tooltips():
    text = APP.read_text(encoding="utf-8")
    assert 'role="status" aria-live="polite"' in text
    assert 'data-speaking-status' in text
    assert '🔊' in text
    assert 'Speaking...' in text
    assert 'Reading response aloud' in text
    assert 'Read this response aloud' in text
    assert 'Currently reading this response aloud' in text
    assert 'Stop audio playback' in text
    assert "stopButton.setAttribute('aria-label','Stop reading aloud');" in text
    assert "button.setAttribute('aria-pressed','true');" in text
    assert "reader.status.hidden=true" in text


def test_read_aloud_css_respects_reduced_motion_and_tooltips():
    css = (APP.parent / "styles.css").read_text(encoding="utf-8")
    assert '@media (prefers-reduced-motion: reduce)' in css
    assert '.speaking-indicator .speaking-icon{animation:none}' in css
    assert '[data-tooltip]::after' in css
    assert ':focus-visible::after' in css
