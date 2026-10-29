# Current verification — 29 October 2026

A separate unmanaged solution and agent connector were accepted in the existing development tenant and exported through PAC. See [solution artifact](../solution/README.md). The reserved example host has no backend/connection, so the conversational, flow and HTTP acceptance steps below remain unverified.

# Microsoft-tenantproef

Dit is een uitvoerbaar integratierecept; de tenantstappen zijn nog niet in een echte omgeving bevestigd. Gebruik uitsluitend een testomgeving en synthetische dossiers. Controleer actuele licenties, connectorbeschikbaarheid en beleid met de tenantbeheerder.

## API en connector

1. Start de lokale tests en demo. Host daarna dezelfde API op een goedgekeurde HTTPS-origin achter een gateway met passende netwerk-, identity- en requestlimieten. Een Copilot-cloudservice kan niet rechtstreeks naar jouw `localhost`.
2. Kopieer `connectors/dossier-agent.swagger.json` naar een tijdelijk bestand. Vervang `host` door de bevoegde HTTPS-host zonder `https://`. Houd dit bestand en eventuele connectionconfiguratie in de testomgeving; keys gaan nooit in het specbestand.
3. Maak in een afzonderlijke Power Platform-solution een custom connector en importeer de Swagger 2.0 JSON. Controleer operation-ID's, headernaam `X-API-Key`, de twee requestroutes en het ontbreken van approval/execute.
4. Configureer voor deze beperkte proef API-keyauthenticatie met de **agentrol**. Een gedeelde key betekent een gedeeld serviceprincipal: die geeft geen afzonderlijke gebruikersidentiteit door. Kies voor productie een gevalideerd Entra/OAuth-ontwerp en pas de server aan; deze API implementeert die JWT-validatie nog niet.
5. Test de connector met een `SYN-001`-voorstel. Herhaal dezelfde sleutel en dezelfde payload; de request-ID moet gelijk blijven. Wijzig de payload; verwacht 409. Controleer tenantisolatie via de rechtstreekse API-tests.

## Copilot Studio

6. Maak een testagent in dezelfde bevoegde omgeving. Voeg de twee connectoracties toe. Gebruik `copilot/instructions.md` als startinstructies en geef actieparameters expliciete beschrijvingen.
7. Vraag ontbrekende synthetische dossierstukken op. De agent moet een voorstel terugmelden en zeggen dat beoordeling nog nodig is. Als parameters ontbreken, moet hij doorvragen; hij mag geen goedkeuring verzinnen.
8. Maak de afzonderlijke approval-flow volgens `power-automate/approval-flow.md`. Voeg review- en execute-routes **niet** als agenttool toe.
9. Test approve, reject, timeout, herhaalde trigger en verkeerde tenant. Controleer audit en lokale mocktaak; Teams, SharePoint en Dataverse blijven in deze versie ongewijzigd.
10. Publiceer pas na een beoordeelde pilot. Exporteer daarna de werkelijke unmanaged solution uit jouw testomgeving voor versiebeheer, met connection references en environment variables; verwijder secrets en controleer de export. Leg solutionversie, omgeving, testdatum en bekende beperkingen vast.

## Acceptatiebewijs

Bewaar een geanonimiseerde opname, connector-testresultaten, flow-run-ID's, negatieve testcases, solutionmanifest en reviewerakkoord. Zonder deze stukken staat de status op **lokaal connectorcontract getest**, niet op **Microsoft-tenantintegratie bewezen**.

Bronnen, via Context7 gecontroleerd op 28 oktober 2026:

- [REST API tools en OpenAPI v2](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api)
- [Custom connector met Entra on-behalf-of](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-custom-connector-on-behalf-of)

REST API-toolimport is in de geraadpleegde documentatie als preview beschreven. Gebruik deze mogelijkheid alleen wanneer je tenantbeleid die toestaat; het custom-connectorpad blijft een afzonderlijk te testen integratiekeuze.
