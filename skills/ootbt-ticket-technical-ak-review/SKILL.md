---
name: ootbt-ticket-technical-ak-review
description: Use when technical ticket acceptance criteria need review.
version: 1.0.0
author: nowrap (Out-of-the-Box Thinking)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ootbt, ticket, acceptance-criteria, technical-review, jira, youtrack, gitlab, multi-agent]
    related_skills: [ootbt-dual-judge-markdown-review]
---

# OOTBT Ticket Technical-AK Review

## Überblick

Dieser Skill prüft **technische Akzeptanzkriterien eines Tickets** gegen einen eingefrorenen
Code-, Konfigurations-, Test- und Dokumentationsstand. Er ist trackerneutral und unterstützt:

- Jira über `acli` zum Lesen und Jira REST API v3 für strukturiertes ADF-Publishing;
- YouTrack über vorhandene MCP-Werkzeuge oder die YouTrack REST API;
- GitLab Issues über `glab`.

Der Workflow zerlegt das Ticket in kriteriumsweise, kontextarme Prüfaufträge. Faktische Kriterien
werden nicht unnötig an ein teures Urteilmodell gegeben. Kriterien mit gebündelten Aussagen,
Systemsemantik oder Architektururteilen werden gezielt stärker geroutet. Fable ist ein
**Konflikt-Judge**, kein Erstprüfer. Beleg schlägt Modellmehrheit.

Der Skill ist ein Geschwister-Workflow von `ootbt-dual-judge-markdown-review`, aber kein Aufruf
oder Spezialfall davon: Prüfgegenstand ist ein Ticket plus Repository-Bestand, nicht eine einzelne
Markdown-Datei. Er erzeugt standardmäßig ein integriertes AK-Review statt zweier unverbundener
Judge-Berichte.

## Wann verwenden

- technische oder Entwicklungs-AKs eines Jira-, YouTrack- oder GitLab-Tickets gegen Code prüfen;
- vor QA-Handoff feststellen, was am Zielstand nachgewiesen, teilweise belegt oder offen ist;
- mehrere AKs parallel, aber ohne monolithischen Modellkontext prüfen;
- strittige Kriterien evidenzbasiert mit einer zweiten Instanz entscheiden;
- ein Review als Markdown vorbereiten und optional kontrolliert im Ticketsystem publizieren.

Nicht automatisch verwenden für:

- fachliche Produktabnahme ohne technische Ground Truth;
- reine QA-/Review-AKs, sofern der Nutzer sie nicht ausdrücklich einschließt;
- allgemeine Plan- oder Sachverhalts-Challenges ohne Ticket — dafür
  `ootbt-dual-judge-markdown-review`;
- ein vollständiges Thesis → Judge → Evaluator-Verfahren — dafür `cross-review`;
- Ticket-Presence oder Backport-Vollständigkeit nur anhand von Ticket-IDs.

## Eingabevertrag

Vor der Collection müssen mindestens feststehen:

```text
tracker         jira | youtrack | gitlab
ticket          stabile ID oder URL
repoRoots       ein oder mehrere explizite Git-Repositories
targetRefs      je Repo ein fester Commit-SHA
baseRefs        optional je Repo ein fester Commit-SHA
criterionScope  technische/Entwicklungs-AKs; Ausschlüsse explizit
publish         false (Default) | true nach sichtbarer Freigabe
```

Ein Branchname allein ist kein eingefrorener Zielstand. Er wird vor dem Review in einen vollen SHA
aufgelöst. Bei mehreren Repositories trägt jeder Beleg `repoId` und `commit`. Vor allem Plugin- oder
Sibling-Repositories nicht still dem Hauptrepo zurechnen: den Root je relevantem Pfad mit
`git rev-parse --show-toplevel` bestimmen.

Der Zielbaum beantwortet: **Existiert die behauptete Implementierung am geprüften Stand?** Ein
optionaler Basis→Ziel-Diff erklärt, was sich änderte, ersetzt aber keinen Beleg im Zielbaum.
Ticket-ID-Treffer in Commit-Subjects oder Kommentaren sind nur Suchhilfen.

**Fertig, wenn:** Tracker, Ticket, Scope, alle Repo-Roots und vollständigen Ziel-SHAs im
Laufmanifest stehen.

## Tracker-Adapter

Nach Auswahl von Jira, YouTrack oder GitLab die passende Sektion aus
`references/tracker-adapters.md` laden. Toolnamen und Schemas live prüfen; insbesondere keine
YouTrack-MCP-Namen raten. Ticket-Rohdaten lokal einfrieren, Quelladapter und Abrufzeit
dokumentieren und Secrets aus Snapshots entfernen.

