"""Non-destructive conversation summarization for Angel Platform 4.3.1-E."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any


@dataclass
class ConversationSummary:
    conversation_id: str
    message_count: int
    generated_at: str
    decisions: list[str]
    actions: list[str]
    open_questions: list[str]
    project_status: list[str]
    important_context: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        sections = [
            ("Decisions", self.decisions),
            ("Actions", self.actions),
            ("Open Questions", self.open_questions),
            ("Project Status", self.project_status),
            ("Important Context", self.important_context),
        ]
        lines = [f"Conversation summary ({self.message_count} messages):"]
        for name, values in sections:
            lines.append(f"{name}:")
            lines.extend(f"- {value}" for value in (values or ["None recorded."]))
        return "\n".join(lines)


class ConversationSummaryService:
    """Create compact, deterministic summaries while preserving the transcript."""

    REFRESH_INTERVAL = 50

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "")).strip()

    @classmethod
    def _select(cls, messages: list[dict[str, Any]], patterns: tuple[str, ...], limit: int = 8) -> list[str]:
        found: list[str] = []
        for item in messages:
            text = cls._clean(item.get("content", ""))
            if not text:
                continue
            lower = text.lower()
            if any(re.search(pattern, lower) for pattern in patterns):
                if text not in found:
                    found.append(text[:500])
            if len(found) >= limit:
                break
        return found

    @classmethod
    def generate(cls, conversation_id: str, messages: list[dict[str, Any]], generated_at: str) -> ConversationSummary:
        decisions = cls._select(messages, (r"\bdecided\b", r"\bdecision\b", r"\buse \w+", r"\bchosen\b", r"\bwe will\b"))
        actions = cls._select(messages, (r"\bbuild\b", r"\bcreate\b", r"\bimplement\b", r"\bfix\b", r"\bupdate\b", r"\bneed to\b", r"\bwill \w+"))
        questions = cls._select(messages, (r"\?", r"\bopen question\b", r"\bunknown\b", r"\bneed to determine\b"))
        status = cls._select(messages, (r"\bstatus\b", r"\bcomplete\b", r"\bcompleted\b", r"\bworking\b", r"\bbuild 4\.3\.1\b", r"\brelease\b"))

        # Keep the most recent substantive exchanges as durable context. This is
        # intentionally extractive: no original transcript is rewritten or lost.
        recent = [cls._clean(x.get("content", ""))[:500] for x in messages[-10:] if cls._clean(x.get("content", ""))]
        important: list[str] = []
        for text in recent:
            if text and text not in important:
                important.append(text)
        return ConversationSummary(conversation_id, len(messages), generated_at, decisions[:8], actions[:8], questions[:8], status[:8], important[:8])
