from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass(frozen=True)
class R4Result:
    conversation_id: str
    response_text: str
    rag_status: str = ""
    evidence_count: int = 0
    knowledge_chunks_included: int = 0
    diagnostic: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)

class AngelR4Client(Protocol):
    def new_conversation(self) -> str: ...
    def send(self, conversation_id: str, message: str) -> R4Result: ...
