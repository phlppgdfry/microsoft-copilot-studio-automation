# Werkelijk verificatiebewijs

Uitgevoerd op 28 oktober 2026, Python 3.13:

- 6 pytest-tests geslaagd, waaronder rollen, tenants, zelfreview, immutable decisions, payloadconflicten, gelijktijdige retries en de agentconnectorgrens. Zie `tests.xml` en `pytest.txt`.
- Volledige lokale propose → blocked execute → approve → execute → retry-demo; zie `demo.json`. Geen externe calls.
- Dependencycontrole geslaagd; zie `dependencies.txt`.
- Docker-image gebouwd, verpakte API getest en standaard Uvicorn-CMD geïsoleerd gestart; `/health` gaf 200. Zie `container-smoke.txt` en `container-runtime.txt`.
- Swagger/OpenAPI uit de echte modellen/routecontracten geëxporteerd en gecontroleerd.

Geen Microsoft-tenant, connectorimport, Teams-bericht of Dataverse-write is uitgevoerd. Eén upstream TestClient-deprecationwarning is zichtbaar. Een contracttest is geen tenantacceptatietest. Remote CI-resultaten worden afzonderlijk door GitHub Actions vastgelegd.
