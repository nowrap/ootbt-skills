---
name: ootbt-dual-judge-markdown-review
description: Use to challenge plans, implementations, or factual Markdown.
version: 2.0.0
author: nowrap (Out-of-the-Box Thinking)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ootbt, dual-judge, markdown-review, sol, frontier, fable, adversarial]
    related_skills: []
---

# OOTBT Dual-Judge Markdown Review

## Überblick

Dieser Skill führt wiederkehrende Kurzaufträge wie diese aus:

> „Bitte challenge diesen Plan / diese Implementierungsdokumentation / diesen dargestellten Sachverhalt unabhängig mit SOL und Fable 5 und lege die Reviews als Judge A und B Markdown-Dateien daneben ab.“

Er ist ein **eigenständiger Dual-Judge-Workflow**. Er benötigt weder `cross-review` noch dessen
Skripte, Templates oder Parser. Zwei frische Prozesse prüfen denselben eingefrorenen Markdown-Stand
adversarial gegen den zugänglichen Repository-Bestand. Die Berichte werden erst nach Validierung
direkt neben der Quelldatei veröffentlicht.

Der Laufvertrag wählt genau einen Modus:

- `challenge-only`: zwei unabhängige Berichte; Dissens bleibt ohne Synthese sichtbar;
- `consolidate`: nach den Judges entscheidet ein frischer, anonymer Evidence-Auswerter jeden
  strittigen Claim. Ein davon getrennter Reviser erzeugt ausschließlich aus dem eingefrorenen
  Revisionsvertrag eine neue Dokumentversion.

Standardbesetzung:

- **Judge A:** frische, kontextisolierte `gpt-5.6-sol`-Instanz mit Reasoning-Effort `max`
  über Codex. Der Codex-Katalog führt SOL als aktuelles „frontier agentic coding model“;
  `frontier` ist eine Beschreibung, kein Modellalias und kein automatischer SOL-Pro-Modus;
- **Judge B:** frische, kontextisolierte Claude-Fable-5-Instanz.

Die Buchstabenzuordnung bleibt standardmäßig stabil. Wenn der Nutzer Anonymität oder zufällige
Zuordnung verlangt, wird sie vor Start zufällig festgelegt und erst nach beiden Läufen offengelegt.

Dieser Skill erzeugt **keine** Thesenphase. Der optionale Auswerter ist keine dritte Stimme und
entscheidet nie per Mehrheit, sondern nach reproduzierbarer Ground Truth. Nicht entscheidbarer
Dissens bleibt auch im Konsolidierungsmodus `UNBEKANNT` oder `WIDERSPRUCH`.

## Wann verwenden

Primäre Anwendungsfälle:

- **Pläne:** Delivery-, Merge-, Release-, Migrations-, Rollout-, Architektur- und Umsetzungspläne;
- **Implementierungen:** Implementierungsdokumentationen, Umsetzungsberichte, technische Konzepte
  und Behauptungen darüber, was Code oder Konfiguration bereits leistet;
- **Sachverhalte:** Bewertungen, Entscheidungsgrundlagen, Ursachenanalysen, Bestandsaufnahmen,
  Vergleiche und andere faktische Darstellungen in Markdown;
- **Revisionen:** v2/v3-Fassungen, die frisch oder gegen frühere Befunde geprüft werden sollen.

Typische Formulierungen:

- „challenge diesen Plan unabhängig mit SOL und Fable 5“;
- „prüfe diese Implementierung mit Judge A und B“;
- „stimmt der hier dargestellte Sachverhalt?“;
- „lege zwei unabhängige Markdown-Reviews daneben“;
- „wieder zwei Reviews wie zuletzt“.

Aufwandsschätzungen sind ein unterstützter **Sonderfall**, nicht der primäre Trigger.

Nicht automatisch verwenden, wenn ein einziges Review genügt, eine Synthese verlangt wird oder ein
vollständiger Thesis → Judge → Evaluator-Prozess gewünscht ist.

## Artefaktvertrag

Für `<ordner>/<basis>.md`:

```text
<ordner>/<basis>-review-judge-a.md
<ordner>/<basis>-review-judge-b.md
```

