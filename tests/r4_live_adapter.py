from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BASE_URL = os.getenv("ANGEL_R4_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
HOME_DATA = Path.home() / "Angel_Platform"

@dataclass(frozen=True)
class R4Result:
    conversation_id: str
    response_text: str
    rag_status: str = ""
    evidence_count: int = 0
    knowledge_chunks_included: int = 0
    diagnostic: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)


def _http(method: str, path: str, payload: dict | None = None, timeout: float = 60) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(BASE_URL + path, data=body, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", errors="replace")
        if "application/json" in (r.headers.get("Content-Type") or ""):
            return json.loads(raw)
        return raw


def _latest_jsonl(path: Path, cid: str, limit: int = 100) -> dict[str, Any]:
    if not path.exists():
        return {}
    records = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f.readlines()[-2000:]:
            try:
                item = json.loads(line)
            except Exception:
                continue
            if str(item.get("conversation_id", "")) == str(cid):
                records.append(item)
    return records[-1] if records else {}


class AngelR4Client:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")

    def new_conversation(self) -> str:
        result = _http("POST", "/api/conversations", {"title": "R4 context integrity test"})
        return str(result["conversation"]["id"])

    def send(self, conversation_id: str, message: str) -> R4Result:
        response = _http("POST", "/api/chat", {"conversation_id": conversation_id, "message": message, "model": "llama3.2:3b"}, timeout=180)
        text = response if isinstance(response, str) else str(response.get("response", ""))
        deadline = time.time() + 10
        diag = {}
        trace = {}
        while time.time() < deadline:
            try:
                api = _http("GET", "/api/context/diagnostics", timeout=5)
                rows = api.get("diagnostics", [])
                matches = [x for x in rows if str(x.get("conversation_id", "")) == str(conversation_id) and x.get("status") == "completed"]
                if matches:
                    diag = matches[-1]
                    break
            except Exception:
                pass
            time.sleep(.1)
        trace = _latest_jsonl(HOME_DATA / "context_traces.jsonl", conversation_id)
        if not diag:
            diag = _latest_jsonl(HOME_DATA / "context_diagnostics.jsonl", conversation_id)
        return R4Result(
            conversation_id=conversation_id,
            response_text=text,
            rag_status=str(diag.get("rag_status", trace.get("rag_status", ""))),
            evidence_count=int(diag.get("evidence_count", 0) or 0),
            knowledge_chunks_included=int(diag.get("knowledge_chunks_included", 0) or 0),
            diagnostic=diag,
            trace=trace,
        )

    def close(self):
        return None


class AsyncAngelR4Client:
    def __init__(self, base_url: str = BASE_URL):
        self.sync = AngelR4Client(base_url)

    async def new_conversation(self):
        return await asyncio.to_thread(self.sync.new_conversation)

    async def send(self, conversation_id: str, message: str):
        return await asyncio.to_thread(self.sync.send, conversation_id, message)

    async def send_many(self, requests, max_concurrency=4):
        sem = asyncio.Semaphore(max_concurrency)
        async def one(cid, msg):
            async with sem:
                return await self.send(cid, msg)
        return await asyncio.gather(*(one(cid, msg) for cid, msg in requests))

    async def close(self):
        self.sync.close()


def create_client():
    return AngelR4Client()

def create_async_client():
    return AsyncAngelR4Client()
