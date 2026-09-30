"""Centralized context construction for Angel Platform 4.3.1-B.

The ContextAssembler owns the shape and ordering of the model context. It is
intentionally dependency-light so the web handler can remain responsible for
HTTP, persistence, routing, and streaming rather than prompt construction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from angel_platform.conversation_intelligence import ConversationIntelligence


@dataclass
class ContextAssembly:
    messages: list[dict[str, str]]
    trace: dict[str, Any]
    token_estimates: dict[str, int]
    truncation_events: list[str] = field(default_factory=list)


class ContextAssembler:
    """Build the complete model context in one deterministic place."""

    HISTORY_LIMIT = 20

    def __init__(
        self,
        *,
        capability_report: Callable[[], str],
        knowledge_context: Callable[[str, int], str | None],
        project_context: Callable[[str | None], dict | None],
        estimate_tokens: Callable[[str], int],
    ) -> None:
        self._capability_report = capability_report
        self._knowledge_context = knowledge_context
        self._project_context = project_context
        self._estimate_tokens = estimate_tokens

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()

    def assemble(
        self,
        *,
        request: str,
        history: list[dict[str, str]],
        model: str,
        lane: str,
        project_id: str | None = None,
        knowledge_hits: list[dict] | None = None,
        evidence: list[dict] | None = None,
        tool_results: list[dict] | None = None,
        conversation_state: dict[str, Any] | None = None,
        confidence: dict[str, Any] | None = None,
        conversation_summary: str | None = None,
        supported_evidence: list[dict] | None = None,
        inferences: list[dict] | None = None,
        unknowns: list[str] | None = None,
        suppress_background_knowledge: bool = False,
    ) -> ContextAssembly:
        request = self._text(request)
        history = [
            {"role": self._text(item.get("role")), "content": self._text(item.get("content"))}
            for item in history
            if item.get("role") in {"user", "assistant", "system"} and self._text(item.get("content"))
        ]
        knowledge_hits = list(knowledge_hits or [])
        evidence = list(evidence or [])
        tool_results = list(tool_results or [])
        supported_evidence = list(supported_evidence or [])
        inferences = list(inferences or [])
        unknowns = list(unknowns or [])
        conversation_state = dict(conversation_state or {})
        confidence = dict(confidence or {})

        truncation_events: list[str] = []
        if len(history) > self.HISTORY_LIMIT:
            history = history[-self.HISTORY_LIMIT :]
            truncation_events.append(f"conversation_history_limit_{self.HISTORY_LIMIT}")

        now = datetime.now().astimezone()
        day_number = now.strftime("%-d") if now.tzname() and __import__("os").name != "nt" else now.strftime("%#d")
        date_context = (
            f"Authoritative application clock: {now.isoformat()} "
            f"({now.strftime('%A, %B')} {day_number}, {now.strftime('%Y')}, "
            f"{now.strftime('%I:%M:%S %p').lstrip('0')}, timezone {now.tzname() or 'local'}). "
            "The application calculated this weekday from its local clock. Treat it as authoritative. "
            "Never recalculate or guess the weekday from memory, UTC, or a prior message. "
            "Use this context for date/time questions; do not claim that the current date or time is unavailable."
        )

        project = self._project_context(project_id)
        conversation_recall = ConversationIntelligence.is_context_recall_request(request)
        knowledge = None if (conversation_recall or suppress_background_knowledge) else self._knowledge_context(request, 6)

        blocks: list[dict[str, Any]] = []
        system_rules = (
            "You are Angel, the warm conversational heart of Angel Nexus. "
            "Speak naturally, kindly, and directly, like a dependable teammate who is present and attentive. "
            "Use the user's name only when it feels natural, avoid repetitive corporate wording, and do not over-explain simple answers. "
            "Acknowledge the user's goal before giving practical help, ask one clear follow-up question when needed, and be honest about uncertainty. "
            "Keep warmth grounded: never pretend to have feelings, memories, actions, or abilities that were not actually provided by the application. "
            "Hold a natural conversation, ask clarifying questions when useful, and do not invoke or imply tools "
            "unless the user explicitly requests the related action. Never execute system changes without explicit approval. "
            f"Cooperative AI lane selected: {lane}. This is a routing hint, not a separate conversation. All lanes share Angel's context and must support one another. "
            + date_context + " " + self._capability_report() + " "
            "Treat the capability report as authoritative for this session. Conversation history is application-managed local storage, not cloud storage or GitHub storage. "
            "Persistent memory is not the same as chat history; do not claim either is saved unless the application reports it. "
            "Never claim a command, API call, lookup, repair, or change occurred unless a verified application result is supplied. "
            "For questions about what the user previously said, gave, asked, or discussed, treat the supplied conversation history as the primary source of truth. "
            "Do not replace active conversation facts with retrieved background knowledge. If the requested detail is absent from the supplied history, say it is not available rather than inventing a source or explanation. "
            "When evidence is available, distinguish Facts supported by evidence, Open Questions where evidence is missing or conflicting, and Recommendations as clearly labeled suggestions. "
            "Use the supplied confidence level as an evidence-coverage signal, not as proof of truth. If confidence is Low or Unknown, state the relevant uncertainty instead of filling gaps with assumptions. "
            "If no result is supplied, say it was not performed."
        )
        blocks.append({"name": "system_rules", "text": system_rules, "always": True})

        objective = conversation_state.get("current_objective") or (
            f"Current objective: respond to the user's current request using the selected cooperative lane ({lane}), "
            "while preserving the conversation's established context and verified application facts."
        )
        task = conversation_state.get("current_task") or "Answer or act on the current request"
        deliverable = conversation_state.get("current_deliverable") or "A useful response addressing the current request"
        objective_text = (
            f"Current objective: {objective}\n"
            f"Current task: {task}\n"
            f"Current deliverable: {deliverable}"
        )
        blocks.append({"name": "current_objective", "text": objective_text, "always": True})

        resolved_request = conversation_state.get("resolved_request") or request
        blocks.append({"name": "current_request", "text": resolved_request, "always": True})

        if conversation_recall and history:
            transcript_lines = []
            for item in history:
                role = self._text(item.get("role")).upper()
                transcript_lines.append(f"{role}: {self._text(item.get('content'))}")
            blocks.append({
                "name": "active_conversation_evidence",
                "text": (
                    "AUTHORITATIVE ACTIVE CONVERSATION EVIDENCE. "
                    "For this recall question, use this transcript as the primary and authoritative source. "
                    "Do not substitute older knowledge, documents, or unrelated context. "
                    "If the requested detail is not present here, say so.\n\n"
                    + "\n".join(transcript_lines)
                ),
                "always": True,
            })

        if conversation_summary:
            blocks.append({"name": "conversation_summary", "text": conversation_summary, "always": False})

        if confidence:
            confidence_text = (
                f"Evidence confidence: {self._text(confidence.get("level", "Unknown"))}. "
                f"Evidence count: {confidence.get("evidence_count", 0)}. "
                f"Source count: {confidence.get("source_count", 0)}. "
                f"Conflicts detected: {confidence.get("conflicts_detected", 0)}. "
                f"Support strength: {self._text(confidence.get("support_strength", "none"))}. "
                f"Open questions: {"; ".join(confidence.get("open_questions", [])) or "None identified."}"
            )
            blocks.append({"name": "evidence_confidence", "text": confidence_text, "always": False})

        if project:
            project_text = (
                f"Project context: {project['project']['name']} (id {project['project']['id']}). "
                f"Resolved scope: {project['resolved_scope']}. "
                f"Scope fingerprint: {project['scope_fingerprint']}."
            )
            blocks.append({"name": "project_context", "text": project_text, "always": False})

        if knowledge:
            blocks.append({"name": "relevant_knowledge", "text": knowledge, "always": False})

        if evidence:
            blocks.append({"name": "evidence", "text": "Verified evidence:\n" + "\n".join(self._text(x.get("content", x)) for x in evidence), "always": False})

        if supported_evidence:
            lines = []
            for claim in supported_evidence:
                lines.append(
                    f"FACT | key={self._text(claim.get('normalized_key'))} | "
                    f"claim={self._text(claim.get('claim_text'))} | "
                    f"source_claim_id={self._text(claim.get('id'))}"
                )
            blocks.append({"name": "supported_evidence", "text": "[SUPPORTED EVIDENCE]\n" + "\n".join(lines), "always": False})

        if inferences:
            lines = [self._text(x.get("claim_text", x)) if isinstance(x, dict) else self._text(x) for x in inferences]
            blocks.append({"name": "inferences", "text": "[INFERENCES]\n" + "\n".join(lines), "always": False})

        if unknowns:
            blocks.append({"name": "unknowns", "text": "[UNKNOWNS]\n" + "\n".join(self._text(x) for x in unknowns), "always": False})

        if tool_results:
            blocks.append({"name": "tool_results", "text": "Verified tool results:\n" + "\n".join(self._text(x.get("content", x)) for x in tool_results), "always": False})

        prompt_messages = [{"role": "system", "content": "\n\n".join(b["text"] for b in blocks)}]
        prompt_messages.extend(history)

        trace_blocks = [
            {"name": b["name"], "included": True, "text": b["text"], "token_estimate": self._estimate_tokens(b["text"])}
            for b in blocks
        ]
        trace = {
            "model": model,
            "history_limit": self.HISTORY_LIMIT,
            "history_messages_included": len(history),
            "context_blocks": trace_blocks,
            "context_order": [b["name"] for b in blocks] + ["conversation_history"],
            "truncation_events": truncation_events,
            "exact_model_messages": prompt_messages,
            "conversation_state": conversation_state,
            "conversation_recall_request": conversation_recall,
            "knowledge_retrieval_suppressed": bool(conversation_recall or suppress_background_knowledge),
        }
        token_estimates = {
            "system": self._estimate_tokens(prompt_messages[0]["content"]),
            "conversation_history": self._estimate_tokens("\n".join(x["content"] for x in history)),
            "total": self._estimate_tokens("\n".join(x["content"] for x in prompt_messages)),
        }
        return ContextAssembly(prompt_messages, trace, token_estimates, truncation_events)
