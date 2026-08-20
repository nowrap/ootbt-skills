#!/usr/bin/env python
"""Validate that a Codex model smoke test completed with the expected marker."""
from __future__ import annotations

import json
import sys
from pathlib import Path

MARKER = "SOL_MAX_AVAILABLE"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-codex-preflight.py <raw-jsonl>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    completed = False
    messages: list[str] = []

    try:
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="strict").splitlines(), 1
        ):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL line {number}: {error}") from error
            if not isinstance(row, dict):
                continue
            if row.get("type") == "turn.completed":
                completed = True
            item = row.get("item") if isinstance(row.get("item"), dict) else {}
            if (
                row.get("type") == "item.completed"
                and item.get("type") == "agent_message"
                and isinstance(item.get("text"), str)
            ):
                messages.append(item["text"])
    except (OSError, ValueError) as error:
        print(f"ERROR: SOL preflight unreadable: {error}", file=sys.stderr)
        return 64

    if not completed:
        print("ERROR: SOL preflight has no turn.completed event", file=sys.stderr)
        return 65
    if not messages or messages[-1].strip() != MARKER:
        print("ERROR: SOL preflight returned no exact availability marker", file=sys.stderr)
        return 66
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
