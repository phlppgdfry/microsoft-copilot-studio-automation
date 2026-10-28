import hashlib
import hmac
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Copilot Approval Boundary", version="0.1.0")
key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def principal(key: str | None = Depends(key_header)):
    for secret, profile in json.loads(os.getenv("AUTOMATION_PRINCIPALS", "{}")).items():
        if key and hmac.compare_digest(key, secret):
            return profile
    raise HTTPException(401, "Invalid API key")


@contextmanager
def database():
    path = Path(os.getenv("AUTOMATION_DB", "data/automation.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
          id TEXT PRIMARY KEY, tenant TEXT, creator TEXT, idem TEXT, digest TEXT,
          payload TEXT, state TEXT, reviewer TEXT, reason TEXT,
          UNIQUE(tenant, idem));
        CREATE TABLE IF NOT EXISTS mock_tasks (
          request_id TEXT PRIMARY KEY, tenant TEXT, payload TEXT);
        CREATE TABLE IF NOT EXISTS audit (
          seq INTEGER PRIMARY KEY, request_id TEXT, actor TEXT, action TEXT,
          created TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def require(profile, roles):
    if profile.get("role") not in roles:
        raise HTTPException(403, "Insufficient role")


def get_row(db, request_id, profile):
    row = db.execute("SELECT * FROM requests WHERE id=? AND tenant=?", (request_id, profile["tenant"])).fetchone()
    if row is None:
        raise HTTPException(404, "Request not found")
    return row


def result(row):
    return {"id": row["id"], "state": row["state"], "payload": json.loads(row["payload"]), "reviewer": row["reviewer"], "reason": row["reason"], "execution_mode": "mock-local-task"}


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idempotency_key: str = Field(min_length=8, max_length=100)
    dossier: str = Field(pattern=r"^SYN-[A-Z0-9-]{1,40}$")
    action: str = Field(pattern=r"^(request_missing_documents|schedule_review)$")
    description: str = Field(min_length=10, max_length=1000)


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approved: bool
    reason: str = Field(min_length=5, max_length=500)


@app.get("/health")
def health():
    return {"status": "ok", "execution_mode": "mock-local-task"}


@app.post("/requests", status_code=201, operation_id="ProposeDossierTask")
def propose(body: Proposal, user=Depends(principal)):
    require(user, {"agent", "employee"})
    payload = body.model_dump(exclude={"idempotency_key"})
    canonical = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM requests WHERE tenant=? AND idem=?", (user["tenant"], body.idempotency_key)).fetchone()
        if row:
            if row["digest"] != digest:
                raise HTTPException(409, "Idempotency key reused with different payload")
            return result(row)
        request_id = str(uuid4())
        db.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?)", (request_id, user["tenant"], user["subject"], body.idempotency_key, digest, canonical, "pending", None, None))
        db.execute("INSERT INTO audit(request_id,actor,action) VALUES (?,?,?)", (request_id, user["subject"], "proposed"))
        return result(get_row(db, request_id, user))


@app.get("/requests/{request_id}", operation_id="GetDossierTask")
def get_request(request_id: str, user=Depends(principal)):
    require(user, {"agent", "employee", "reviewer", "executor"})
    with database() as db:
        return result(get_row(db, request_id, user))


@app.post("/requests/{request_id}/decision", operation_id="ReviewDossierTask")
def decide(request_id: str, body: Decision, user=Depends(principal)):
    require(user, {"reviewer"})
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = get_row(db, request_id, user)
        if row["creator"] == user["subject"]:
            raise HTTPException(403, "Four-eyes review requires another person")
        state = "approved" if body.approved else "rejected"
        if row["state"] != "pending":
            if row["state"] == state and row["reviewer"] == user["subject"] and row["reason"] == body.reason:
                return result(row)
            raise HTTPException(409, "Decision is immutable")
        db.execute("UPDATE requests SET state=?,reviewer=?,reason=? WHERE id=?", (state, user["subject"], body.reason, request_id))
        db.execute("INSERT INTO audit(request_id,actor,action) VALUES (?,?,?)", (request_id, user["subject"], state))
        return result(get_row(db, request_id, user))


@app.post("/requests/{request_id}/execute", operation_id="ExecuteApprovedDossierTask")
def execute(request_id: str, user=Depends(principal)):
    require(user, {"executor"})
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = get_row(db, request_id, user)
        if row["state"] == "completed":
            return result(row)
        if row["state"] != "approved":
            raise HTTPException(409, "Human approval required")
        # Atomic local sink + state transition. External sinks require their own idempotency contract.
        db.execute("INSERT INTO mock_tasks VALUES (?,?,?)", (request_id, user["tenant"], row["payload"]))
        db.execute("UPDATE requests SET state='completed' WHERE id=?", (request_id,))
        db.execute("INSERT INTO audit(request_id,actor,action) VALUES (?,?,?)", (request_id, user["subject"], "mock-task-created"))
        return result(get_row(db, request_id, user))


@app.get("/requests/{request_id}/audit", operation_id="GetDossierTaskAudit")
def audit(request_id: str, user=Depends(principal)):
    require(user, {"reviewer"})
    with database() as db:
        get_row(db, request_id, user)
        return [dict(row) for row in db.execute("SELECT seq,actor,action,created FROM audit WHERE request_id=? ORDER BY seq", (request_id,))]
