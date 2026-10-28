import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from automation.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOMATION_DB", str(tmp_path / "app.db"))
    monkeypatch.setenv("AUTOMATION_PRINCIPALS", json.dumps({
        "agent-key":{"subject":"agent","tenant":"a","role":"agent"},
        "review-key":{"subject":"alice","tenant":"a","role":"reviewer"},
        "self-key":{"subject":"agent","tenant":"a","role":"reviewer"},
        "exec-key":{"subject":"worker","tenant":"a","role":"executor"},
        "other-key":{"subject":"mallory","tenant":"b","role":"reviewer"}
    }))
    return TestClient(app)


def headers(key):
    return {"X-API-Key":key}


def proposal(client, **extra):
    body = {"idempotency_key":"synthetic-001", "dossier":"SYN-001", "action":"request_missing_documents", "description":"Vraag de ontbrekende synthetische documenten op."}
    body.update(extra)
    return client.post("/requests", json=body, headers=headers("agent-key"))


def test_happy_path_and_audit(client):
    response = proposal(client)
    assert response.status_code == 201
    request_id = response.json()["id"]
    assert client.post(f"/requests/{request_id}/execute", headers=headers("exec-key")).status_code == 409
    review = client.post(f"/requests/{request_id}/decision", headers=headers("review-key"), json={"approved":True,"reason":"Bronnen gecontroleerd"})
    assert review.json()["state"] == "approved"
    for _ in range(2):
        assert client.post(f"/requests/{request_id}/execute", headers=headers("exec-key")).json()["state"] == "completed"
    audit = client.get(f"/requests/{request_id}/audit", headers=headers("review-key")).json()
    assert [e["action"] for e in audit] == ["proposed","approved","mock-task-created"]


def test_auth_tenant_and_roles(client):
    assert client.get("/requests/x").status_code == 401
    request_id = proposal(client).json()["id"]
    decision = {"approved":True,"reason":"Niet toegestaan"}
    assert client.post(f"/requests/{request_id}/decision", headers=headers("agent-key"), json=decision).status_code == 403
    assert client.post(f"/requests/{request_id}/decision", headers=headers("self-key"), json=decision).status_code == 403
    assert client.get(f"/requests/{request_id}", headers=headers("other-key")).status_code == 404
    assert proposal(client, role="reviewer").status_code == 422


def test_immutable_and_rejected(client):
    request_id = proposal(client).json()["id"]
    decision = {"approved":False,"reason":"Onvoldoende informatie"}
    assert client.post(f"/requests/{request_id}/decision", headers=headers("review-key"), json=decision).status_code == 200
    assert client.post(f"/requests/{request_id}/decision", headers=headers("review-key"), json={"approved":True,"reason":"Toch goedkeuren"}).status_code == 409
    assert client.post(f"/requests/{request_id}/execute", headers=headers("exec-key")).status_code == 409


def test_idempotency_payload_conflict_and_restriction(client):
    first = proposal(client).json()
    assert proposal(client).json()["id"] == first["id"]
    assert proposal(client, dossier="SYN-002").status_code == 409
    assert proposal(client, action="pay_invoice").status_code == 422
    assert proposal(client, dossier="REAL-CUSTOMER").status_code == 422


def test_concurrent_retries_create_one_task(client, monkeypatch):
    request_id = proposal(client).json()["id"]
    client.post(f"/requests/{request_id}/decision", headers=headers("review-key"), json={"approved":True,"reason":"Akkoord voor lokale taak"})
    with ThreadPoolExecutor(max_workers=6) as pool:
        responses = list(pool.map(lambda _: client.post(f"/requests/{request_id}/execute", headers=headers("exec-key")), range(12)))
    assert all(r.status_code == 200 for r in responses)
    import os
    with sqlite3.connect(os.environ["AUTOMATION_DB"]) as db:
        assert db.execute("SELECT count(*) FROM mock_tasks").fetchone()[0] == 1