**Fertig, wenn:** Die aktuelle Ticket-Originalquelle erfolgreich gelesen und gehasht wurde oder
der Zugriff sichtbar als `UNBEKANNT` blockiert ist.

## Artefaktvertrag

Flüchtige Arbeitsdaten:

```text
<repo-root>/.handoff/<timestamp>_<ticket>_technical-ak-review/
├── manifest.json
├── ticket/
│   ├── raw.<json|md>
│   ├── criteria-extracted.json
│   └── criteria-approved.json
├── evidence/
│   ├── repository-manifest.json
│   └── criterion-<id>.md
├── prompts/
├── runs/<anonymous-run-id>/
│   ├── prompt.md
│   ├── raw-output.*
│   └── metrics.json
├── judgments/
└── staging/
    └── technical-ak-review.md
```

Dauerhafter ticketbezogener Output liegt im Repository des geprüften Codes:

```text
docs/tasks/<TICKET-ID>/technical-ak-review/
├── review.md
└── evidence-manifest.md
```

Existiert eine verbindliche Projektdokumentationsstruktur, gewinnt diese. `.handoff`-Pfade,
Promptpfade, Rohoutputs und absolute lokale Pfade dürfen nicht in veröffentlichte Ticketkommentare
gelangen. Dauerhafte Evidence-Manifeste nennen öffentliche Pfade/Refs und Hashes statt interner
Arbeitsordner.

## Nicht verhandelbare Regeln

1. **AK-Text zuerst einfrieren.** Modelle lesen nicht wiederholt das bewegliche Live-Ticket.
2. **Original und Zerlegung erhalten.** Atomare Teilclaims dürfen die ursprüngliche Reichweite
   weder still erweitern noch verkleinern.
3. **Ein AK = ein Prozess je Primärspur = eine Ergebnisdatei je Spur.** Sonnet, Terra und
   OpenCode laufen im TRIAD-Profil getrennt; kein Prozess hängt an einem früheren Modellchat oder
   schreibt in eine gemeinsame Append-Datei.
4. **Relevanter Kontext statt Gesamtrepo.** Pro Auftrag feste Pfade, kleine Ausschnitte und fixe
   Refs; keine vollständige Quelldatei nur aus Bequemlichkeit übergeben.
5. **Zielbaum-Primat.** Diff, Commit-Subject und Ticket-ID sind keine Erfüllungsbeweise.
6. **Read-only Prüfer.** Reviewer verändern weder Repository noch Ticket und publizieren nicht.
7. **Fachurteil und Address-Gate trennen.** Eine reale Fundstelle beweist nicht automatisch die
   richtige Interpretation.
8. **Negative Claims brauchen negative Sonden.** „Existiert nicht“ oder „keine Regel greift“ darf
   nicht aus einem einzelnen Suchbegriff folgen.
9. **Gebaut ≠ getestet ≠ deployed ≠ produktiv wirksam.** Nachweisstufen getrennt ausweisen.
10. **Beleg schlägt Mehrheit.** Keine automatische Konsens- oder Mehrheitslogik.
11. **Fable judgt, sammelt aber nicht zuerst.** Ein Judge sieht einen kleinen eingefrorenen
    Konfliktvertrag, nicht das gesamte Ticket zur freien Erstprüfung.
12. **Publishing ist opt-in.** Vorschau und Ziel erneut zeigen; erst nach expliziter Freigabe
    kommentieren.
13. **`UNBEKANNT` ist ein korrektes Ergebnis.** Fehlende Rechte, Tests oder Laufzeitdaten niemals
    durch plausible Modellprosa ersetzen.

## Ablauf

### 1. Ticket und Repository-Stand einfrieren

- Ticket über den passenden Adapter lesen und Rohantwort hashen.
- Branch/Ref je Repo in vollen SHA auflösen; Repo-Status und Remote-URL erfassen.
- Bei ausdrücklich gewähltem Commit sind fremde Worktree-Änderungen nicht Teil des Prüfstands.
- Repository-Regeln aus dem steuernden Checkout lesen; den geprüften Code refqualifiziert mit
  `git show <sha>:<path>` oder einem detached Worktree untersuchen.
- Bei Netzaktualität klar unterscheiden: lokaler Remote-Tracking-Stand ist nicht automatisch
  aktueller Serverstand. Fetch nur, wenn erlaubt.

**Fertig, wenn:** Ticket-Hash, Target-SHAs, optional Base-SHAs, Branch-Hinweise und Repo-IDs im
Manifest stehen.

### 2. Technische AKs extrahieren und bestätigen

- Nur technische/Entwicklungs-AKs extrahieren; QA-/Review-Kriterien separat inventarisieren und
  standardmäßig ausschließen.
