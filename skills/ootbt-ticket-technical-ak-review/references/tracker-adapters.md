# Tracker-Adapter für technische AK-Reviews

Diese Referenz wird nach Auswahl des Ticketsystems geladen. In allen Fällen die Rohantwort als
aktuelle Originalquelle einfrieren, Abrufzeit und Adapter dokumentieren und Secrets entfernen.

## Jira über `acli`

```bash
acli jira workitem view <KEY> --fields '*all' --json
```

Die JSON-Ausgabe unverändert als Rohquelle sichern. Nur den Abschnitt mit technischen bzw.
„Akzeptanzkriterien (Entwicklung)“ extrahieren. `acli` eignet sich zum Lesen, aber strukturierte
ADF-Kommentare sind versionsabhängig nicht zuverlässig; für ADF einen vorhandenen, getesteten
Repo-Adapter oder Jira REST API v3 verwenden. Credentials niemals ausgeben oder in Artefakte
kopieren.

**Ausgabegrenzen:** `--fields '*all'` kann die Capture-Grenze des Tool-Harness überschreiten und
liefert dann syntaktisch unvollständiges JSON. Nicht versuchen, einen head/tail-trunkierten String
zu parsen oder als vollständige Rohquelle auszugeben. Stattdessen die unveränderte CLI-Ausgabe vor
der Capture-Grenze lokal in eine Datei streamen oder bereits in der Pipeline strukturell auf die
benötigten Felder reduzieren. Ist nur ein ADF-Abschnitt eingefroren, dessen exakten Hash als
`AK-Extrakt-Hash` kennzeichnen und offenlegen, dass kein Hash der vollständigen Ticketantwort
vorliegt. Der Abschnitt muss aus den ADF-Nodes ohne Umformulierung entstehen.

## YouTrack über MCP oder REST

1. Zuerst die in der aktuellen Session tatsächlich verfügbaren MCP-Werkzeuge inventarisieren.
2. Passende Issue-Get-/Comment-Operationen anhand ihres Schemas verwenden; keine Toolnamen raten.
3. Fehlt ein passendes MCP-Werkzeug, die konfigurierte YouTrack-Basis-URL und Authentisierung
   feststellen und die offizielle REST API verwenden.
4. Nur notwendige Felder abrufen: ID, Summary, Description, relevante Custom Fields und bei Bedarf
   bestehende Kommentare.

Ohne erreichbaren MCP-/API-Pfad nicht aus Sessionhistorie oder einer kopierten Zusammenfassung so
tun, als sei der aktuelle Ticketstand gelesen worden. Dann Ticketinhalt als `UNBEKANNT` markieren
oder den Nutzer um einen Export bitten.

## GitLab über `glab`

```bash
glab issue view <IID-ODER-URL> --output json --repo <GROUP/PROJECT>
```

Eine Full URL ist vorzuziehen, wenn IID oder Projekt mehrdeutig sind. Kommentare werden erst nach
Freigabe gesetzt:

```bash
glab issue note <IID> --repo <GROUP/PROJECT> --message '<validierter Text>'
```

MR-Beschreibungen oder MR-Diskussionen nur dann als Ticketquelle behandeln, wenn der Nutzer den MR
explizit als Prüfgegenstand nennt.

## Publishing und Readback

Vor jedem Schreibzugriff Vorschau, Payload-Hash, Tracker und Ticket zeigen und eine explizite
Freigabe einholen.

- **Jira:** ADF über getesteten Repo-Adapter oder REST API v3; `acli` nicht blind als
  Formatgarantie behandeln.
- **YouTrack:** vorhandenes MCP-Comment-Tool gemäß Live-Schema, sonst REST API; Antwort-ID/URL
  zurücklesen.
- **GitLab:** `glab issue note`; anschließendes `glab issue view --comments` oder API-Readback.

Nach dem Schreiben Kommentar/Notiz zurücklesen und Marker oder Hash gegen die freigegebene
Payload prüfen. Ohne Readback nicht „publiziert und verifiziert“ behaupten.
