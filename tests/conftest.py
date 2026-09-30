from __future__ import annotations

import json
import os
import threading
import urllib.request
from pathlib import Path

import pytest


class AngelHTTPClient:
    def __init__(self, base_url: str, server_module):
        self.base_url = base_url.rstrip("/")
        self.server = server_module

    def _request(self, method: str, path: str, payload=None):
        body = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path, data=body, headers=headers, method=method
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw.decode("utf-8"))
        return raw.decode("utf-8", errors="replace")

    def create_conversation(self, title="EBR test") -> str:
        result = self._request("POST", "/api/conversations", {"title": title})
        return str(result["conversation"]["id"])

    def chat(self, conversation_id: str, message: str) -> str:
        return self._request(
            "POST", "/api/chat",
            {"conversation_id": conversation_id, "message": message},
        )

    def trace_records(self, conversation_id: str):
        records = []
        for name, loader in (
            ("diagnostic", lambda: self.server.load_context_diagnostics(conversation_id, 100)),
            ("trace", lambda: self.server.load_context_traces(conversation_id, 100)),
        ):
            try:
                records.extend(loader())
            except Exception:
                pass
        return records

    def latest_diagnostic(self, conversation_id: str):
        records = [r for r in self.server.load_context_diagnostics(100) if str(r.get("conversation_id", "")) == str(conversation_id)]
        return records[0] if records else None

    def latest_trace(self, conversation_id: str):
        records = self.server.load_context_traces(conversation_id, 100)
        return records[0] if records else None


@pytest.fixture(scope="session")
def angel_client(tmp_path_factory, monkeypatch_session):
    data_dir = tmp_path_factory.mktemp("angel_home")
    monkeypatch_session.setenv("HOME", str(data_dir))
    monkeypatch_session.setenv("ENABLE_PROVENANCE_V1", "true")

    import importlib
    import angel_platform.storage.database as database
    import angel_platform.webui.server as server
    database._default_database = None
    server = importlib.reload(server)

    httpd = server.run("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    client = AngelHTTPClient(f"http://127.0.0.1:{httpd.server_address[1]}", server)
    try:
        yield client
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


@pytest.fixture(scope="session")
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch
    patch = MonkeyPatch()
    yield patch
    patch.undo()

@pytest.fixture
def angel_r4_client():
    import importlib
    module_name = os.getenv("ANGEL_R4_ADAPTER", "tests.r4_live_adapter")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.skip(f"Live adapter not available: {module_name}")
    client = module.create_client()
    try:
        yield client
    finally:
        close = getattr(client, "close", None)
        if close:
            close()

@pytest.fixture
async def async_angel_r4_client():
    import importlib
    module_name = os.getenv("ANGEL_R4_ADAPTER", "tests.r4_live_adapter")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.skip(f"Live adapter not available: {module_name}")
    factory = getattr(module, "create_async_client", None)
    if factory is None:
        pytest.skip(f"Async adapter factory missing from {module_name}")
    client = factory()
    try:
        yield client
    finally:
        await client.close()
