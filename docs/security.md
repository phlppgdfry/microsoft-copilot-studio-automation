# Threat model en pilotcriteria

| Risico | Implementatie | Nog nodig voor echte uitrol |
|---|---|---|
| Agent keurt eigen voorstel goed | Agentconnector heeft geen review/execute; serverrollen | Gevalideerde gebruikersidentiteit en correcte toekenning |
| Dubbele taak bij retries | Unieke tenant/idempotencykey, digest, transactionele mocktask | Idempotency en reconciliation in externe sink |
| Andere tenant lezen | Alle objectreads met tenant uit serverconfiguratie | Identity gateway en tenantconfiguratie-audit |
| Betaling via prompt injection | Gesloten actie-enum, geen betaalroute | Permanente evaluaties op werkelijke agentconfiguratie |
| Manipulatie na akkoord | Geen wijzigroute; beslissing immutabel | Beheerbeleid voor superseding/reopening |
| Key uitlekken | `.env` genegeerd, bootstrap genereert willekeurige keys | Vault/managed identity, rotatie en netwerkbeperking |

De dossierprefix `SYN-` helpt de demo begrenzen maar is geen persoonsgegevensdetectie. Een beschrijving kan nog steeds ongewenste tekst bevatten. Gebruik in deze versie uitsluitend verzonnen inhoud. Er is geen automatische retentie, auditimmutabiliteit, PII-redactie, JWT-validatie of algemeen compliancebewijs.

Pilotacceptatie: bevoegde eigenaar, gedocumenteerde data-/privacybeoordeling, minimaal drie verschillende rollen, alle negatieve tests groen, aparte connectorconnections, bewezen reject/timeoutpad, gecontroleerde solutionexport en herstelplan. Stop bij een toegangslek, onbedoelde externe actie of een audit die niet aan de echte reviewer te koppelen is.
