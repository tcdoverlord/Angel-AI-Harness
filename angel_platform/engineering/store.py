from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA = Path.home() / "Angel_Platform"
DB = DATA / "angel_intelligence.sqlite3"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

class EngineeringStore:
    """Append-oriented local store for Angel 4.1 engineering records.

    Historical records are never overwritten by lifecycle operations.
    This is intentionally additive so the existing Angel persistence remains
    the source of truth for conversations and the 4.1 layer can observe it.
    """

    def __init__(self, path: Path | str = DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init()

    def _connect(self):
        c = sqlite3.connect(self.path, timeout=15, check_same_thread=False)
        c.row_factory = sqlite3.Row
        return c

    def _init(self):
        schema = """
        CREATE TABLE IF NOT EXISTS angel41_rag_runs (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            project_context_json TEXT,
            retrieval_config_json TEXT NOT NULL,
            index_fingerprint TEXT,
            status TEXT NOT NULL,
            answer_json TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS angel41_evaluations (
            id TEXT PRIMARY KEY,
            rag_run_id TEXT NOT NULL,
            evaluation_set_id TEXT,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angel41_evidence (
            id TEXT PRIMARY KEY,
            evaluation_id TEXT,
            rag_run_id TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angel41_measurements (
            id TEXT PRIMARY KEY,
            evaluation_id TEXT,
            metric TEXT NOT NULL,
            value REAL,
            status TEXT NOT NULL,
            numerator REAL,
            denominator REAL,
            calculation_version TEXT,
            evidence_ids_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angel41_snapshots (
            id TEXT PRIMARY KEY,
            index_fingerprint TEXT,
            evaluation_set_version TEXT,
            health_json TEXT NOT NULL,
            evidence_summary_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angel41_recommendations (
            id TEXT PRIMARY KEY,
            problem TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            evidence_ids_json TEXT NOT NULL,
            status TEXT NOT NULL,
            decision_json TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS angel41_knowledge_changes (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            items_json TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS angel41_index_builds (
            id TEXT PRIMARY KEY,
            change_set_id TEXT,
            source_fingerprint TEXT,
            target_fingerprint TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS angel41_operations (
            id TEXT PRIMARY KEY,
            operation TEXT NOT NULL,
            status TEXT NOT NULL,
            resource_id TEXT,
            detail_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock, self._connect() as c:
            c.executescript(schema)

    def create_rag_run(self, question: str, project_context: dict | None,
                       retrieval_config: dict, index_fingerprint: str | None) -> dict:
        rid = new_id("rag")
        record = {
            "id": rid, "question": question,
            "project_context": project_context,
            "retrieval_config": retrieval_config,
            "index_fingerprint": index_fingerprint,
            "status": "completed",
            "answer": None, "created_at": now(), "completed_at": now()
        }
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_rag_runs
                (id,question,project_context_json,retrieval_config_json,index_fingerprint,status,answer_json,created_at,completed_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (rid, question, json.dumps(project_context), json.dumps(retrieval_config),
                 index_fingerprint, "completed", None, record["created_at"], record["completed_at"]))
        return record

    def update_rag_run_answer(self, rid: str, answer: str) -> dict | None:
        with self._lock, self._connect() as c:
            c.execute("UPDATE angel41_rag_runs SET answer_json=?, status=?, completed_at=? WHERE id=?", (json.dumps(answer, ensure_ascii=False), "completed", now(), rid))
        return self.get_rag_run(rid)

    def list_evidence(self, rag_run_id: str) -> list[dict]:
        with self._lock, self._connect() as c:
            rows=c.execute("SELECT * FROM angel41_evidence WHERE rag_run_id=? ORDER BY created_at", (rag_run_id,)).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item["evidence"]=json.loads(item.pop("evidence_json") or "{}")
            out.append(item)
        return out

    def list_evaluations(self, rag_run_id: str) -> list[dict]:
        with self._lock, self._connect() as c:
            rows=c.execute("SELECT * FROM angel41_evaluations WHERE rag_run_id=? ORDER BY created_at DESC", (rag_run_id,)).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item["result"]=json.loads(item.pop("result_json") or "{}")
            out.append(item)
        return out

    def list_measurements(self, evaluation_id: str | None = None, rag_run_id: str | None = None) -> list[dict]:
        sql="SELECT m.* FROM angel41_measurements m"; params=[]
        if rag_run_id:
            sql += " JOIN angel41_evaluations e ON e.id=m.evaluation_id WHERE e.rag_run_id=?"; params.append(rag_run_id)
        elif evaluation_id:
            sql += " WHERE m.evaluation_id=?"; params.append(evaluation_id)
        else:
            sql += " WHERE 1=0"
        sql += " ORDER BY m.created_at DESC"
        with self._lock, self._connect() as c: rows=c.execute(sql, params).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item["evidence_ids"]=json.loads(item.pop("evidence_ids_json") or "[]"); out.append(item)
        return out

    def get_rag_run(self, rid: str) -> dict | None:
        with self._lock, self._connect() as c:
            r = c.execute("SELECT * FROM angel41_rag_runs WHERE id=?", (rid,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["project_context"] = json.loads(d.pop("project_context_json") or "null")
        d["retrieval_config"] = json.loads(d.pop("retrieval_config_json") or "{}")
        d["answer"] = json.loads(d.pop("answer_json") or "null")
        return d

    def list_rag_runs(self, limit=100) -> list[dict]:
        with self._lock, self._connect() as c:
            rows = c.execute(
                "SELECT id FROM angel41_rag_runs ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 500)),)
            ).fetchall()
        return [self.get_rag_run(r["id"]) for r in rows]

    def create_evaluation(self, rag_run_id: str, evaluation_set_id: str | None, result: dict) -> dict:
        eid = new_id("eval")
        record = {"id": eid, "rag_run_id": rag_run_id, "evaluation_set_id": evaluation_set_id,
                  "result": result, "created_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_evaluations
                (id,rag_run_id,evaluation_set_id,result_json,created_at) VALUES (?,?,?,?,?)""",
                (eid, rag_run_id, evaluation_set_id, json.dumps(result), record["created_at"]))
        return record

    def create_evidence(self, rag_run_id: str, evaluation_id: str | None, evidence: dict) -> dict:
        xid = new_id("evidence")
        record = {"id": xid, "rag_run_id": rag_run_id, "evaluation_id": evaluation_id,
                  "evidence": evidence, "created_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_evidence
                (id,evaluation_id,rag_run_id,evidence_json,created_at) VALUES (?,?,?,?,?)""",
                (xid, evaluation_id, rag_run_id, json.dumps(evidence), record["created_at"]))
        return record

    def create_measurement(self, evaluation_id: str | None, metric: str, value: float | None,
                           status: str, numerator: float | None, denominator: float | None,
                           calculation_version: str, evidence_ids: list[str]) -> dict:
        mid = new_id("measurement")
        record = {"id": mid, "evaluation_id": evaluation_id, "metric": metric, "value": value,
                  "status": status, "numerator": numerator, "denominator": denominator,
                  "calculation_version": calculation_version, "evidence_ids": evidence_ids,
                  "created_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_measurements
                (id,evaluation_id,metric,value,status,numerator,denominator,calculation_version,evidence_ids_json,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (mid, evaluation_id, metric, value, status, numerator, denominator,
                 calculation_version, json.dumps(evidence_ids), record["created_at"]))
        return record

    def create_snapshot(self, index_fingerprint: str | None, evaluation_set_version: str | None,
                        health: dict, evidence_summary: dict) -> dict:
        sid = new_id("snapshot")
        record = {"id": sid, "index_fingerprint": index_fingerprint,
                  "evaluation_set_version": evaluation_set_version, "health": health,
                  "evidence_summary": evidence_summary, "created_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_snapshots
                (id,index_fingerprint,evaluation_set_version,health_json,evidence_summary_json,created_at)
                VALUES (?,?,?,?,?,?)""",
                (sid, index_fingerprint, evaluation_set_version, json.dumps(health),
                 json.dumps(evidence_summary), record["created_at"]))
        return record

    def create_recommendation(self, problem: str, recommendation: str,
                              evidence_ids: list[str]) -> dict:
        rid = new_id("recommendation")
        record = {"id": rid, "problem": problem, "recommendation": recommendation,
                  "evidence_ids": evidence_ids, "status": "proposed",
                  "decision": None, "created_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_recommendations
                (id,problem,recommendation,evidence_ids_json,status,decision_json,created_at)
                VALUES (?,?,?,?,?,?,?)""",
                (rid, problem, recommendation, json.dumps(evidence_ids), "proposed",
                 None, record["created_at"]))
        return record

    def create_knowledge_change(self, project_id: str | None, items: list[dict]) -> dict:
        cid = new_id("change")
        record = {"id": cid, "project_id": project_id, "items": items,
                  "status": "proposed", "created_at": now(), "completed_at": None}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_knowledge_changes
                (id,project_id,items_json,status,created_at,completed_at)
                VALUES (?,?,?,?,?,?)""",
                (cid, project_id, json.dumps(items), "proposed", record["created_at"], None))
        return record

    def create_index_build(self, change_set_id: str | None, source_fingerprint: str | None,
                           target_fingerprint: str | None) -> dict:
        iid = new_id("index")
        record = {"id": iid, "change_set_id": change_set_id,
                  "source_fingerprint": source_fingerprint,
                  "target_fingerprint": target_fingerprint,
                  "status": "completed", "created_at": now(), "completed_at": now()}
        with self._lock, self._connect() as c:
            c.execute("""INSERT INTO angel41_index_builds
                (id,change_set_id,source_fingerprint,target_fingerprint,status,created_at,completed_at)
                VALUES (?,?,?,?,?,?,?)""",
                (iid, change_set_id, source_fingerprint, target_fingerprint,
                 "completed", record["created_at"], record["completed_at"]))
        return record
