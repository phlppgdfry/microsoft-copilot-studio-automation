# Architectuur

```mermaid
sequenceDiagram
  participant C as Copilot-agent
  participant A as Actie-API
  participant D as SQLite
  participant R as Bevoegde reviewer
  participant W as Executor
  C->>A: Voorstel en idempotency key
  A->>D: Immutable payload + pending + audit
  A-->>C: request_id en pending
  R->>A: Beslissing met reden
  A->>D: approved of rejected + reviewer
  W->>A: Execute request_id
  A->>D: Controle approved; INSERT mocktask + completed
  C->>A: Status opvragen
  A-->>C: Definitieve status, geen belofte vooraf
```

**ADR: een smalle agentconnector.** Swagger bevat alleen `ProposeDossierTask` en `GetDossierTask`. De LLM mag geen betalingsactie of willekeurige URL selecteren. De API valideert het actie-enum en dossierprefix opnieuw; connectorbeschrijvingen zijn op zichzelf geen securitycontrole.

**ADR: server-side goedkeuring.** De reviewer is een apart serverprincipal. De creator kan zichzelf ook met een andere rolkey niet goedkeuren wanneer de subjectnaam gelijk is. Een tenantgrens geeft 404. Dat is nog geen bewijs dat een Power Automate-gebruiker die key terecht gebruikt: tenantidentiteit en roltoekenning moeten door het integratieontwerp worden afgedwongen.

**ADR: lokale transactionele sink.** In deze demo kunnen taakcreatie en statusupdate één SQLite-transactie delen. Bij Dataverse, Graph of ERP kan dat niet. Gebruik dan een outbox, dezelfde request-ID als idempotencykey, een unieke externe sleutel en reconciliation. Zeg bij een timeout nooit dat de externe actie niet plaatsvond zonder dit te controleren.

**Levenscyclus.** `pending` gaat eenmalig naar `approved` of `rejected`; alleen `approved` kan naar `completed`. Dezelfde beslissing van dezelfde reviewer met dezelfde reden mag opnieuw worden aangeboden. Een conflict op een eerdere beslissing geeft 409. Er is geen impliciete reset, wijziging of heropening; een gewijzigd voorstel krijgt een nieuwe sleutel en een nieuwe review.
