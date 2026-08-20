from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED_SKILLS = {
    "ootbt-dual-judge-markdown-review",
    "ootbt-ticket-technical-ak-review",
}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".yml", ".yaml", ".txt", ""}

FORBIDDEN = {
    "absolute Windows user path": re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s]+"),
    "absolute Unix user path": re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/"),
    "private IPv4 address": re.compile(
        r"(?<!\d)(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?!\d)"
    ),
    "credential-shaped token": re.compile(
        r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|glpat-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})"
    ),
    "credential assignment": re.compile(
        r"(?i)(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*['\"][^'\"<>\s]{12,}['\"]"
    ),
    "hardcoded Ollama provider": re.compile(r"(?<!<)\b[A-Za-z][A-Za-z0-9_-]*-ollama/"),
    "local endpoint": re.compile(r"(?i)https?://(?:localhost|127\.0\.0\.1|[^\s/]+\.local)(?::\d+)?"),
}

REQUIRED_FILES = {
    "ootbt-dual-judge-markdown-review": {
        "SKILL.md",
        "templates/judge-prompt.md",
        "templates/consolidation-evaluator-prompt.md",
        "templates/reviser-prompt.md",
        "scripts/run-sol-judge.sh",
        "scripts/run-sol-codex-wsl.sh",
        "scripts/run-fable-judge.sh",
        "scripts/check-codex-preflight.py",
        "scripts/parse-agent-output.py",
        "scripts/validate-report.py",
        "scripts/validate-revision.py",
    },
    "ootbt-ticket-technical-ak-review": {
        "SKILL.md",
        "references/tracker-adapters.md",
        "templates/criterion-review-prompt.md",
        "templates/ak-disposition-prompt.md",
    },
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def frontmatter(text: str, path: Path, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        fail(errors, f"{path}: frontmatter must begin at byte 0")
        return {}
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        fail(errors, f"{path}: frontmatter is not closed")
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line and not line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []
    private_markers = {
        marker.strip().casefold()
        for marker in os.environ.get("PUBLICATION_DENYLIST", "").split(",")
        if marker.strip()
    }
    if not (ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"):
        fail(errors, "LICENSE is not MIT")

    skill_dirs = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    if skill_dirs != EXPECTED_SKILLS:
        fail(errors, f"skill directories differ: {sorted(skill_dirs)}")

    for skill, required in REQUIRED_FILES.items():
        root = SKILLS / skill
        actual = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        }
        missing = required - actual
        if missing:
            fail(errors, f"{skill}: missing required files {sorted(missing)}")
        if any(
            part == ".handoff"
            for path in root.rglob("*")
            for part in path.relative_to(root).parts
        ):
            fail(errors, f"{skill}: nested .handoff content is forbidden")

        skill_file = root / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        fm = frontmatter(text, skill_file.relative_to(ROOT), errors)
        if fm.get("name") != skill:
            fail(errors, f"{skill}: frontmatter name mismatch")
        if not fm.get("description", "").startswith("Use "):
            fail(errors, f"{skill}: description must start with 'Use '")
        if len(fm.get("description", "")) > 1024:
            fail(errors, f"{skill}: description exceeds 1024 characters")
        if fm.get("license") != "MIT":
            fail(errors, f"{skill}: license must be MIT")
        if len(text) > 100_000:
            fail(errors, f"{skill}: SKILL.md exceeds 100000 characters")

    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            fail(errors, f"{path.relative_to(ROOT)}: symlinks are forbidden")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            fail(errors, f"{path.relative_to(ROOT)}: unexpected non-text file")
            continue
        text = path.read_text(encoding="utf-8")
        scanned += 1
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                fail(errors, f"{path.relative_to(ROOT)}: {label}")
        folded = text.casefold()
        for marker in private_markers:
            if marker in folded:
                fail(errors, f"{path.relative_to(ROOT)}: denylisted private marker")

    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    for path in ROOT.rglob("*.sh"):
        completed = subprocess.run(
            ["bash", "-n"],
            input=path.read_bytes(),
            capture_output=True,
        )
        if completed.returncode:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            fail(errors, f"{path.relative_to(ROOT)}: bash -n failed: {stderr}")

    if errors:
        print("PUBLICATION VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLICATION VALIDATION: PASS")
    print(f"skills={len(EXPECTED_SKILLS)} files_scanned={scanned}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