Zusätzlich im Modus `consolidate`:

```text
<ordner>/<basis>-review-evaluation.md
<ordner>/<basis>-revision-contract.md
<ordner>/<basis>-v<N>.md
<ordner>/<basis>-v<N>.changes.json
```

Bei versionierten Namen bleibt die Version Teil der Basis. Im Modus `challenge-only` werden nur die
beiden validierten Berichte neben dem Prüfgegenstand veröffentlicht. Im Modus `consolidate` kommen
nur die oben genannten, validierten Konsolidierungsartefakte hinzu. Prompts, Snapshots, Rohoutputs,
Telemetrie, fehlgeschlagene Versuche und Stagingdateien bleiben in:

```text
<repo-root>/.handoff/<timestamp>_<slug>_dual-judge/
```

Bestehende Zielberichte niemals still überschreiben. Bei einem klaren Revisionsauftrag ersetzen
oder einen neuen Versionsnamen verwenden.

**Publikationsgrenze:** Kein Markdown-Bericht im Zielverzeichnis darf die Zeichenfolge `.handoff`
(unabhängig von Groß-/Kleinschreibung), einen internen Snapshot-/Prompt-/Raw-Pfad oder einen
absoluten lokalen Handoff-Pfad enthalten. Interne Provenienz bleibt ausschließlich im Handoff und
in dessen Telemetrie. Im Bericht wird die Quelle nur über eine öffentliche Quellenbezeichnung wie
`konzept-v1.md (eingefrorener Snapshot)` sowie Hash und fixe Refs benannt. Der Validator lehnt
jeden `.handoff`-Treffer hart ab; solche Berichte dürfen nicht publiziert werden.

## Nicht verhandelbare Regeln

1. **Frische Prozesse:** Keine Fortsetzung alter Sessions.
2. **Identischer Vertrag:** Scope, Snapshot, Refs, Fragen, Evidenzregeln und Schema sind gleich;
   Unterschiede nur Judge-ID und H1.
3. **Gegenseitige Blindheit:** Kein Judge liest Prompt, Rohoutput oder Bericht des anderen.
4. **Adversarial:** Widerlegung und Grenzprüfung, nicht Bestätigung.
5. **Dokument ist Claimquelle:** Ground Truth sind Bestand und reproduzierbare Prüfungen.
6. **Read-only:** Keine Dateien, Refs oder Repository-Objekte ändern; kein Netzwerk ohne Auftrag.
7. **Ein Revisionstand:** Beide prüfen bytegleich denselben Snapshot und dieselben fixen Refs.
8. **Beleg statt Mehrheit:** Übereinstimmung ist noch kein Beweis.
9. **Toolfehler ernst nehmen:** Plausibler Bericht mit gescheiterten tragenden Checks ist ungültig.
10. **Dissens erhalten:** Keine Glättung unterschiedlicher Urteile oder Zahlen.
11. **Belegstatus getrennt vom Urteil:** `BELEGT`, `PLAUSIBEL`, `UNBEKANNT` und `WIDERSPRUCH`
    beschreiben die Evidenzlage; sie ersetzen nicht das Gesamturteil.
12. **Zeitstand sichtbar:** Jeder tragende Beleg nennt Ref/Stand und, wo relevant, Prüfdatum.
    Ein historisch richtiger Befund ist nicht automatisch am aktuellen Stand richtig.
13. **Entscheidung ist kein Bau:** Offene Produkt-, Scope- oder Betriebsentscheidungen dürfen nicht
    als Implementierungsschritt oder technischer Restaufwand versteckt werden.
14. **Gebaut ist nicht verhaltensgeprüft:** Merge, vorhandener Code oder statischer Test beweisen
    weder Runtime-Verhalten noch Produktionswirkung.
15. **Methodengrenzen offenlegen:** Jeder Bericht nennt, was nicht geprüft wurde und welche
    Schlussfolgerungen deshalb nicht gezogen werden dürfen.