- Nummerierung und Wortlaut bewahren.
- Gebündelte Kriterien in atomare Subclaims zerlegen, aber unter derselben AK-ID belassen.
- Jedes Kriterium klassifizieren:

```text
FAKTISCH       direkte Existenz, Wert, Mapping, Test, Fehlerpfad
URTEIL         „typischerweise“, DRY, angemessen, vollständig, konsistent
SYSTEMISCH     Verhalten über Komponenten/Lerneinheiten/Mandanten/Phasen hinweg
NEGATIV        „keine“, „nie“, „entfernt“, „greift nicht“, Vollständigkeitsclaim
LAUFZEIT       nur durch ausgeführte Tests, Logs oder Umgebung belegbar
```

Mehrfachklassifikation ist erlaubt. Ist Extraktion, Abschnittsgrenze oder Zerlegung mehrdeutig,
dem Nutzer `criteria-extracted.json` zur Bestätigung vorlegen. Ohne interaktiven Nutzer darf ein
Cron-/Batchlauf die unsichere Menge nicht still genehmigen; er endet mit `UNBEKANNT`.

**Fertig, wenn:** Jedes freigegebene AK einen Originaltext, atomare Subclaims, Klassifikation und
stabile ID besitzt.

### 3. Evidence Pack und Routingmatrix bauen

Der Runner lokalisiert Mapper/Services/Call Paths/Tests/Config/Dokumentation, ohne schon das
Endurteil zu setzen. Je AK entsteht ein kleiner Evidence-Shard:

- Original-AK und Subclaims;
- Repo-ID, Ziel-SHA und optional Basis-SHA;
- höchstens acht primäre Pfade;
- nur relevante Ausschnitte oder refqualifizierte Lesekommandos;
- bekannte Tests und ein ausführbarer Verifikationsweg;
- offene Suchflächen und verbotene Schlussfolgerungen.

Keine Ticket-ID-Nennung als Evidenz einspeisen, wenn sie nur Dokumentation oder Kommentar ist.
Jede Routingzeile nennt Primärprüfer, Begründung und mögliche Eskalation.

**Fertig, wenn:** Jeder Primärprozess ohne Zugriff auf Ergebnisse anderer Kriterien selbstständig
antworten kann und keine Platzhalterpfade enthält.

### 4. Primärprüfer kriteriumsweise und parallel starten

Parallelität ist innerhalb dieser eingefrorenen Phase erlaubt. Der Standard ist das
**TRIAD-Profil**: pro AK laufen drei frische, gegenseitig blinde Primärprozesse gegen denselben
Evidence-Shard:

1. Claude **Sonnet** als ausgewogener Hauptprüfer;
2. OpenAI **GPT-5.6 Terra** als ausgewogenes ChatGPT-/Codex-Gegenstück;
3. **OpenCode** ausschließlich mit einem vom Nutzer freigegebenen lokalen Ollama-Modell.
   Zulässig sind nur live verifizierte Modell-IDs unter `<LOCAL_PROVIDER_PREFIX>/*`; externe OpenCode-,
   OpenRouter- oder Cloud-Provider sind für diese Spur ausgeschlossen.

Damit entstehen pro AK drei getrennte Ergebnisdateien. Keine Primärstimme liest eine andere und
keine Mehrheit wird automatisch zum Urteil. Ein optionales **LEAN-Profil** mit genau einem
Primärprüfer ist nur nach ausdrücklicher Wahl oder bei Budget-/Verfügbarkeitsgrenzen zulässig.

#### Modellfamilien und Abstufung

| Rolle | Claude | OpenAI | Einsatz |
|---|---|---|---|
| stärkste Eskalation | Opus 5 | GPT-5.6 Sol | nur schwierige systemische/urteilsintensive Konflikte |
| ausgewogener Primärprüfer | Sonnet 5 | GPT-5.6 Terra | Standard je AK im TRIAD-Profil |
| kostengünstiger Helfer | Haiku | GPT-5.6 Luna | Extraktion, Normalisierung, mechanische Hilfsarbeit; keine unabhängige Hauptstimme ohne Auftrag |
| schneller Coding-Spezialist | — | GPT-5.3 Codex Spark | optionale kurze Code-Sonde; separate ältere Codex-Familie, **kein** GPT-5.6-Tier und kein Ersatz für Terra |

Die OpenAI-Abstufung lautet damit **Sol → Terra → Luna**. Spark gehört zusätzlich in den
Werkzeugkasten, aber nicht als vermeintliches drittes GPT-5.6-Tier. Modellnamen und Verfügbarkeit
werden live gesmoke-testet; diese Tabelle ist Routingsemantik, kein Verfügbarkeitsbeweis.

#### Modellrouting

