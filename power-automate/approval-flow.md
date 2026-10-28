# Flowrecept: apart menselijk akkoord

Dit document is geen importeerbare Power Automate-export. Bouw het in je eigen testsolution en bewaar pas na testen een echte export. Er is geen tenant-run uitgevoerd.

| Stap | Concrete configuratie en controle |
|---|---|
| Trigger | Een geautoriseerde medewerker start de testflow met een bestaande request-ID; geen anonieme publieke webhook |
| Status lezen | Gebruik de agent/read-connection; alleen `pending` mag naar review |
| Approval starten | Gebruik de tenantfunctie voor approvals; routeer naar een expliciet bevoegde groep, nooit naar een door het model gekozen e-mailadres |
| Menselijke taak | Toon dossier, actie, ongewijzigde beschrijving en request-ID; informeer dat deze versie alleen een lokale mocktaak maakt |
| Responder controleren | Controleer dat het antwoord van de toegewezen reviewer komt en dat die verschilt van de indiener; servicekeys vormen op zichzelf geen gebruikersbewijs |
| Beslissing registreren | De afzonderlijke reviewerconnection roept `POST /requests/{id}/decision` aan met approved en reason |
| Uitvoeren | Alleen na geslaagde servergoedkeuring roept een afzonderlijke executorconnection de execute-route aan |
| Retry | Hergebruik request-ID; een voltooide execute mag veilig herhaald worden. Een 409 is een te onderzoeken stateconflict |
| Timeout/weigering | Voer niets uit. Toon pending of registreer een expliciete afwijzing door de bevoegde rol |
| Rapportage | Bewaar flow-run-ID, request-ID en foutcode; log geen volledige dossierinhoud of credentials |

De API bewaart als reviewer de serveridentity achter de key, niet automatisch de menselijke Entra-gebruiker. Voor echte persoonsgebonden audit implementeer je geverifieerde delegated identity of een gecontroleerde broker die claims valideert, actorbinding afdwingt en audit vastlegt. Een model mag deze actorinformatie niet aanleveren.

Test twee gelijktijdige flowtriggers, een afwijzing, een verlopen approval, een 401 en een timeout na execute. Controleer dat één lokale taak bestaat. Een externe sink vereist extra tests op zijn eigen idempotency- en reconciliatiegedrag.