16. **Keine Handoff-Leaks:** Veröffentlichbare Berichte enthalten weder `.handoff` noch interne
    Snapshot-, Prompt-, Raw- oder Telemetriepfade. Hash und öffentliche Quellenbezeichnung genügen.
17. **Auswerter ist kein Mehrheitsrichter:** Jede Entscheidung bindet Claim, Gegenprobe und
    Ground Truth; Modellübereinstimmung allein trägt keine Übernahme.
18. **Auswertung und Revision trennen:** Der Auswerter schreibt den Revisionsvertrag, nicht die
    neue Dokumentfassung. Der Reviser darf keine neuen Sachentscheidungen hinzufügen.

## Ablauf

### 1. Ziel und Repository bestimmen

- Zielpfad auflösen und Existenz prüfen.
- Mit `git -C <zielordner> rev-parse --show-toplevel` das Repository bestimmen.
- `git status --short`, Branch und `HEAD` erfassen.
- Relevante Geschwister-Repositories nur aufnehmen, wenn das Dokument sie berührt.
- Bestehende `*review-judge*.md` inventarisieren, aber nicht als Ground Truth verwenden.

**Fertig, wenn:** Zielpfad, Repo-Root, HEAD, Branch und vorhandene Zielartefakte bekannt sind.

### 2. Bytes und Refs einfrieren

- Quelldatei bytegleich nach `<handoff>/input/<basis>.<kurzhash>.md` kopieren.
- SHA-256, Bytezahl und Zeilenzahl erfassen.
- Entscheidungsrelevante Repo-Refs mit vollständiger SHA pinnen.
- Beide Prompts lesen Dokumenttext und Dokumentzeilen nur aus dem Snapshot.
- Livepfad dient nur als Provenienz und wird vor Publikation erneut gehasht.

Ein Hash ohne Snapshot friert keine veränderliche Datei ein.

**Fertig, wenn:** Snapshot und Hash erneut verifiziert sind und verwendete Refs feststehen.

### 3. Gemeinsamen Prüfvertrag schreiben

Aus `templates/judge-prompt.md` zwei Prompts erzeugen und alle Platzhalter ersetzen. Beide enthalten:

- Zweck und Artefaktklasse (primär Plan, Implementierung oder Sachverhaltsdarstellung);
- Snapshotpfad und SHA-256 als interne Eingabe;
- eine öffentliche Quellenbezeichnung ohne `.handoff` für sämtliche Berichtsnennungen;
- Originalpfad nur als interne Provenienz;
- ausdrückliches Verbot, Snapshot-, Prompt-, Raw-, Telemetrie- oder andere Handoff-Pfade in der
  finalen Markdown-Ausgabe wiederzugeben;
- Repo-Root und fixe Refs;
- Ausschlüsse, insbesondere bestehende Judge-Berichte;
- adversariales Ziel und tragende Fragen;
- Evidenzpflicht `path:line`, bei Historie refqualifiziert;
- Trennung von Codebeleg, Test, Laufzeitbeleg und Annahme;
- mechanische Nachrechnung von Zahlen;
- `UNBEKANNT` statt Raten;
- identische Überschriften und Urteilssemantik;
- eine Claim-Matrix für tragende Aussagen mit stabilen IDs, Belegstatus, Zeitstand und
  Entscheidungsauswirkung;
- eine explizite Methodengrenze: ausgeführte und nicht ausgeführte Prüfarten;
- eine Trennung von offenen Entscheidungen, technischen Bauaufgaben und reinen Verifikationsgates.

Bei Revisionen wählen: **frische Challenge** mit Verbot alter Reviews oder **Closure-Review** mit
Closure-Matrix. Nicht vermischen.

**Fertig, wenn:** Ein Diff nur Judge-ID und Titel als sachliche Unterschiede zeigt.

### 4. Preflight

- `codex --version` und `claude --version` erfassen.
- **Windows-Capability-Auswahl:** Der SOL-Runner prüft vor jedem Lauf zuerst, ob WSL, eine
  erreichbare Distribution, ein gemappter Repository-/Promptpfad, Node (einschließlich NVM) und
  natives Linux-Codex verfügbar sind. Bei vollständiger Capability läuft SOL direkt in WSL mit der
  Linux-Read-only-Sandbox; andernfalls verwendet er natives Windows-Codex.
