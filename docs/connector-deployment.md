# Connector deployment package

The repository now generates the two parameterized input files consumed by `pac connector create`. This is a generated custom connector package, **not** a tenant-exported Power Platform solution. The generated files were accepted by a real development tenant; a separate [actual solution export](../solution/README.md) records that acceptance. The package generator itself still does not export a solution.

```bash
.venv/bin/python scripts/package_connector.py --origin https://your-approved-api.example.com --out build/connector
```

Review `apiDefinition.swagger.json`, `apiProperties.json` and their SHA-256 manifest before any tenant mutation. The generated connector contains only proposal and status operations. Configure only an agent credential in the connection; reviewer and executor identities remain outside Copilot Studio.

With an authorized Power Platform CLI profile selected in a licensed test environment, the administrator can run:

```bash
pac connector create --api-definition-file build/connector/apiDefinition.swagger.json --api-properties-file build/connector/apiProperties.json
```

This command creates a Dataverse connector row. This command was executed against the isolated portfolio solution in the existing development environment with a reserved example backend host; see [tenant evidence](../evidence/tenant-artifact-2026-10-29.json). The example above remains a recipe for your own approved host. Check the selected account/environment before running it. Use the tenant setup guide to configure a connection, DLP classification and a test agent; import success alone does not establish end-to-end behavior. After a real tenant validation, include the connector, flows, connection references and environment variables in a real solution and export it through that environment. Do not manufacture a solution ZIP or claim the flow recipe is importable.

Acceptance record must include environment ID (redacted when sharing), solution/version, connector operation tests, request/run IDs, agent approval denial, independent human decision, executor result, DLP review, failure/retry behavior and cleanup. Tests must use synthetic records. Graph/Dataverse business writes, Entra authentication and Power Automate flow execution remain unimplemented here.

Official CLI reference resolved using Context7 on 29 October 2026: [pac connector](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/connector). Generated properties are locally inspected/contract-tested; Microsoft artifact acceptance is **VERIFIED** for the exported example connector; actual backend/Copilot execution remains **IMPLEMENTED BUT NOT VERIFIED** or unimplemented as stated in the tenant evidence.