- **TRIAD-Primärphase:** Sonnet + Terra + OpenCode für jedes AK, unabhängig von dessen Klasse.
  Die Klassifikation steuert Toolbudget, Reasoning-Effort und spätere Eskalation, nicht die
  Kardinalität der drei Primärstimmen.
- **URTEIL oder SYSTEMISCH:** bei unresolved Dissens punktuell Opus 5 oder GPT-5.6 Sol,
  insbesondere für gebündelte Wirkungsbehauptungen, „typischerweise“, DRY, Vollständigkeit oder
  Architektursemantik. Beide nicht für triviale Existenzchecks verschwenden.
- **OpenCode:** ausschließlich lokale Ollama-Modelldiät mit explizitem Providerpräfix
  `<LOCAL_PROVIDER_PREFIX>/*` und kleinem Kontext. Deshalb strikt ein Auftrag, ein Prozess, eine Ergebnisdatei;
  kein Gesamtticket, keine ganze Quelldatei, keine Folgeaufträge im selben Chat. Externe Modelle
  wie `opencode/*`, OpenRouter, Anthropic oder OpenAI sind in dieser Spur verboten. Ist kein
  lokales Modell technisch nutzbar, bleibt die OpenCode-Spur als sichtbarer technischer Ausfall
  offen; sie wird nicht durch einen Cloud-Fallback ersetzt.
- **Sonnet:** frischer Prozess je AK; ausgewogene Claude-Hauptstimme.
- **Terra:** frischer Codex-Prozess je AK; ausgewogene OpenAI-/ChatGPT-Hauptstimme.
- **Sol/Opus:** Eskalationsmodelle, nicht planmäßige vierte und fünfte Primärstimme.
- **Luna/Haiku/Spark:** optionale Helfer oder Sonden; ihre Ergebnisse zählen nur dann als Stimme,
  wenn der Laufvertrag das ausdrücklich festlegt.
- **Fable 5:** nie regulärer Primärprüfer; nur Judge nach Eskalation.

Das TRIAD-Profil liefert drei Modelldiäten nur, wenn OpenCode tatsächlich über den explizit
konfigurierten lokalen Provider läuft und nicht dasselbe canonical Modell wie Claude oder OpenAI nutzt.
Die OpenCode-Konfiguration, Ollama-Basis-URL ohne Credentials, Modell-ID und Telemetrie werden
vor dem Fan-out erfasst. Ein Cloud-Fallback ist unzulässig. Gleiche Modelle in getrennten
Prozessen sind kontextisoliert, aber keine zusätzliche Modellfamilie.

Vor einer Modellphase Version, Providerpfad, Aliasauflösung, tatsächliches Modell und terminalen
Abschluss smoke-testen. Nicht still auf ein anderes Modell oder schwächeren Effort fallen.

**CLI-Härtung:** Das erlaubte Shell-Tool ist OS-/Harness-spezifisch. Claude Code kann unter
Windows trotz `PowerShell`-Hinweisen echte Repo-Sonden als `Bash` emittieren; eine unpassende
Allowlist führt dann zu Permission-Denials und Turn-Limit-Schleifen. Vor dem Fan-out einen echten
Read-/Such-/Parser-Smoke-Test über exakt dieselbe Tool-Allowlist ausführen. Wenn `Bash` nötig ist,
ist es nur im disposable detached Worktree zulässig und dessen Status wird danach geprüft.

Codex `--sandbox read-only` kann unter Windows beim Prozessstart mit
`CreateProcessWithLogonW failed: 2` scheitern, obwohl das Modell selbst erreichbar ist. Das ist
kein Fachurteil. Nach genau diesem strukturierten Sandbox-Fehler darf der frische Lauf im
**disposable detached Worktree** mit `--sandbox danger-full-access`, `--ask-for-approval never` und
einem explizit read-only Prompt wiederholt werden; vorher/nachher `git status --short` vergleichen
und jeden Unterschied als Policy-Verstoß behandeln. Nie im Benutzercheckout eskalieren.

OpenCode-Modelle müssen einen echten Smoke-Test bestehen. Zulässig sind ausschließlich lokal über
Ollama angebotene IDs unter `<LOCAL_PROVIDER_PREFIX>/*`. Gibt das lokale Modell Tool-XML nur als
Text aus oder ignoriert der Standard-`build`-Agent den read-only Vertrag, einen **frischen**,
projektisolierten One-Shot-Agenten verwenden: eigener Config-/State-Pfad außerhalb des Repos,
Provider und Modell explizit auf `<LOCAL_PROVIDER_PREFIX>/*`, `permission: {"*":"deny"}` und ein vorab
erzeugter begrenzter Evidence-Shard. Bei `qwen3-coder-agent` kann `tools: {"*":false}` zu einer
leeren Ein-Token-Antwort führen; dann Tools im Agentenschema sichtbar lassen, ihre Ausführung aber
per Permission verweigern, den Shard **inline** in den Nutzerprompt setzen und jeden tatsächlich
emittierten Tool-Event als ungültigen Lauf verwerfen. Der Shard enthält nur kriteriumsrelevante
Ausschnitte mit Zeilennummern und festen Refs.