- Die Pfadabbildung erfolgt über `WSLENV`/WSL-Pfadtranslation, nicht durch fest verdrahtetes
  Ersetzen von Laufwerksbuchstaben. `SOL_WSL_DISTRO` darf optional eine Distribution festlegen.
- Sobald WSL ausgewählt ist, führt ein Auth-, Provider-, Modell-, Effort- oder Preflightfehler zum
  harten Abbruch. Nach einem solchen Laufzeitfehler niemals still auf natives Windows wechseln.
- Weder im WSL- noch im nativen Pfad ist ein automatischer
  `dangerously-bypass-approvals-and-sandbox`-Fallback zulässig.
- SOL über exakt den späteren Providerpfad, den Modellnamen `gpt-5.6-sol` und
  `model_reasoning_effort=max` smoke-testen.
- Der SOL-Runner führt diesen Smoke-Test bei jedem Aufruf unmittelbar vor dem eigentlichen
  Judge-Lauf selbst aus. Ein früherer erfolgreicher Test oder ein Modellkatalog ersetzt ihn nicht.
- Der Smoke-Test muss einen terminal abgeschlossenen Codex-Turn und den exakten Marker
  `SOL_MAX_AVAILABLE` liefern. Auth-, Provider-, Rollout-, Quota-, Modell- und Effortfehler brechen den
  SOL-Pfad vor dem Judge-Prompt ab.
- Bei nicht verfügbarem SOL/max nicht still auf einen schwächeren Effort oder ein anderes Modell
  fallen. Nur nach ausdrücklicher Nutzerfreigabe mit offengelegter Ersatzbesetzung neu starten.
- Fable-Alias live testen; `fable-5` nicht dauerhaft als gültig annehmen.
- Canonical Model aus strukturierter Telemetrie erfassen.
- Eigene Skripte dieses Skills auf Vorhandensein prüfen.

```bash
CODEX_MODEL=gpt-5.6-sol CODEX_REASONING_EFFORT=max bash scripts/run-sol-judge.sh \
  <repo-root> <prompt-a.md> <staging-a.md>

FABLE_MODEL=fable bash scripts/run-fable-judge.sh \
  <prompt-b.md> <staging-b.md>
```

Unter Windows ist WSL bei vollständiger Capability der Primärpfad und kein Fehler-Fallback. Fehlt
WSL, Node oder natives Linux-Codex bereits im Capability-Check, darf der Runner natives
Windows-Codex mit normaler Read-only-Sandbox verwenden. Scheitert dagegen ein bereits ausgewählter
WSL-Pfad oder die native Windows-Sandbox beim Preflight, Output archivieren und hart abbrechen;
keinen Sandbox-Bypass starten und fehlgeschlagene Checks nie als ausgeführt umformulieren.

**Fertig, wenn:** Beide Modellpfade strukturiert abgeschlossene Smoke-Tests liefern, unter Windows
die gewählte Ausführungsumgebung (`wsl` oder `native`) samt Capability-Status in der Telemetrie
steht und der SOL/max-Preflight zum unmittelbar folgenden Judge-Aufruf gehört.

### 5. Judges parallel starten

Beide dürfen parallel laufen, sobald Snapshot, Refs und Prompts eingefroren sind. Jeder schreibt in
eigene Staging-, Raw- und Metrics-Dateien. Kein Prozess publiziert direkt neben das Zieldokument.
Fehlversuche bleiben archiviert; Retries starten frisch.

**Fertig, wenn:** Beide Prozesse terminal abgeschlossen oder Ausfälle ausdrücklich dokumentiert sind.

### 6. Berichte validieren

```bash
python scripts/validate-report.py \
  --report <staging.md> \
  --title '# <Dokumenttyp>-Challenge — Judge A' \
  --source <snapshot.md> \
  --metrics <staging.md.metrics.json> \
  --expected-provider <provider> \
  --expected-requested-model <canonical-model>
```

