# Copilot Studio Dossier Automation

[Current release evaluation](docs/release.md) · [Capability evidence](evidence/release-2026-10-30/FEATURES.md). Local checks are recorded; hosted CI and cloud runtime remain separately unverified.

Een API met een concrete grens tussen **een taak voorstellen**, **menselijk goedkeuren** en **uitvoeren**. De meegeleverde Swagger 2.0-connector laat een Copilot-agent uitsluitend voorstellen en status opvragen. Goedkeuring en uitvoering gebruiken andere rollen en komen niet in het agentgereedschap.

## Portfolio update — 29 October 2026

Added strict approval booleans, safe credential handling, bounded request bodies, safe validation errors and correlated request metadata. A tested packaging command generates parameterized Swagger/API-properties input for `pac connector create`. A real [tenant-exported solution](solution/README.md) now contains the accepted agent-only connector; its reserved example host has no active backend.

[Connector deployment package](docs/connector-deployment.md) · [Current evidence matrix](evidence/FEATURES.md)

**Status:** werkende lokale API, persistente goedkeuringsflow en connectorbestand. De uitvoering maakt één lokale mocktaak aan; ze stuurt geen mail en wijzigt geen Teams, Dataverse, ERP of SharePoint. De connector is contractgetest en als artifact geïmporteerd in een bestaande developmenttenant; de echte solution-export staat in [solution](solution/README.md). Een Microsoft-connection, agentgesprek en backendaanroep zijn niet getest. Het [tenantdraaiboek](docs/tenant-setup.md) beschrijft die accountafhankelijke stappen.

## Lokaal uitvoeren

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pytest -q
.venv/bin/python -m automation.demo
.venv/bin/python scripts/bootstrap.py
.venv/bin/uvicorn automation.api:app --env-file .env --host 127.0.0.1 --port 8085
```

Open `http://127.0.0.1:8085/docs`. Lees de willekeurige keys lokaal uit `.env`; elke key is aan een serverrol en tenant gebonden. Het democommando gebruikt zijn eigen tijdelijke database en toont de volledige flow, inclusief blokkering zonder toestemming en één uitvoering bij herhaalde calls.

## Wat werkt

- Strikte voorstellen voor twee acties: ontbrekende documenten opvragen en review inplannen, uitsluitend `SYN-`-dossiers.
- Persistente idempotency met payloadhash; een gewijzigde payload op dezelfde sleutel geeft 409.
- Rollen `agent/employee`, `reviewer` en `executor` uit serverconfiguratie, plus tenantisolatie.
- Vier-ogencontrole en een definitieve approve/reject-beslissing met reden.
- Atomische lokale taakcreatie en statustransitie; gelijktijdige retries leveren één mocktaak op.
- Audittrail en hervatten via status opvragen na een herstart.
- [Swagger 2.0 voor de agent](connectors/dossier-agent.swagger.json) en [volledige OpenAPI](docs/openapi.json).
- GitHub Actions, dependencylock, Docker en negatieve tests.

## Integreren en leren

- [Architectuur en proces](docs/architecture.md)
- [Copilot Studio en Power Automate instellen](docs/tenant-setup.md)
- [Agentinstructies](copilot/instructions.md)
- [Flowrecept](power-automate/approval-flow.md)
- [Threat model en releasecriteria](docs/security.md)
- [Demo, storingen en oefeningen](docs/learning-runbook.md)
- [Vastgelegde test- en demoresultaten](evidence/README.md)

Een Copilot-conversatie is geen vertrouwde goedkeuringsidentiteit. Ook wanneer de gebruiker in tekst zegt dat iets goedgekeurd is, moet de serverbeslissing via de reviewerrol verlopen. Bewaar de review- en executorcredential nooit in de agentconnector.

## Grenzen

Dit is een integratiereferentie met een werkelijk uit de developmenttenant geëxporteerde unmanaged solution. Die bevat uitsluitend de agentconnector met een gereserveerde voorbeeldhost; geen geconfigureerde connection, agent of flow. Artifactimport is getest, tenant-runtimegedrag niet. Je hebt een bevoegde Microsoft-omgeving, passende licenties, connectorbeleid en een beveiligde HTTPS-host nodig voor een echte proef. Entra JWT-validatie en externe taakuitvoering moeten apart worden geïmplementeerd en getest voordat je echte klantdata gebruikt. Met AI-ondersteuning gemaakt; beheersing moet je zelf aantonen.
