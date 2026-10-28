import json
from pathlib import Path
from automation.api import app, Proposal


def test_agent_connector_never_grants_approval():
    spec = json.loads(Path("connectors/dossier-agent.swagger.json").read_text())
    assert spec["swagger"] == "2.0"
    assert set(spec["paths"]) == {"/requests","/requests/{request_id}"}
    assert spec["securityDefinitions"]["api_key"]["name"] == "X-API-Key"
    assert spec["definitions"]["Proposal"] == Proposal.model_json_schema()
    operations = {route.operation_id for route in app.routes if getattr(route,"operation_id",None)}
    for path in spec["paths"].values():
        for operation in path.values():
            assert operation["operationId"] in operations