Für Spuren mit verlässlicher beobachteter Modell- oder Thread-Telemetrie zusätzlich
`--expected-observed-model <model>` beziehungsweise `--require-thread-id` setzen. Zugesicherte
Telemetriefelder werden wiederholbar mit `--require-metric <feld>` gegated. Ein angefordertes
Modell wird nie als beobachtetes Modell ausgegeben, wenn der Rawstream das nicht selbst belegt.

Zusätzlich prüfen:

- genau ein erkennbarer Bericht-H1 und alle Pflichtabschnitte;
- kein Treffer für `.handoff` (case-insensitive) und kein interner Snapshot-, Prompt-, Raw- oder
  Telemetriepfad im Bericht;
- jede in der Claim-Matrix geführte tragende Aussage hat Belegstatus, Zeitstand/Ref,
  Gegenprüfung und Auswirkung;
- Angaben wie „gebaut“, „gemergt“, „live“, „produktiv“, „vollständig“ oder „getestet“ werden nur
  übernommen, wenn die jeweils behauptete Stufe tatsächlich belegt ist;
- offene Entscheidungen werden nicht als technische Tasks oder scheinbar geschätzter Aufwand
  ausgegeben;
- der Abschnitt `Grenzen der Methode` widerspricht keiner stärkeren Behauptung im Bericht;
- substanzieller Inhalt ohne Klartext-Toolcalls, Arbeitsnotizen oder automatische Fußzeilen;
- keine Secrets oder langen Credentialwerte;
- entscheidungsändernde Zahlen, Summen und Hashes nachgerechnet;
- `path:line`-Anker existieren am genannten Ref;
- Toolfehler/Permission-Denials widersprechen keinem behaupteten Beleg;
- Fable-Telemetrie nennt canonical Hauptmodell; Hilfsmodelle offenlegen, nicht als Stimme zählen;
- SOL-Telemetrie bestätigt abgeschlossenen frischen Thread sowie Ausführungsumgebung und
  Capability-Status; ein WSL-Lauf nennt zusätzlich Distribution, Kernel, Node-, Codex-Version und
  gemappten Repositorypfad.

Wenn nur Markdown verlangt wurde, darf ein kurzer Vorspann mechanisch vor dem einzigen H1 entfernt
und nur die H1 normalisiert werden. Rawoutput bewahren und Bereinigung offenlegen. Findings,
Severity und Body nie redaktionell ändern. Bei fehlendem/mehrdeutigem H1 oder explizitem
Byte-exakt-Vertrag frisch wiederholen.

**Fertig, wenn:** Beide Berichte gültig und empfehlungsändernde mechanische Claims reproduziert sind.

### 6a. Optional auswerten und konsolidieren

Nur bei `mode: consolidate`:

1. Tragende Judge-Claims atomisieren und anhand von Gegenstand, Fundstelle und Evidenzausschnitt
   deduplizieren; unterschiedliche Reichweiten nicht zusammenziehen.
2. Herkunft und Modellnamen entfernen. Der Auswerter erhält den Original-Snapshot, fixe Refs,
   beide anonymisierten Berichte und die reproduzierten Runner-Belege.
3. Mit `templates/consolidation-evaluator-prompt.md` jeden Claim einstufen:
   `ÜBERNEHMEN | PRÄZISIEREN | VERWERFEN | UNBEKANNT | WIDERSPRUCH_OFFEN`.
4. Jede Einstufung nennt Ground-Truth-Beleg, Gegenprobe, Methodengrenze und konkrete
   Änderungsauswirkung. Fehlende oder gescheiterte Evidenz darf keinen Claim freigeben.
5. Der Runner reproduziert alle inhaltlich wirksamen Entscheidungen und friert danach
   `<basis>-revision-contract.md` samt Hash ein.
6. Ein frischer Reviser erhält mit `templates/reviser-prompt.md` nur Original-Snapshot und
   Revisionsvertrag. Er erzeugt `<basis>-v<N>.md` und `<basis>-v<N>.changes.json`; neue Findings oder
   eigenständige Umdeutungen sind unzulässig.
