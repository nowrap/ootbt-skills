#!/usr/bin/env python
"""Prove that a revised document consists only of contract-authorized replacements."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ACCEPTED = ("ÜBERNEHMEN", "PRÄZISIEREN")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    parser.add_argument("--revised", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--mapping", required=True)
    args = parser.parse_args()

    paths = {name: Path(getattr(args, name)) for name in ("original", "revised", "contract", "mapping")}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        print(f"ERROR: missing files: {', '.join(missing)}", file=sys.stderr)
        return 64

    try:
        mapping = json.loads(paths["mapping"].read_text(encoding="utf-8", errors="strict"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invalid mapping JSON: {error}", file=sys.stderr)
        return 64
    if not isinstance(mapping, dict) or not isinstance(mapping.get("changes"), list):
        print("ERROR: mapping must be an object with a changes array", file=sys.stderr)
        return 64

    expected_hashes = {
        "original_sha256": digest(paths["original"]),
        "contract_sha256": digest(paths["contract"]),
        "revised_sha256": digest(paths["revised"]),
    }
    errors: list[str] = []
    for field, expected in expected_hashes.items():
        if mapping.get(field) != expected:
            errors.append(f"{field} mismatch")

    contract = paths["contract"].read_text(encoding="utf-8", errors="strict")
    current = paths["original"].read_bytes()
    seen: set[str] = set()
    for index, change in enumerate(mapping["changes"], 1):
        if not isinstance(change, dict):
            errors.append(f"change {index} is not an object")
            continue
        claim = change.get("claim_id")
        old = change.get("old_text")
        new = change.get("new_text")
        if not all(isinstance(value, str) for value in (claim, old, new)):
            errors.append(f"change {index} fields must be strings")
            continue
        if not claim or not old or old == new:
            errors.append(f"change {index} has empty/identity values")
            continue
        if claim in seen:
            errors.append(f"duplicate claim_id: {claim}")
        seen.add(claim)
        contract_lines = [line for line in contract.splitlines() if re.search(rf"(?<![\w-]){re.escape(claim)}(?![\w-])", line)]
        if not contract_lines or not any(
            any(disposition in line for disposition in ACCEPTED) and "BESTÄTIGT" in line
            for line in contract_lines
        ):
            errors.append(f"claim is not confirmed in contract: {claim}")
            continue
        old_bytes = old.encode("utf-8")
        new_bytes = new.encode("utf-8")
        occurrences = current.count(old_bytes)
        if occurrences != 1:
            errors.append(f"change {index} old_text occurrences: {occurrences}")
            continue
        current = current.replace(old_bytes, new_bytes, 1)

    revised = paths["revised"].read_bytes()
    if current != revised:
        errors.append("replayed replacements do not equal revised document")
    if not mapping["changes"] and current != revised:
        errors.append("changed document has no mapped changes")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 64

    print(
        json.dumps(
            {
                "valid": True,
                "changes": len(mapping["changes"]),
                **expected_hashes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