Bei `--format json` kann OpenCode nach dem Primärbericht zusätzliche Titel-/Summary-Housekeeping-
Schritte emittieren. Als Bericht nur den ersten nichtleeren, mit `reason=stop` abgeschlossenen
Modellschritt extrahieren; trotzdem Tool-Events im **gesamten** Rohstream prüfen und bei irgendeinem
Tool-Event den Lauf verwerfen. Report muss bytegleich aus diesem Primärschritt stammen, einen
erlaubten Urteilswert und den exakten finalen `Fertig:`-Marker besitzen. Scheitert auch dieser
Modus, zählt die OpenCode-Spur als technischer Ausfall. Kein Wechsel auf `opencode/*`, OpenRouter
oder einen anderen Cloud-Provider. Fehlgeschlagene Rohlogs bewahren und nicht denselben Prozess
weiterprompten. Mehrere lokale OpenCode-Prozesse können außerdem dieselbe SQLite-State-DB sperren
(`database is locked`). Deshalb OpenCode standardmäßig **seriell** fan-outen oder jedem Prozess ein
nachweislich isoliertes State-Verzeichnis geben; Parallelität der Sonnet-/Terra-Spuren bleibt davon
unberührt.

Shell-Zugriff kann trotz gesperrtem `Write`-Tool Dateien erzeugen. Primärprüfer deshalb im
disposable detached Worktree starten, ihren `git status --short` vorher/nachher vergleichen und
jeden Schreibversuch als Policy-Verstoß behandeln. Toolaufrufe im Prompt begrenzen, `max-turns`
oberhalb dieses Budgets setzen und nur `subtype=success`, terminalen Abschluss, Ergebnistext und
null Permission-Denials akzeptieren. Fehlversuche samt Telemetrie bewahren; Wiederholungen sind
frisch und enger gescoped.

Unmittelbar vor dem Rendern Branch und HEAD des steuernden Checkouts erneut erfassen. Hat sich ein
beweglicher Branch nach dem Einfrieren verändert, bleibt das Review am ursprünglichen Ziel-SHA;
der spätere Stand wird sichtbar als nicht geprüft ausgewiesen und nicht still in Belege gemischt.

Der Einzelauftrag folgt `templates/criterion-review-prompt.md` und endet mit
`Fertig: <konkrete Ergebnisdatei>`.

**Fertig, wenn:** Im TRIAD-Profil pro AK drei formal gültige Primärberichte oder je Spur ein
sichtbarer technischer Ausfall vorliegen; fehlende Kriterien oder Spuren werden nie still
ausgelassen.

### 5. Runner-Gate: Belege mechanisch und semantisch gegenprüfen

Für jeden positiven Codebeleg:

1. Repo-ID und Commit stimmen mit dem Laufvertrag.
2. Datei existiert per `git show <sha>:<path>`.
3. Zeilenbereich ist gültig.
4. Der Runner liest den kanonischen Ausschnitt selbst; keine LLM-Transkription als Ground Truth.
5. Commitgebundener GitLab-Link ist reproduzierbar.
6. Kommentar, String, Dokumentation und aktiver Code werden nicht gleichgesetzt.

Für jeden negativen oder absoluten Befund:

- mindestens zwei verschiedenartige, scopesichtbare Gegenproben;
- Suchwurzel und ausgeschlossene Flächen nennen;
- relevante Synonyme, alte Namen, dynamische Aufrufe und sibling call paths berücksichtigen;
- bei nicht ausführbarer Probe `UNBEKANNT`, nicht `NICHT_NACHGEWIESEN`.

Tests nur als ausgeführt bezeichnen, wenn echter Command, Exit-Code und relevante Ausgabe
vorliegen. Ein vorhandener Test beweist nur die von ihm tatsächlich asserted Semantik.

**Fertig, wenn:** Jeder tragende Beleg einen getrennten fachlichen Status und Gate-Status besitzt;
alle empfehlungsändernden Zahlen, Pfade und Tests reproduziert sind.

### 6. Nur getriggert eskalieren

Eine zusätzliche, claimbezogene Gegenprüfung wird nur gestartet, wenn mindestens ein Trigger
vorliegt. Sie ist keine weitere reguläre Primärspur: Im `LEAN`-Profil kann sie die zweite
Modellantwort sein, im `TRIAD`-Profil ist sie eine fokussierte Zusatzprüfung nach den drei bereits
abgeschlossenen Primärprozessen.