7. `scripts/validate-revision.py` spielt jede exakte Ersetzung aus dem Mapping auf dem Original nach.
   Nur wenn das Byteergebnis der neuen Version entspricht, alle Hashes stimmen und jede Claim-ID in
   einer `BESTÄTIGT`-Vertragszeile mit `ÜBERNEHMEN` oder `PRÄZISIEREN` steht, ist der Delta-Check
   bestanden. Nicht zuordenbare Änderungen blockieren die Publikation.

```bash
python scripts/validate-revision.py \
  --original <snapshot.md> \
  --revised <basis-vN.md> \
  --contract <basis-revision-contract.md> \
  --mapping <basis-vN.changes.json>
```

**Fertig, wenn:** Evaluation und Revisionsvertrag gehasht, alle tragenden Entscheidungen vom Runner
reproduziert und jede Änderung der neuen Version vollständig auf den Vertrag zurückgeführt ist.

### 7. Publizieren

- Livequelle erneut hashen.
- Beide freigegebenen Stagingberichte unmittelbar vor dem Kopieren erneut auf `.handoff` und
  interne Handoff-Pfade prüfen; bei jedem Treffer Publikation abbrechen und den betroffenen Judge
  frisch mit korrigiertem Prompt wiederholen. Findings nicht nachträglich umschreiben.
- Bei gleichem Hash normal publizieren.
- Bei geändertem Hash: eingefrorenen Stand kenntlich machen oder bei gewünschter aktueller Revision
  beide Berichte verwerfen, neu einfrieren und neu laufen.
- Stagingtexte als UTF-8/LF in die zwei Ziele schreiben.
- Ziel und Staging per SHA-256/Textgleichheit vergleichen.
- Anschließend alle veröffentlichten `*review-judge*.md` im Zielverzeichnis case-insensitive auf
  `.handoff` prüfen. Der Abschluss ist nur bei null Treffern zulässig; bestehende Fremdtreffer nicht
  still ändern, sondern offenlegen und vor Freigabe bereinigen lassen. Die geprüfte Quelldatei ist
  von diesem Scan ausgenommen, weil sie interne Handoff-Mechanik selbst dokumentieren kann.
- Prüfen, dass Quelle und fremde Dateien unverändert blieben.

**Fertig, wenn:** Beide Ziele validiert und mit freigegebenem Staging identisch sind.

### 8. Abschluss berichten

Nennen: Zielpfade, Judge-/Modellzuordnung, canonical models, jeweiliges Gesamturteil, zentrale
Übereinstimmungen, Dissens, Quellhash, Berichtshashes, Retries, Titelbereinigungen,
Hilfsmodellnutzung, SOL-Ausführungsumgebung (`wsl`/`native`) samt Capability-/Versionsdaten und
`UNBEKANNT` gebliebene Prüfungen. Keine Synthese erfinden.

## Berichtsschema

```text
# <Artefakt>-Challenge — Judge <A|B>

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
```

Die Claim-Matrix enthält mindestens:

```text
| ID | Tragende Aussage | Belegstatus | Stand/Ref | Gegenprüfung | Auswirkung |
```

Belegstatus: `BELEGT`, `PLAUSIBEL`, `UNBEKANNT`, `WIDERSPRUCH`.

Die Abschnitte zu Abhängigkeiten/Gates und Scope dürfen bei einem nachweislich nicht einschlägigen
Artefakt knapp `NICHT EINSCHLÄGIG` ausweisen, aber nicht still fehlen.

Urteilsskala: `TRÄGT`, `TRÄGT MIT ÄNDERUNGEN`, `NICHT BELASTBAR`, `WIDERLEGT`, `UNBEKANNT`.

## Konsolidierungsschema

`<basis>-review-evaluation.md` enthält mindestens:

```text
# Konsolidierte Auswertung
## Eingefrorener Stand und Hashes
## Anonyme Claim-Matrix
## Evidenzbasierte Entscheidungen
## Offener Dissens / UNBEKANNT
## Revisionsvertrag
## Methodengrenzen
```

Der Revisionsvertrag enthält je Änderung:

```text
| Claim | Disposition | Quellabschnitt | Zieländerung | Ground Truth | Runner-Gate |
```

