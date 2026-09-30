import json
import threading
import urllib.request

from angel_platform.webui import server


def test_chat_endpoint_returns_stream_instead_of_network_reset(monkeypatch):
    # Keep this smoke test deterministic and offline. The regression being guarded
    # against occurred after headers were sent when the chat handler touched its
    # runtime timing path, causing browsers to report a generic network error.
    monkeypatch.setattr(server, "ollama_available", lambda: False)
    httpd = server.run("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        payload = json.dumps({"message": "hello", "model": "llama3.2:3b"}).encode()
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            assert response.status == 200
            assert "offline mode" in body.lower()
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
