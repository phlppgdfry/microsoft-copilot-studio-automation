import json
import os
import secrets
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from automation.api import app


def main():
    names = ("agent","reviewer","executor")
    keys = {name:secrets.token_urlsafe(32) for name in names}
    profiles = {keys[name]:{"subject":f"synthetic-{name}","tenant":"synthetic-firm","role":name} for name in names}
    with tempfile.TemporaryDirectory() as directory:
        os.environ["AUTOMATION_DB"] = str(Path(directory) / "demo.sqlite3")
        os.environ["AUTOMATION_PRINCIPALS"] = json.dumps(profiles)
        client = TestClient(app)
        proposal = client.post("/requests", headers={"X-API-Key":keys["agent"]},json={"idempotency_key":"synthetic-demo-001","dossier":"SYN-001","action":"request_missing_documents","description":"Vraag de ontbrekende synthetische dossierstukken op."})
        assert proposal.status_code == 201, proposal.text
        task = proposal.json()
        request_id = task["id"]
        blocked = client.post(f"/requests/{request_id}/execute", headers={"X-API-Key":keys["executor"]})
        assert blocked.status_code == 409
        review = client.post(f"/requests/{request_id}/decision",headers={"X-API-Key":keys["reviewer"]},json={"approved":True,"reason":"Synthetische bronnen gecontroleerd"})
        assert review.status_code == 200
        for _ in range(2):
            execution = client.post(f"/requests/{request_id}/execute",headers={"X-API-Key":keys["executor"]})
            assert execution.status_code == 200
        audit = client.get(f"/requests/{request_id}/audit",headers={"X-API-Key":keys["reviewer"]}).json()
        print(json.dumps({"initial":task,"without_approval_http":blocked.status_code,"final":execution.json(),"audit":audit,"external_calls":0},indent=2,ensure_ascii=False))


if __name__ == "__main__":
    main()
