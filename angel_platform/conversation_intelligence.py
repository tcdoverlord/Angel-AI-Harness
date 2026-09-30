"""Conversation continuity helpers for Angel Platform 4.3.1-C.

This module intentionally uses deterministic, auditable heuristics rather than a
second model. It resolves short follow-ups from the immediately available
conversation context and records an explicit objective/task/deliverable state.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any


@dataclass
class ConversationState:
    current_objective: str
    current_task: str
    current_deliverable: str
    resolved_request: str
    references: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConversationIntelligence:
    REFERENCE_TERMS = ("it", "that", "this", "those", "previous design", "last build", "current project")

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "")).strip()

    @classmethod
    def _candidate_context(cls, history: list[dict[str, str]]) -> list[str]:
        return [cls._clean(x.get("content", "")) for x in history if x.get("content")]

    @classmethod
    def _resolve_reference(cls, request: str, history: list[dict[str, str]]) -> tuple[str, dict[str, str]]:
        request = cls._clean(request)
        refs: dict[str, str] = {}
        candidates = cls._candidate_context(history)
        if not candidates:
            return request, refs

        previous_user = next((x for x in reversed(history) if x.get("role") == "user" and cls._clean(x.get("content", "")) != request), None)
        previous_assistant = next((x for x in reversed(history) if x.get("role") == "assistant"), None)
        previous = cls._clean((previous_user or previous_assistant or {}).get("content", ""))
        assistant = cls._clean((previous_assistant or {}).get("content", ""))

        replacements = {
            "last build": previous,
            "previous design": previous,
            "current project": previous,
            "those": previous,
            "that": previous,
            "this": previous,
            "it": previous,
        }
        resolved = request
        # Resolve only when the reference is the short follow-up target. This
        # avoids rewriting meaningful sentences such as "fix it later" into a
        # giant transcript while still making common conversational shorthand
        # explicit for the model and diagnostics.
        lowered = request.lower()
        for term in sorted(replacements, key=len, reverse=True):
            if lowered == term or lowered.startswith(term + " "):
                target = replacements[term]
                if target:
                    refs[term] = target
                    resolved = f"{request} [Reference resolved to: {target}]"
                    break
        if lowered in {"do it again", "change that", "use the same design", "use the previous version"}:
            target = assistant or previous
            if target:
                refs[request.lower()] = target
                resolved = f"{request} [Reference resolved to: {target}]"
        return resolved, refs

    @classmethod
    def is_context_recall_request(cls, request: str) -> bool:
        """Return True when the user is asking about the active conversation itself.

        These requests should prioritize the application-managed transcript over
        background knowledge retrieval. This prevents an unrelated knowledge
        document from overriding a fact that was just stated in the conversation.
        """
        text = cls._clean(request).lower()
        patterns = (
            r"\bwhat did i (?:say|tell you|give you|ask you)\b",
            r"\bwhat was (?:the|my|that|this)\b.*\b(?:i|you)\b",
            r"\bdo you remember\b",
            r"\bdo you recall\b",
            r"\bremember what\b",
            r"\bwhat did you just\b",
            r"\bwhat did we (?:say|discuss|decide)\b",
            r"\bearlier (?:i|you|we)\b",
            r"\bprevious message\b",
            r"\bprevious conversation\b",
            r"\btest phrase\b",
        )
        return any(re.search(pattern, text) for pattern in patterns)

    @classmethod
    def deterministic_phrase_recall(cls, request: str, history: list[dict[str, str]]) -> str | None:
        """Return an exact phrase from the active transcript when the request is a
        narrowly identifiable phrase-recall question. This is deliberately
        extractive: it never invents or semantically guesses the answer.
        """
        text = cls._clean(request)
        lower = text.lower()
        if not ("test phrase" in lower or re.search(r"\bwhat was (?:the|my) phrase\b", lower)):
            # Also support an explicit "do you know <identifier>" check, but only
            # when that exact identifier occurs in the active transcript.
            m = re.search(r"\bdo you know (?:the phrase )?[`\"]?([A-Za-z0-9][A-Za-z0-9._-]{2,})[`\"]?\s*[?]?$", text, re.I)
            if not m:
                return None
            candidate = m.group(1)
            if any(candidate in str(item.get("content", "")) for item in history):
                return candidate
            return None

        # Prefer a user-authored instruction that explicitly establishes a phrase.
        pattern = re.compile(r"(?:remember|save|note|store)\s+(?:this\s+)?test\s+phrase\s*(?:for\s+this\s+conversation\s*)?[:=-]\s*[`\"]?([^`\"\n]+?)[`\"]?(?:\.|$)", re.I)
        for item in reversed(history):
            if item.get("role") != "user":
                continue
            match = pattern.search(str(item.get("content", "")))
            if match:
                return cls._clean(match.group(1)).rstrip(".")

        # Fallback for a direct phrase declaration such as "the phrase is X".
        pattern2 = re.compile(r"(?:the|my)\s+(?:test\s+)?phrase\s+is\s+[`\"]?([^`\"\n]+?)[`\"]?(?:\.|$)", re.I)
        for item in reversed(history):
            if item.get("role") != "user":
                continue
            match = pattern2.search(str(item.get("content", "")))
            if match:
                return cls._clean(match.group(1)).rstrip(".")
        return None

    @classmethod
    def analyze(cls, request: str, history: list[dict[str, str]]) -> ConversationState:
        request = cls._clean(request)
        resolved, refs = cls._resolve_reference(request, history)
        base = cls._clean(resolved.split(" [Reference resolved to:", 1)[0])

        if base.lower() in {"do it again", "change that", "use the same design", "use the previous version"} and refs:
            target = next(iter(refs.values()))
            objective = f"Continue the prior work referenced by: {target[:240]}"
            task = base
            deliverable = "An updated version of the referenced work"
        elif base.lower().startswith("use "):
            objective = base
            task = "Apply the requested technology, design, or approach to the current work"
            deliverable = "Updated current work using the requested approach"
        elif base.lower().startswith(("build ", "create ", "make ", "write ", "fix ", "change ", "update ", "implement ")):
            objective = base
            task = "Execute the requested change while preserving established context"
            deliverable = "A completed or updated implementation"
        else:
            objective = base or "Continue the current conversation"
            task = "Answer or act on the current request"
            deliverable = "A useful response addressing the current request"

        return ConversationState(objective, task, deliverable, resolved, refs)
