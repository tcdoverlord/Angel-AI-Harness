from __future__ import annotations

import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from .lifecycle import KnowledgeEngineeringLifecycle

CONTRACT = Path(__file__).resolve().parents[2] / "api" / "Angel_4.1_Canonical_OpenAPI.yaml"
lifecycle = KnowledgeEngineeringLifecycle()

def problem(status, code, detail):
    return {
        "type": f"https://angel.local/problems/{code.lower()}",
        "title": code.replace("_", " ").title(),
        "status": status,
        "code": code,
        "detail": detail,
    }

class Handler(BaseHTTPRequestHandler):
    server_version = "Angel4.1Engineering/0.1"

    def _send(self, status, payload, content_type="application/json"):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/v1/health":
            return self._send(200, {
                "status": "ok",
                "contract": "4.1.0",
                "service": "knowledge-engineering-foundation",
            })
        if path == "/api/v1/rag-runs":
            return self._send(200, {"items": lifecycle.store.list_rag_runs()})
        if path.startswith("/api/v1/rag-runs/"):
            rid = path.rsplit("/", 1)[-1]
            record = lifecycle.store.get_rag_run(rid)
            if record is None:
                return self._send(404, problem(404, "RAG_RUN_NOT_FOUND", "The requested RAG Run does not exist."))
            return self._send(200, record)
        if path == "/openapi.yaml":
            body = CONTRACT.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/yaml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return self._send(404, problem(404, "RESOURCE_NOT_FOUND", "The requested resource does not exist."))

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self._json()
        except Exception:
            return self._send(400, problem(400, "INVALID_REQUEST", "Request body must be valid JSON."))

        if path == "/api/v1/rag-runs":
            question = str(data.get("question", "")).strip()
            if not question:
                return self._send(422, problem(422, "QUESTION_REQUIRED", "question is required."))
            record = lifecycle.record_rag_run(
                question,
                data.get("project_context"),
                data.get("retrieval_config") or {},
                data.get("index_fingerprint"),
            )
            return self._send(201, record)

        if path == "/api/v1/evaluations":
            rid = str(data.get("rag_run_id", "")).strip()
            if not lifecycle.store.get_rag_run(rid):
                return self._send(404, problem(404, "RAG_RUN_NOT_FOUND", "The referenced RAG Run does not exist."))
            return self._send(201, lifecycle.evaluate(
                rid, data.get("result") or {}, data.get("evaluation_set_id")
            ))

        if path == "/api/v1/evidence":
            rid = str(data.get("rag_run_id", "")).strip()
            if not lifecycle.store.get_rag_run(rid):
                return self._send(404, problem(404, "RAG_RUN_NOT_FOUND", "The referenced RAG Run does not exist."))
            return self._send(201, lifecycle.record_evidence(
                rid, data.get("evidence") or {}, data.get("evaluation_id")
            ))

        if path == "/api/v1/measurements":
            return self._send(201, lifecycle.measure(
                str(data.get("metric", "")),
                data.get("value"),
                str(data.get("status", "not_evaluated")),
                data.get("evidence_ids") or [],
                data.get("evaluation_id"),
                data.get("numerator"),
                data.get("denominator"),
                str(data.get("calculation_version", "1")),
            ))

        if path == "/api/v1/snapshots":
            return self._send(201, lifecycle.snapshot(
                data.get("health") or {},
                data.get("evidence_summary") or {},
                data.get("index_fingerprint"),
                data.get("evaluation_set_version"),
            ))

        if path == "/api/v1/recommendations":
            try:
                return self._send(201, lifecycle.recommend(
                    str(data.get("problem", "")),
                    str(data.get("recommendation", "")),
                    data.get("evidence_ids") or [],
                ))
            except ValueError as exc:
                return self._send(422, problem(422, "RECOMMENDATION_EVIDENCE_MISSING", str(exc)))

        if path == "/api/v1/knowledge-changes":
            return self._send(201, lifecycle.authorize_change(
                data.get("project_id"), data.get("items") or []
            ))

        if path == "/api/v1/index-builds":
            return self._send(201, lifecycle.build_index(
                data.get("change_set_id"),
                data.get("source_fingerprint"),
                data.get("target_fingerprint"),
            ))

        return self._send(404, problem(404, "RESOURCE_NOT_FOUND", "The requested resource does not exist."))

    def log_message(self, fmt, *args):
        return

def run(host="127.0.0.1", port=8780):
    server = ThreadingHTTPServer((host, port), Handler)
    return server