## Artefaktspezifische Prüfdimensionen

### Pläne

- Ist der Ausgangsstand korrekt und auf feste Refs sowie Prüfdaten bezogen?
- Sind Schritte vollständig, in ausführbarer Reihenfolge und mit klaren Gates beschrieben?
- Ist jede Kante eine belegte Vorher-Nachher-Beziehung oder nur eine plausible Annahme?
- Gelten Gates global oder je Service/Teilprodukt, und serialisiert der Plan unabhängige Stränge
  unnötig hintereinander?
- Stimmen Abhängigkeiten, Verantwortlichkeiten, Rollback und Abbruchbedingungen?
- Sind offene Entscheidungen als Entscheidungen markiert oder fälschlich in Baupaketen verborgen?
- Widersprechen sich Zielbild, CI/CD-Reihenfolge, Freigaberegeln oder Betriebsmodell?
- Sind Verifikation, Observability und Definition of Done konkret genug?
- Welche Produktflächen, Kategorien, Repositories oder Konsumenten besitzen keine Programmheimat,
  keinen Owner oder keinen tragenden Planschritt?
- Wird Aufwand mit Durchlaufzeit vermischt oder werden relative Klassen unzulässig addiert?

### Implementierungen und Umsetzungsberichte

- Existiert die behauptete Funktion tatsächlich im Code und auf dem genannten Ref?
- Sind alle Konsumenten, Call Paths, Fehlerpfade und Seiteneffekte berücksichtigt?
- Decken Tests die behauptete Semantik oder nur einen Happy Path ab?
- Stimmen Dokumentation, Typverträge, Runtime-Verhalten, Konfiguration und Deployment überein?
- Werden `implementiert`, `gemergt`, `deployed`, `live` und `verhaltensgeprüft` als verschiedene
  Nachweisstufen behandelt?
- Ist die Implementierung nur vorhanden oder auch über reale Principal-, Mandanten-, Fehler- und
  Nebenläufigkeitspfade geprüft?
- Werden Zielzustand und bereits nachgewiesener Istzustand sauber getrennt?

### Sachverhaltsdarstellungen und Bewertungen

- Tragen Quellen und Berechnungen jede entscheidungsrelevante Aussage?
- Sind Ursache, Korrelation, Möglichkeit und gemessene Wirkung getrennt?
- Sind absolute Negativ- oder Vollständigkeitsbehauptungen reproduzierbar?
- Werden Gegenbeispiele, alternative Erklärungen und unbekannte Randbedingungen sichtbar?
- Folgt die Empfehlung tatsächlich aus dem belegten Sachverhalt?

### Aufwandsschätzungen (Sonderfall)

Jede Summe und Bandbreite nachrechnen; Scope/Nicht-Scope, Abhängigkeiten,
Parallelisierbarkeit, Kalenderzeit und Reserve ohne Doppelzählung prüfen; eigene Bandbreite nur aus
Ground Truth herleiten.

## Technische Eigenständigkeit

```text
SKILL.md
templates/judge-prompt.md
templates/consolidation-evaluator-prompt.md
templates/reviser-prompt.md
scripts/run-sol-judge.sh
scripts/run-sol-codex-wsl.sh
scripts/run-fable-judge.sh
scripts/check-codex-preflight.py
scripts/parse-agent-output.py
scripts/validate-report.py
scripts/validate-revision.py
```

Keine Datei importiert oder referenziert einen anderen Skill.

## Häufige Fehler

1. Live-Datei trotz Hash lesen → Snapshot als einzige Dokumentquelle.
2. Fable-Alias fest annehmen → Smoke-Test und canonical `modelUsage`.
3. Alte Judge-Berichte zulassen → Namensmuster ausdrücklich ausschließen.
4. Direkt publizieren → Raw → Parse → Stage → Validate → Publish.
5. Windows-Sandboxfehler ignorieren → Bericht ungültig behandeln.
6. Fable-Hilfsmodell als Stimme zählen → nur als Telemetrie offenlegen.
7. Runner wird dritter Judge → nur objektive Claims reproduzieren.
8. Dissens glätten → unverändert ausliefern.
9. Ungetrackte Quelle ändert sich → bei „aktuellste Revision“ beide neu starten.
10. Fremde Änderungen beanspruchen → Status vorher/nachher vergleichen.
11. SOL/max nur aus Katalog/Alt-Lauf ableiten → bei jedem Runner-Aufruf live preflighten und bei
    Fehlschlag ohne stillen Fallback abbrechen.
