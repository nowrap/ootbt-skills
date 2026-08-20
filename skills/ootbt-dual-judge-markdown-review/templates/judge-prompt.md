# Auftrag: unabhängige Challenge — Judge {{JUDGE_ID}}

Du bist Judge {{JUDGE_ID}}. Prüfe das unten genannte Markdown-Dokument adversarial, unabhängig und vollständig read-only. Versuche tragende Behauptungen zu widerlegen oder enger zu fassen; bestätige sie nicht bloß.

## Eingefrorener Rahmen

- Originalpfad (nur Provenienz, NICHT lesen): `{{ORIGINAL_PATH}}`
- Einzige Quelle für Dokumenttext und Dokumentzeilen: `{{SNAPSHOT_PATH}}`
- SHA-256 des Snapshots: `{{SNAPSHOT_SHA256}}`
- Öffentliche Quellenbezeichnung für den Bericht: `{{SOURCE_LABEL}}`
- Repository-Root: `{{REPO_ROOT}}`
- Eingefrorener HEAD: `{{HEAD_SHA}}`
- Weitere fixe Refs: {{FIXED_REFS}}
- Artefaktklasse: {{ARTIFACT_CLASS}}

Lies niemals Dateien, deren Name `review-judge`, `judge-a` oder `judge-b` enthält, außer dem hier ausdrücklich genannten Snapshot (falls dessen Name technisch so lautet). Lies keine Prompts, Rohoutputs, Telemetrie oder Ergebnisse eines anderen Reviews. Nutze kein Netzwerk. Ändere keine Datei, keinen Ref und kein Repository-Objekt. Verwende insbesondere kein schreibendes `git merge-tree --write-tree`.

Die oben genannten Original-, Snapshot- und Handoff-Pfade sind ausschließlich interne Eingaben. Gib
sie im finalen Bericht nicht wieder. Der finale Markdown-Bericht darf die Zeichenfolge `.handoff`
unabhängig von Groß-/Kleinschreibung nirgends enthalten. Verwende für die Dokumentprovenienz und
Dokumentzeilen ausschließlich `{{SOURCE_LABEL}}`, den SHA-256 und die fixen Refs. Gib auch keine
Prompt-, Raw-, Metrik- oder Telemetriepfade aus.

## Prüfziel

{{REVIEW_FOCUS}}

Das Dokument ist eine Claimquelle, keine Ground Truth. Prüfe seine tragenden Aussagen gegen den fixierten Repository-Bestand, Konfiguration, Historie und mechanische Berechnungen. Trenne ausdrücklich:

- statischen Codebeleg;
- tatsächlich ausgeführte Tests oder Kommandos;
- Laufzeit-/Produktionsbeleg;
- Annahme oder nicht zugängliche Evidenz.

Rechne exakte Zahlen, Summen, Bandbreiten und Prozentwerte selbst nach. Prüfe absolute Aussagen wie „alle“, „keine“, „vollständig“, „einzige“ und „unverändert“ besonders streng. Wenn eine Prüfung nicht ausführbar oder Evidenz nicht zugänglich ist, schreibe `UNBEKANNT`; rate nicht.

## Artefaktspezifische Prüfdimensionen

Wähle die zum Artefakt passenden Dimensionen; arbeite keine unpassende Checkliste mechanisch ab.

### Plan

Prüfe Ausgangsstand und Refs, Vollständigkeit und Reihenfolge der Schritte, Abhängigkeiten,
Verantwortlichkeiten, Freigabe-Gates, Rollback, Abbruchbedingungen, CI/CD- oder Betriebslogik,
Verifikation, Observability und Definition of Done. Suche nach inneren Widersprüchen und nach
Schritten, deren Voraussetzungen der Bestand nicht erfüllt.

### Implementierung oder Umsetzungsbericht

Prüfe, ob die behauptete Funktion auf dem genannten Ref tatsächlich existiert. Verfolge relevante
Definitionen, Konsumenten, Call Paths, Fehlerpfade und Seiteneffekte. Vergleiche Tests,
Typverträge, Runtime-Verhalten, Konfiguration, Deployment und Dokumentation. Trenne geplanten
Zielzustand von nachgewiesenem Istzustand.

