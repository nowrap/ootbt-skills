#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 2 ]; then echo "Usage: $0 <prompt-file> <result-file>" >&2; exit 2; fi
PROMPT="$1"; RESULT="$2"; MODEL="${FABLE_MODEL:-fable}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PARSER="$DIR/parse-agent-output.py"
if command -v cygpath >/dev/null 2>&1; then PARSER_FOR_PYTHON="$(cygpath -w "$PARSER")"; else PARSER_FOR_PYTHON="$PARSER"; fi
RAW="$RESULT.raw.json"; METRICS="$RESULT.metrics.json"
if command -v cygpath >/dev/null 2>&1; then
  RAW_FOR_PYTHON="$(cygpath -w "$RAW")"
  RESULT_FOR_PYTHON="$(cygpath -w "$RESULT")"
  METRICS_FOR_PYTHON="$(cygpath -w "$METRICS")"
else
  RAW_FOR_PYTHON="$RAW"
  RESULT_FOR_PYTHON="$RESULT"
  METRICS_FOR_PYTHON="$METRICS"
fi
[ -f "$PROMPT" ] || { echo "ERROR: prompt missing: $PROMPT" >&2; exit 2; }
command -v claude >/dev/null || { echo "ERROR: claude missing" >&2; exit 2; }
command -v python >/dev/null || { echo "ERROR: python missing" >&2; exit 2; }
mkdir -p "$(dirname "$RESULT")"; rm -f "$RESULT" "$RAW" "$METRICS"
TITLE="${EXPECTED_TITLE:-# Markdown-Challenge — Judge B}"
if command -v cygpath >/dev/null 2>&1; then
  SHELL_TOOL="PowerShell"
  FORBIDDEN_SHELL="Bash"
else
  SHELL_TOOL="Bash"
  FORBIDDEN_SHELL="PowerShell"
fi
CMD=(claude -p "Lies den vollständigen Auftrag aus dieser Datei und führe ihn exakt aus: $PROMPT" \
  --append-system-prompt "Use only $SHELL_TOOL or Read for repository inspection. Remain read-only. Never inspect a parent, sibling, other repository, or live working-tree evidence file unless the prompt explicitly authorizes its exact root and fixed ref or frozen evidence path; for every authorized repository use ref-qualified reads only. Your final response must begin as its very first bytes, with no preamble, exactly with: $TITLE" \
  --model "$MODEL" --allowedTools "Read,$SHELL_TOOL" \
  --disallowedTools "Agent,Edit,Write,NotebookEdit,WebSearch,WebFetch,$FORBIDDEN_SHELL" \
  --permission-mode dontAsk --output-format json --no-session-persistence \
  --prompt-suggestions false --disable-slash-commands)
if [ -n "${MAX_BUDGET_USD:-}" ]; then CMD+=(--max-budget-usd "$MAX_BUDGET_USD"); fi
"${CMD[@]}" >"$RAW"
DUAL_JUDGE_MODEL="$MODEL" python "$PARSER_FOR_PYTHON" claude "$RAW_FOR_PYTHON" "$RESULT_FOR_PYTHON" "$METRICS_FOR_PYTHON"