- AK bündelt mehrere Wirkungen oder hat `URTEIL`/`SYSTEMISCH`/`NEGATIV`;
- absolute Aussage wie „alle“, „keine“, „einzige“, „vollständig“, „immer“, „nie“;
- DRY-, Seiteneffekt-, Fallback-, Mandanten-, Berechtigungs- oder Reihenfolgebehauptung;
- Primärbeleg scheitert am Gate oder Test ist nicht reproduzierbar;
- zwei Kriterien oder Quellen widersprechen sich;
- Primärurteil ist `UNBEKANNT` und die offene Frage kann die Empfehlung ändern;
- der Runner findet ein entscheidungsänderndes Gegenbeispiel.

Die zusätzliche Gegenprüfung erhält nur den strittigen Claim, den nötigen Evidence-Shard, Triggergrund und
fixe Refs. Sie läuft in einer **anderen Modellfamilie**, wenn verfügbar. Ihre Aufgabe ist
Gegenprüfung, nicht Bestätigung.

Bleibt danach ein entscheidungsrelevanter Dissens, wird ein anonymes Judge-Bundle gebaut:

```text
AK-ID und Originaltext
strittiger atomarer Claim
Urteil A + Belegadresse
Urteil B + Belegadresse
fixe Refs und reproduzierbare Prüfkommandos
keine Modellnamen, keine Urheberhinweise
```

Fable 5 entscheidet dieses Bundle in einer frischen Instanz mit
`TRÄGT | ÜBERZOGEN | FALSCH | UNBELEGT` und separater Sicherheit
`VERIFIZIERT | PLAUSIBEL | UNBEKANNT | WIDERSPRUCH`. Fable darf zusätzliche kleine Gegenprüfungen
am eingefrorenen Bestand ausführen, aber keinen neuen Gesamtreview beginnen. Das Judge-Urteil ist
wiederum ein Claim; der Runner reproduziert jeden entscheidungsändernden Befund.

**Fertig, wenn:** Jeder Eskalationslauf einen dokumentierten Trigger hat, Dissens sichtbar bleibt
und kein Urteil allein per Stimmenzahl übernommen wurde.

### 7. AK-Disposition auswerten

Das integrierte Ergebnis beantwortet getrennt:

1. Ist das AK am eingefrorenen Stand erfüllt?
2. Ist das AK selbst eindeutig, atomar, technisch zugeordnet und prüfbar formuliert?

Ein frischer Auswerter erhält die anonymisierten Primärurteile, Gate-Ergebnisse, Konflikturteile
und den Original-AK-Text. Er ist keine zusätzliche Stimme. Er entscheidet nach reproduzierbarer
Evidenz anhand von `templates/ak-disposition-prompt.md` und weist pro AK genau eine Disposition zu:

- `KEEP`: AK ist brauchbar und am Zielstand erfüllt;
- `KEEP_UNMET`: AK ist brauchbar, aber nicht oder nur teilweise erfüllt;
- `REFINE`: Reichweite oder Nachweisbedingung muss präzisiert werden;
- `SPLIT`: gebündelte, unabhängig prüfbare Subclaims werden getrennt;
- `MOVE_TO_QA`: Kriterium beschreibt Produkt-/QA-Abnahme statt technischen Zielzustand;
- `REMOVE_PROPOSED`: nachweislich obsolet oder redundant; Entfernung benötigt Menschenfreigabe;
- `PRODUCT_DECISION_REQUIRED`: Konflikt kann nicht technisch entschieden werden;
- `UNKNOWN`: zugängliche Ground Truth reicht für keine belastbare Disposition.

„Nicht erfüllt“ führt niemals automatisch zu `REMOVE_PROPOSED`. Der Auswerter schreibt nur einen
Änderungsvorschlag. Eine neue AK-Liste wird erst aus einem eingefrorenen Dispositionsvertrag erzeugt;
Trackeränderungen bleiben opt-in und benötigen Vorschau, Hash, Ziel-Recheck und explizite Freigabe.

Pflichtmatrix:

```text
| AK | Erfüllungsstatus | Gate-Status | Disposition | Vorgeschlagener Wortlaut | Begründung | Freigabe |
```

Bei `REFINE` oder `SPLIT` enthält der Vertrag Originaltext, atomare Zielclaims und vollständig
ausformulierten Ersatztext. Ein separater Reviser darf nur diesen Vertrag anwenden und keine neuen
Produktentscheidungen treffen.

**Fertig, wenn:** Jedes AK genau eine evidenzgebundene Disposition besitzt und jede vorgeschlagene
Textänderung auf einen vom Runner reproduzierten Befund oder eine sichtbare offene Entscheidung
zurückgeführt ist.