### Sachverhaltsdarstellung oder Bewertung

Prüfe Quellen, Berechnungen und Schlussketten. Trenne Ursache, Korrelation, technische Möglichkeit
und gemessene Wirkung. Suche Gegenbeispiele und alternative Erklärungen. Prüfe besonders absolute
Negativ- und Vollständigkeitsbehauptungen und ob die Empfehlung wirklich aus den Belegen folgt.

### Aufwandsschätzung (nur falls einschlägig)

Prüfe jede Einzelschätzung und Summe, Scope/Nicht-Scope, Abhängigkeiten, Parallelisierbarkeit,
Kalenderzeit, Risikoaufschläge und Doppelzählungen. Gib eine eigene Bandbreite nur an, wenn sie aus
zugänglicher Ground Truth herleitbar ist.

## Evidenzpflicht

- Belege mit `path:line` nennen; historische Belege als `<ref>:path:line`.
- Ausgeführte Kommandos und ihr relevantes Ergebnis knapp dokumentieren.
- Fehlgeschlagene Checks als fehlgeschlagen kennzeichnen und nicht in Belege umdeuten.
- Keine Secrets, Tokens oder langen Credentialwerte wiedergeben.
- Empfehlungen angeben, die das Dokument konkret freigabefähiger machen.
- Für jeden tragenden Claim Belegstatus und Zeitstand getrennt ausweisen.
- `implementiert`, `gemergt`, `deployed`, `live` und `verhaltensgeprüft` nicht gleichsetzen.
- Offene Entscheidungen nicht als technische Restarbeit tarnen.
- Interne Staging- und `.handoff`-Pfade niemals im finalen Bericht wiedergeben. Zitiere die primäre Quelle als `Snapshot:<Zeile>` und den eingefrorenen technischen Anhang als `Anhang:<Zeile>`; der vollständige interne Pfad bleibt ausschließlich im Prompt und in der Telemetrie.

## Claim-Matrix

Führe jede tragende Aussage mit stabiler ID in dieser Tabelle:

```text
| ID | Tragende Aussage | Belegstatus | Stand/Ref | Gegenprüfung | Auswirkung |
```

Erlaubte Belegstatus: `BELEGT`, `PLAUSIBEL`, `UNBEKANNT`, `WIDERSPRUCH`.
Der Belegstatus beschreibt die Evidenzlage und ist nicht das Gesamturteil.

## Urteilsskala

Verwende genau eines als Gesamturteil:

- `TRÄGT`
- `TRÄGT MIT ÄNDERUNGEN`
- `NICHT BELASTBAR`
- `WIDERLEGT`
- `UNBEKANNT`

## Ausgabeformat

Deine finale Antwort muss ohne Vorrede exakt mit folgender Zeile beginnen:

# {{REPORT_TITLE}} — Judge {{JUDGE_ID}}

Danach exakt diese Abschnitte:

## Gesamturteil
## Tragende Befunde
## Claim-Matrix
## Detailprüfung der Behauptungen
## Abhängigkeiten, Gates und offene Entscheidungen
## Scope-Abdeckung und nicht zugeordnete Flächen
## Risiken, Lücken und Widersprüche
## Konkrete Korrekturen vor Freigabe
## Belege und durchgeführte Prüfungen
## Grenzen der Methode
## Offene Punkte / UNBEKANNT

Wenn Abhängigkeiten/Gates oder Scope für das Artefakt nachweislich nicht einschlägig sind, schreibe
im jeweiligen Abschnitt knapp `NICHT EINSCHLÄGIG` mit Begründung; lasse ihn nicht weg.

Unter `Grenzen der Methode` nenne ausdrücklich, welche Repositorys/Refs, Laufzeitumgebungen,
externen Systeme, Tests und Daten nicht geprüft wurden und welche stärkeren Aussagen deshalb nicht
zulässig sind. Nenne dabei keine internen Handoff-, Snapshot-, Prompt-, Raw- oder Telemetriepfade;
verwende ausschließlich die öffentliche Quellenbezeichnung.

Gib ausschließlich den vollständigen Markdown-Bericht aus. Ändere und erzeuge keine Datei.
