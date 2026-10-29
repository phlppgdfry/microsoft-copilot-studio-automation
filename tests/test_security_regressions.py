from fastapi.testclient import TestClient
from automation.api import app


def test_non_ascii_credential_fails_closed(monkeypatch):
    monkeypatch.setenv('AUTOMATION_PRINCIPALS', '{"valid-key":{"subject":"a","tenant":"a","role":"agent"}}')
    assert TestClient(app).get('/requests/missing', headers={'X-API-Key': b'\xc3\xa9-invalid'}).status_code == 401
