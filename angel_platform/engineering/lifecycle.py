from __future__ import annotations
from .store import EngineeringStore

class KnowledgeEngineeringLifecycle:
    """Thin orchestration layer implementing the canonical Angel 4.1 record flow."""

    def __init__(self, store: EngineeringStore | None = None):
        self.store = store or EngineeringStore()

    def record_rag_run(self, question, project_context=None, retrieval_config=None,
                       index_fingerprint=None):
        return self.store.create_rag_run(
            question,
            project_context,
            retrieval_config or {},
            index_fingerprint,
        )

    def evaluate(self, rag_run_id, result, evaluation_set_id=None):
        return self.store.create_evaluation(rag_run_id, evaluation_set_id, result)

    def record_evidence(self, rag_run_id, evidence, evaluation_id=None):
        return self.store.create_evidence(rag_run_id, evaluation_id, evidence)

    def measure(self, metric, value, status, evidence_ids, evaluation_id=None,
                numerator=None, denominator=None, calculation_version="1"):
        return self.store.create_measurement(
            evaluation_id, metric, value, status, numerator, denominator,
            calculation_version, evidence_ids
        )

    def snapshot(self, health, evidence_summary, index_fingerprint=None,
                 evaluation_set_version=None):
        return self.store.create_snapshot(
            index_fingerprint, evaluation_set_version, health, evidence_summary
        )

    def recommend(self, problem, recommendation, evidence_ids):
        if not evidence_ids:
            raise ValueError("Recommendation requires supporting evidence.")
        return self.store.create_recommendation(problem, recommendation, evidence_ids)

    def authorize_change(self, project_id, items):
        return self.store.create_knowledge_change(project_id, items)

    def build_index(self, change_set_id=None, source_fingerprint=None,
                    target_fingerprint=None):
        return self.store.create_index_build(
            change_set_id, source_fingerprint, target_fingerprint
        )