### 8. Integriertes Review rendern

Status je AK:

- `ERFÜLLT_LAUT_REVIEW`;
- `TEILWEISE_LAUT_REVIEW`;
- `NICHT_NACHGEWIESEN`;
- `WIDERSPRUCH`;
- `UNBEKANNT`.

Gate-Status separat:

- `BELEGE_ADRESSGEPRÜFT`;
- `BELEGE_TEILWEISE_GEPRÜFT`;
- `BELEGE_FEHLERHAFT`;
- `BELEGE_UNGEPRÜFT`.

Pflichtstruktur:

```text
# Technischer AK-Review — <TICKET>
## Scope und eingefrorener Stand
## Kriterienmatrix
## Detailprüfung je AK
## Ausgeführte Tests und Sonden
## Eskalationen und Dissens
## Nicht geprüfte Flächen / UNBEKANNT
## Empfehlung für den technischen Handoff
## Provenienz und Methodengrenzen
```

Die Kriterienmatrix enthält mindestens:

```text
| AK | Kurzfassung | Fachstatus | Gate-Status | Disposition | Primärbeleg | Eskalation | Konsequenz |
```

Reviewer-/Modellzuordnung bleibt während eines anonymen Judgments verborgen, wird im finalen
Review aber vollständig mit tatsächlichem Tool, systemverifiziertem canonical model und Rolle
aufgelöst. Hilfsmodelle/Subagenten offenlegen, nicht als zusätzliche unabhängige Stimme zählen.

Keine QA-Testempfehlungen aus ausgeschlossenen Review-AKs erfinden. Technische Restprüfungen sind
zulässig, müssen aber klar von Produkt-/QA-Abnahme getrennt sein. Footer sinngemäß:

> Dieser Review ist eine technische Lesehilfe, keine Produkt-, QA- oder Release-Freigabe.

**Fertig, wenn:** Alle freigegebenen AK-IDs genau einmal in der Matrix vorkommen, Teilclaims in der
Detailprüfung vollständig abgedeckt sind und jede stärkere Aussage mit ihrer Methodengrenze
vereinbar ist.

### 9. Validieren und optional publizieren

Vor Publikation:

- Ticket-Livequelle erneut lesen oder mindestens Ziel-ID/URL unmittelbar verifizieren;
- Target-SHAs und Berichtshash nennen;
- keine Secrets, lokalen absoluten Pfade, `.handoff`-Pfade oder Rohtelemetrie im Kommentar;
- Links sind commitgebunden und zeigen auf die tatsächlich zitierte Zeile;
- Vorschau und Payload hashen;
- Nutzer sieht Tracker, Ticket, Vorschau und Ziel und gibt das Publishing ausdrücklich frei.

Publishing-Adapter:

- **Jira:** ADF über getesteten Repo-Adapter oder REST API v3; `acli` nicht blind als
  Formatgarantie behandeln.
- **YouTrack:** vorhandenes MCP-Comment-Tool gemäß Live-Schema, sonst REST API; Antwort-ID/URL
  zurücklesen.
- **GitLab:** `glab issue note`; anschließendes `glab issue view --comments` oder API-Readback.

Nach dem Schreiben Kommentar/Notiz zurücklesen und Marker oder Hash gegen die freigegebene
Payload prüfen. Ohne Readback nicht „publiziert und verifiziert“ behaupten.

**Fertig, wenn:** Entweder ein validierter Dry-Run-Bericht vorliegt oder der freigegebene Kommentar
mit externer ID/URL zurückgelesen wurde.

## Abbruchkriterium

Eine weitere Modellrunde ist nur gerechtfertigt, wenn sie Fachstatus, Empfehlung, Scope oder eine
tragende Abhängigkeit ändern kann. Liefert eine Runde nur Formulierungsvarianten, stoppen. Ein
technischer Ausfall wird nicht durch beliebig viele identische Retries in derselben Modellfamilie
kompensiert.

## Häufige Fehler

1. **Alle AKs in einen Prompt kippen.** Kontext und Zustände vermischen sich. → Ein AK je Prozess
   und je Primärspur eine eigene Ergebnisdatei.
2. **TRIAD per Mehrheit entscheiden.** Drei gleiche Stimmen sind kein Beweis. → Belege einzeln
   gaten; Dissens erhalten und nur triggerbasiert eskalieren.
3. **Opus oder Sol für triviale Fakten verwenden.** Teuer ohne Urteilsvorteil. → Nur punktuell
   eskalieren.
4. **Spark als GPT-5.6-Unterstufe behandeln.** Spark ist ein separater GPT-5.3-Codex-
   Geschwindigkeitsspezialist. → Sol/Terra/Luna als 5.6-Abstufung verwenden.
