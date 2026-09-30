from pathlib import Path

def test_unified_workspace_navigation_contract():
    root = Path(__file__).parents[1] / "angel_platform" / "webui"
    html = (root / "index.html").read_text(encoding="utf-8")
    app = (root / "app.js").read_text(encoding="utf-8")
    assert 'data-page="home"' in html
    assert 'data-page="chat"' in html
    assert 'data-page="projects"' in html
    assert 'data-page="knowledge"' in html
    assert 'data-page="memory"' not in html
    assert 'data-page="skills"' in html
    assert 'id="conversationSearch"' in html
    assert 'data-mode="chat"' not in html
    assert 'data-mode="work"' not in html
    assert 'id="contextPanel"' in html
    assert 'renderConversationTree' in app
    assert 'renderContext' in app
    assert "page==='memory'" not in app
    assert '<label>Memory</label>' not in app
    assert 'homeAnalyze' not in app
    assert 'Knowledge library ready' in app
    assert 'Future ideas' in app
    assert 'renderWorkView' not in app
    assert 'setMode(' not in app

def test_evidence_is_progressive_disclosure():
    app = (Path(__file__).parents[1] / "angel_platform" / "webui" / "app.js").read_text(encoding="utf-8")
    assert 'className="evidence-card collapsed"' in app
    assert 'Retrieval Scope' in app
    assert 'Evaluation' in app
    assert 'Inspect Retrieval' in app

def test_workspace_summary_endpoint_contract():
    server = (Path(__file__).parents[1] / "angel_platform" / "webui" / "server.py").read_text(encoding="utf-8")
    assert 'self.path.startswith("/api/workspace/summary")' in server
    assert '"retrieval_scope"' in server
    assert '"skills"' in server
    assert '"tools"' in server
    assert '"model"' in server
    assert '"cards"' in server

def test_project_workspace_does_not_rewrite_conversation_scope():
    app = (Path(__file__).parents[1] / "angel_platform" / "webui" / "app.js").read_text(encoding="utf-8")
    project_start = app[app.index("c.querySelectorAll('[data-project]')"):app.index("async function renderKnowledge")]
    assert "setActiveProject(p)" in project_start
    assert "set_conversation_project" not in project_start
    assert "createServerConversation('New '+p.name+' Chat',p.id)" in project_start

def test_4_2_build_manifest_exists():
    manifest = Path(__file__).parents[1] / "docs" / "manifests" / "ANGEL_4.2_BUILD_MANIFEST.json"
    assert manifest.exists()