12. Internen Snapshotpfad als Provenienz abdrucken → öffentliche Quellenbezeichnung verwenden;
    Validator muss jeden `.handoff`-Treffer vor Publikation ablehnen.
13. Unter Windows immer natives Codex zuerst starten → zuerst WSL-, Node-, Codex- und Pfad-
    Capabilities prüfen; bei Erfolg WSL als Primärpfad wählen.
14. Nach WSL-Preflightfehler auf Windows oder Sandbox-Bypass wechseln → hart abbrechen; nur ein
    fehlender Capability-Check vor dem Providerlauf erlaubt den normalen nativen Windows-Pfad.
15. Judges direkt zu einer Mischfassung auffordern → erst anonym auswerten, dann separaten Reviser
    ausschließlich gegen den eingefrorenen Revisionsvertrag ausführen.
16. Unbekannten Dissens sprachlich glätten → als `UNBEKANNT` oder `WIDERSPRUCH_OFFEN` erhalten.

## Verifikationscheckliste

- [ ] Ziel, Repo, Branch, HEAD und Ausgangsstatus erfasst.
- [ ] Bytegleicher Snapshot mit SHA-256, Byte- und Zeilenzahl vorhanden.
- [ ] Prompts unterscheiden sich sachlich nur in Judge-ID und H1.
- [ ] Alte Judge-Berichte sind für frische Challenges ausgeschlossen.
- [ ] SOL mit Reasoning-Effort `max` und Fable liefen frisch und isoliert.
- [ ] Unter Windows wurde die WSL-Capability vor dem SOL-Preflight geprüft; bei vorhandener WSL-,
      Node-, Codex- und Pfad-Capability lief SOL direkt in WSL.
- [ ] SOL-Telemetrie nennt Ausführungsumgebung und Capability-Status; bei WSL zusätzlich
      Distribution, Kernel, Node-, Codex-Version und gemappten Repo-Pfad.
- [ ] Kein SOL-Lauf verwendete einen automatischen Sandbox-Bypass oder wechselte nach einem
      WSL-Provider-/Auth-/Modell-/Effortfehler still auf Windows.
- [ ] SOL/max-Preflight lief unmittelbar davor über denselben Modell- und Providerpfad erfolgreich.
- [ ] Beide lasen denselben Snapshot und dieselben Refs.
- [ ] Rawoutput/Telemetrie liegen nur im Handoff.
- [ ] Canonical models und terminaler Abschluss geprüft.
- [ ] Titel, Pflichtabschnitte, Substanz und Secretfreiheit validiert.
- [ ] Beide Staging- und Zielberichte enthalten weder `.handoff` noch interne Handoff-Pfade.
- [ ] Der abschließende case-insensitive Scan aller veröffentlichten `*review-judge*.md` im
      Zielverzeichnis liefert null `.handoff`-Treffer; die Quelldatei ist ausgenommen.
- [ ] Entscheidungsändernde Zahlen, Hashes und Anker reproduziert.
- [ ] Quelle vor Publikation erneut gehasht.
- [ ] Zielberichte sind mit freigegebenem Staging identisch.
- [ ] Quelle und fremde Änderungen blieben unangetastet.
- [ ] Übereinstimmungen und Dissens ohne Synthese berichtet.
- [ ] Bei `challenge-only` existiert weder Evaluation noch automatisch erzeugte Revision.
- [ ] Bei `consolidate` ist jede Auswerterentscheidung an reproduzierte Ground Truth gebunden.
- [ ] Auswerter und Reviser liefen in getrennten frischen Prozessen.
- [ ] Jede materielle Änderung der neuen Version ist einer freigegebenen Vertragszeile zugeordnet.