5. **Fable als Erstprüfer einsetzen.** Judge-Rolle geht verloren. → Nur Konfliktbundle.
6. **OpenCode Folgeaufträge geben.** Kleiner Kontext läuft voll. → Frischer Prozess und eigene
   Datei pro Kriterium.
7. **OpenCode auf ein Cloud-Modell routen.** Verletzt die vertraglich lokale Ollama-Spur. → Nur
   `<LOCAL_PROVIDER_PREFIX>/*`; bei lokalem Ausfall technische Lücke offen ausweisen, niemals Cloud-Fallback.
8. **Eine frische Instanz als neue Modelldiät zählen.** Kontextisolation ist keine
   Familienunabhängigkeit. → Canonical Modelle und Provider offenlegen.
9. **Ticket-ID als Codebeleg.** Commit-Subject oder Kommentar beweist keine Erfüllung. → Zielbaum.
10. **Belegadresse als Fachbeweis behandeln.** Reale Zeile kann semantisch irrelevant sein. →
   Gate und Urteil trennen.
11. **„Keine Regel greift“ aus einem Nulltreffer.** Synonyme/dynamische Pfade fehlen. → Mehrere
    Sonden oder `UNBEKANNT`.
12. **Branchlinks veröffentlichen.** Branch bewegt sich. → Voller Commit-SHA im Link.
13. **Trackerkommentar ohne Freigabe posten.** → Vorschau, Hash, Ziel-Recheck, explizites Opt-in.
14. **Toolalias oder Modellname glauben.** → Live-Smoke-Test und canonical Telemetrie.
15. **Dissens glattbügeln.** → Alle Belege zeigen; evidenzbasiert entscheiden oder offenlassen.
16. **Nicht erfüllt mit unnötig verwechseln.** → Brauchbare offene Anforderungen als `KEEP_UNMET`
    erhalten; Entfernung nur begründet vorschlagen und menschlich freigeben.
17. **Auswerter schreibt das Ticket um.** → Dispositionsvertrag und Reviser trennen; Publishing
    bleibt ein eigenes Opt-in-Gate.

## Verifikationscheckliste

- [ ] Ticket wurde über die aktuelle Originalquelle gelesen und gehasht.
- [ ] Scope enthält nur die ausdrücklich gewünschten technischen AKs.
- [ ] Alle Repo-Roots und Zielstände sind als volle SHAs fixiert.
- [ ] Original-AKs, atomare Subclaims und Klassifikation sind nachvollziehbar.
- [ ] Im TRIAD-Profil besitzt jedes AK je einen getrennten Sonnet-, Terra- und OpenCode-Lauf mit
      eigener Ergebnisdatei oder einem sichtbaren technischen Ausfall.
- [ ] OpenCode-/Kleinmodell-Shards enthalten feste Pfade und keinen monolithischen Kontext.
- [ ] Canonical Modelle bestätigen Sonnet, Terra und ein ausschließlich lokales, explizit
      konfiguriertes OpenCode-Modell; kein OpenCode-Cloud-Fallback wurde als Primärspur gewertet.
- [ ] Gleiche Familien werden nicht doppelt als Modelldiät gezählt.
- [ ] Sol und Opus wurden nur für echte Urteils-/Systemeskalationen eingesetzt; Luna, Haiku und
      Spark nur in der im Laufvertrag ausgewiesenen Helferrolle.
- [ ] Jede Zweitprüfung nennt einen deterministischen Eskalationstrigger.
- [ ] Fable wurde nur als frischer, anonymer Konflikt-Judge eingesetzt.
- [ ] Positive Belegadressen wurden am fixen Commit reproduziert.
- [ ] Negative/absolute Claims besitzen ausreichende Sonden oder bleiben `UNBEKANNT`.
- [ ] Testbehauptungen stammen aus echten abgeschlossenen Testläufen.
- [ ] Fachstatus und Gate-Status sind getrennt.
- [ ] Jedes AK besitzt genau eine Disposition; `KEEP_UNMET` und `REMOVE_PROPOSED` sind getrennt.
- [ ] Vorgeschlagene AK-Änderungen stammen ausschließlich aus dem reproduzierten Dispositionsvertrag.
- [ ] Kein Mehrheitsurteil ersetzt Evidenz.
- [ ] Finales Review löst tatsächliche Tools/Modelle/Rollen auf.
- [ ] Kommentar enthält keine Secrets oder internen Arbeitswege.
- [ ] Ohne Publishing-Freigabe blieb der Lauf read-only.
- [ ] Bei Publishing wurde Ziel erneut verifiziert und Ergebnis zurückgelesen.
