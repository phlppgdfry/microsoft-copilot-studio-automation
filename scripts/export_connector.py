"""Export Swagger 2.0 agent-only connector. Approval credentials never belong here."""
import argparse
import json
from pathlib import Path
from automation.api import Proposal


def document():
    return {
        "swagger":"2.0", "info":{"title":"Synthetic Dossier Assistant", "version":"1.0", "description":"Propose a synthetic dossier task and read status. No approval or execution actions are exposed to the agent."},
        "host":"replace-with-your-api-host.example.invalid", "basePath":"/", "schemes":["https"], "consumes":["application/json"], "produces":["application/json"],
        "securityDefinitions":{"api_key":{"type":"apiKey","in":"header","name":"X-API-Key"}}, "security":[{"api_key":[]}],
        "paths":{
            "/requests":{"post":{"operationId":"ProposeDossierTask", "summary":"Prepare a task for human review", "description":"Only synthetic dossier IDs starting with SYN-. Never promises that the task is executed. Reuse the same idempotency key on retries.", "parameters":[{"name":"proposal","in":"body","required":True,"schema":{"$ref":"#/definitions/Proposal"}}], "responses":{"201":{"description":"Task proposed or original idempotent result","schema":{"$ref":"#/definitions/Task"}},"401":{"description":"Authentication required"},"403":{"description":"Role rejected"},"409":{"description":"Conflicting idempotency payload"},"422":{"description":"Invalid proposal"}}}},
            "/requests/{request_id}":{"get":{"operationId":"GetDossierTask", "summary":"Read task status", "parameters":[{"name":"request_id","in":"path","required":True,"type":"string"}], "responses":{"200":{"description":"Current task state","schema":{"$ref":"#/definitions/Task"}},"401":{"description":"Authentication required"},"404":{"description":"Not found in caller's tenant"}}}}
        },
        "definitions":{
            "Proposal":Proposal.model_json_schema(),
            "Task":{"type":"object","properties":{"id":{"type":"string"},"state":{"type":"string","enum":["pending","approved","rejected","completed"]},"payload":{"type":"object"},"reviewer":{"type":"string","x-nullable":True},"reason":{"type":"string","x-nullable":True},"execution_mode":{"type":"string"}}, "required":["id","state","payload","execution_mode"]}
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = Path("connectors/dossier-agent.swagger.json")
    content = json.dumps(document(),indent=2,sort_keys=True)+"\n"
    if args.check:
        if not path.exists() or path.read_text() != content:
            raise SystemExit("Connector snapshot differs")
    else:
        path.parent.mkdir(exist_ok=True)
        path.write_text(content)


if __name__ == "__main__":
    main()
