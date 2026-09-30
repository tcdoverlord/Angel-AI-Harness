"""Evidence-aware confidence heuristics for Angel Platform 4.3.1-D.

This is an auditable evidence-coverage signal, not a claim that a model's answer
is objectively true. It deliberately returns Unknown when no supporting evidence
is available.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any


@dataclass
class ConfidenceAssessment:
    level: str
    evidence_count: int
    source_count: int
    conflicts_detected: int
    support_strength: str
    evidence: list[dict[str, Any]]
    open_questions: list[str]
    notes: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvidenceConfidence:
    LEVELS = ("High", "Medium", "Low", "Unknown")

    @staticmethod
    def _text(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @classmethod
    def _terms(cls, text: str) -> set[str]:
        return {x for x in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower())}

    @classmethod
    def assess(cls, request: str, evidence: list[dict[str, Any]] | None = None) -> ConfidenceAssessment:
        items = list(evidence or [])
        request_terms = cls._terms(request)
        normalized: list[dict[str, Any]] = []
        sources: set[str] = set()
        for item in items:
            content = cls._text(item.get("content", item.get("passage", item)))
            source = cls._text(item.get("source", item.get("title", "Unknown source"))) or "Unknown source"
            title = cls._text(item.get("title", source)) or source
            overlap = len(request_terms & cls._terms(content))
            sources.add(source)
            normalized.append({
                "title": title,
                "source": source,
                "content": content[:1800],
                "support_overlap_terms": overlap,
            })

        conflicts = 0
        for i, left in enumerate(normalized):
            for right in normalized[i + 1:]:
                left_text = left["content"].lower()
                right_text = right["content"].lower()
                shared = cls._terms(left_text) & cls._terms(right_text) & request_terms
                # Conservative conflict heuristic: only count an explicit
                # negation pattern around a shared request term. It is a flag
                # for review, not a semantic contradiction engine.
                if shared and (("not " in left_text and "not " not in right_text) or
                               ("not " in right_text and "not " not in left_text)):
                    conflicts += 1

        total_overlap = sum(x["support_overlap_terms"] for x in normalized)
        if not normalized:
            level = "Unknown"
            strength = "none"
            open_questions = ["What evidence supports the requested claim or action?"]
            notes = ["No supporting evidence was available in the current context."]
        elif conflicts:
            level = "Low"
            strength = "conflicted"
            open_questions = ["Which source is authoritative where the retrieved evidence conflicts?"]
            notes = ["Conflicting evidence was detected by a conservative heuristic; review the sources before treating the claim as established."]
        elif len(sources) >= 2 and total_overlap >= 2:
            level = "High"
            strength = "strong"
            open_questions = []
            notes = ["Multiple sources provide relevant retrieved support. This is an evidence-coverage signal, not a truth guarantee."]
        elif total_overlap >= 1:
            level = "Medium"
            strength = "partial"
            open_questions = ["Is the available source sufficient for the full claim?"]
            notes = ["Retrieved evidence is relevant but limited in breadth or corroboration."]
        else:
            level = "Low"
            strength = "weak"
            open_questions = ["Does the retrieved material actually support the requested claim?"]
            notes = ["Evidence was retrieved, but little direct request/evidence overlap was found."]

        return ConfidenceAssessment(level, len(normalized), len(sources), conflicts, strength, normalized, open_questions, notes)
