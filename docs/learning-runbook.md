# Demonstreren, leren en beheren

## Twee minuten

0:00: leg het fictieve dossier en de twee toegestane acties uit. 0:20: draai `python -m automation.demo`. 0:45: toon 409 voor uitvoering zonder approval. 1:00: toon afzonderlijke reviewer en complete-state. 1:20: toon dat twee execute-calls maar één auditevent voor taakcreatie opleveren. 1:40: open de Swagger en wijs aan dat de agent alleen propose/get krijgt. Sluit af met wat nog een tenanttest vereist.

## Begrippen en oefeningen

Een **connector** beschrijft en beveiligt API-acties voor een platform; hij maakt de server niet vanzelf betrouwbaar. Een **connection** bindt credentials in een omgeving. Een **solution** bundelt componenten voor transport en ALM. Een **environment variable** draagt omgevingsafhankelijke configuratie; geen excuus om secrets in Git te bewaren. **Human-in-the-loop** heeft betekenis wanneer de beslisser bevoegd is en de software het akkoord daadwerkelijk afdwingt.

1. Leg zonder AI uit waarom 'de gebruiker zei akkoord' geen serverbeslissing is.
2. Voeg zelf een derde veilige mockactie toe, inclusief servervalidatie, connectorexport en twee negatieve tests. Behoud de goedkeuringsgrens.
3. Diagnoseer een 409 bij een retry: vergelijk request-ID, idempotencykey, payload en status zonder secrets te loggen.
4. Ontwerp een Dataverse-sink met een unieke externe request-ID. Leg uit hoe je na een timeout vaststelt of de taak bestaat.
5. Maak een afwijzingspad in je tenant en toon de run-ID. Een screenshot van de floweditor bewijst niet dat het pad werkt.

## Runbook

Bij 401 controleer je lokaal de connection en keyconfiguratie. Bij 403 controleer je de serverrol. Bij 404 controleer je tenant en request-ID. Bij 409 lees je eerst status en audit. Heropen een afwijzing nooit door databasevelden handmatig te wijzigen. Maak bij gewijzigd werk een nieuw traceerbaar voorstel.

Stop writes voor een consistente databasebackup of gebruik SQLite backup-API. Test een restore in een andere map met `AUTOMATION_DB`. Rollback van een solution maakt reeds uitgevoerde acties niet ongedaan: beoordeel bestaande taken afzonderlijk.

Voor rollout: één proces, twee getrainde reviewers, maximaal tien synthetische proefgevallen. Meet correct taaktype, onterechte taakvoorstellen, doorlooptijd tot menselijke beslissing, afwijzingen en dubbele taken. De beoogde dubbele-taakratio is nul; er is geen gemeten productiebaseline.
