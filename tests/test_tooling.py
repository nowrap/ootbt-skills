from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "ootbt-dual-judge-markdown-review" / "scripts"


class ToolingSmokeTest(unittest.TestCase):
    @staticmethod
    def valid_report() -> str:
        sections = [
            ("## Gesamturteil", "TRÄGT"),
            ("## Tragende Befunde", "Keine blockierenden Befunde."),
            (
                "## Claim-Matrix",
                "| ID | Tragende Aussage | Belegstatus | Stand/Ref | Gegenprüfung | Auswirkung |\n"
                "|---|---|---|---|---|---|\n"
                "| C1 | Aussage | BELEGT | ref | geprüft | keine |",
            ),
            ("## Detailprüfung der Behauptungen", "C1 wurde gegen die Quelle geprüft."),
            ("## Abhängigkeiten, Gates und offene Entscheidungen", "Keine."),
            ("## Scope-Abdeckung und nicht zugeordnete Flächen", "Der definierte Scope ist abgedeckt."),
            ("## Risiken, Lücken und Widersprüche", "Keine bekannten Widersprüche."),
            ("## Konkrete Korrekturen vor Freigabe", "Keine erforderlich."),
            ("## Belege und durchgeführte Prüfungen", "Quelle und Gegenprobe wurden gelesen."),
            (
                "## Grenzen der Methode",
                "Diese synthetische Prüfung belegt ausschließlich das Validatorschema und keine "
                "fachliche Aussage über ein reales Dokument oder Repository.",
            ),
            ("## Offene Punkte / UNBEKANNT", "Keine."),
        ]
        filler = "\n\n" + ("Reproduzierbarer neutraler Testinhalt. " * 40)
        return "# Test-Challenge — Judge A\n\n" + "\n\n".join(
            f"{heading}\n\n{body}" for heading, body in sections
        ) + filler + "\n"

    def test_codex_preflight_accepts_completed_exact_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "preflight.jsonl"
            raw.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "agent_message",
                                    "text": "SOL_MAX_AVAILABLE",
                                },
                            }
                        ),
                        json.dumps({"type": "turn.completed"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPTS / "check-codex-preflight.py"), str(raw)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_codex_parser_writes_report_and_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw.jsonl"
            report = root / "report.md"
            metrics = root / "metrics.json"
            raw.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "thread.started", "thread_id": "test-thread"}),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {"type": "agent_message", "text": "# Review\n\nOK"},
                            }
                        ),
                        json.dumps(
                            {
                                "type": "turn.completed",
                                "usage": {
                                    "input_tokens": 10,
                                    "cached_input_tokens": 3,
                                    "output_tokens": 2,
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "parse-agent-output.py"),
                    "codex",
                    str(raw),
                    str(report),
                    str(metrics),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(report.read_text(encoding="utf-8"), "# Review\n\nOK\n")
            parsed = json.loads(metrics.read_text(encoding="utf-8"))
            self.assertEqual(parsed["thread_id"], "test-thread")
            self.assertEqual(parsed["input_tokens"], 7)
            self.assertEqual(parsed["cached_input_tokens"], 3)
            self.assertEqual(parsed["output_tokens"], 2)
            self.assertTrue(parsed["terminal_completion"])

    def test_report_validator_enforces_contract_and_permission_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            source = root / "source.md"
            metrics = root / "metrics.json"
            report.write_text(self.valid_report(), encoding="utf-8")
            source.write_text("source\n", encoding="utf-8")
            base_metrics = {
                "terminal_completion": True,
                "provider": "test-provider",
                "requested_model": "test-model",
                "model": "observed-model",
                "thread_id": "thread-1",
                "permission_denials": [],
            }
            metrics.write_text(json.dumps(base_metrics), encoding="utf-8")
            command = [
                sys.executable,
                str(SCRIPTS / "validate-report.py"),
                "--report", str(report),
                "--title", "# Test-Challenge — Judge A",
                "--source", str(source),
                "--metrics", str(metrics),
                "--expected-provider", "test-provider",
                "--expected-requested-model", "test-model",
                "--expected-observed-model", "observed-model",
                "--require-thread-id",
            ]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            base_metrics["permission_denials"] = ["denied"]
            metrics.write_text(json.dumps(base_metrics), encoding="utf-8")
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 64)
            self.assertIn("permission denials", rejected.stderr)

    def test_revision_validator_replays_only_confirmed_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original.md"
            revised = root / "revised.md"
            contract = root / "contract.md"
            mapping = root / "changes.json"
            original.write_text("Alpha old Omega\n", encoding="utf-8")
            revised.write_text("Alpha new Omega\n", encoding="utf-8")
            contract.write_text(
                "| Claim | Disposition | Runner-Gate |\n"
                "|---|---|---|\n"
                "| C-001 | ÜBERNEHMEN | BESTÄTIGT |\n",
                encoding="utf-8",
            )

            def sha(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()

            payload = {
                "original_sha256": sha(original),
                "contract_sha256": sha(contract),
                "revised_sha256": sha(revised),
                "changes": [
                    {"claim_id": "C-001", "old_text": "old", "new_text": "new"}
                ],
            }
            mapping.write_text(json.dumps(payload), encoding="utf-8")
            command = [
                sys.executable,
                str(SCRIPTS / "validate-revision.py"),
                "--original", str(original),
                "--revised", str(revised),
                "--contract", str(contract),
                "--mapping", str(mapping),
            ]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            revised.write_text("Alpha new Omega\nUnmapped.\n", encoding="utf-8")
            payload["revised_sha256"] = sha(revised)
            mapping.write_text(json.dumps(payload), encoding="utf-8")
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 64)
            self.assertIn("do not equal revised document", rejected.stderr)

            original.write_bytes(b"Alpha\r\n")
            revised.write_bytes(b"Alpha\n")
            payload = {
                "original_sha256": sha(original),
                "contract_sha256": sha(contract),
                "revised_sha256": sha(revised),
                "changes": [],
            }
            mapping.write_text(json.dumps(payload), encoding="utf-8")
            newline_bypass = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(newline_bypass.returncode, 64)
            self.assertIn("do not equal revised document", newline_bypass.stderr)

    def test_publication_validator_ignores_generated_pycache(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "validate_publication.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
