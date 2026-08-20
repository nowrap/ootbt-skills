#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 3 ]; then echo "Usage: $0 <repo-root> <prompt-file> <result-file>" >&2; exit 2; fi
REPO="$1"; PROMPT="$2"; RESULT="$3"; MODEL="${CODEX_MODEL:-gpt-5.6-sol}"; EFFORT="${CODEX_REASONING_EFFORT:-max}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PARSER="$DIR/parse-agent-output.py"; PREFLIGHT_CHECKER="$DIR/check-codex-preflight.py"; WSL_HELPER="$DIR/run-sol-codex-wsl.sh"
if command -v cygpath >/dev/null 2>&1; then
  PARSER_FOR_PYTHON="$(cygpath -w "$PARSER")"
  PREFLIGHT_CHECKER_FOR_PYTHON="$(cygpath -w "$PREFLIGHT_CHECKER")"
else
  PARSER_FOR_PYTHON="$PARSER"
  PREFLIGHT_CHECKER_FOR_PYTHON="$PREFLIGHT_CHECKER"
fi
RAW="$RESULT.raw.jsonl"; METRICS="$RESULT.metrics.json"
PREFLIGHT_RAW="$RESULT.preflight.raw.jsonl"; PREFLIGHT_STDERR="$RESULT.preflight.stderr.log"
if command -v cygpath >/dev/null 2>&1; then
  RAW_FOR_PYTHON="$(cygpath -w "$RAW")"
  RESULT_FOR_PYTHON="$(cygpath -w "$RESULT")"
  METRICS_FOR_PYTHON="$(cygpath -w "$METRICS")"
  PREFLIGHT_RAW_FOR_PYTHON="$(cygpath -w "$PREFLIGHT_RAW")"
else
  RAW_FOR_PYTHON="$RAW"
  RESULT_FOR_PYTHON="$RESULT"
  METRICS_FOR_PYTHON="$METRICS"
  PREFLIGHT_RAW_FOR_PYTHON="$PREFLIGHT_RAW"
fi
[ -d "$REPO" ] || { echo "ERROR: repo missing: $REPO" >&2; exit 2; }
[ -f "$PROMPT" ] || { echo "ERROR: prompt missing: $PROMPT" >&2; exit 2; }
command -v python >/dev/null || { echo "ERROR: python missing" >&2; exit 2; }
[ -f "$PREFLIGHT_CHECKER" ] || { echo "ERROR: preflight checker missing: $PREFLIGHT_CHECKER" >&2; exit 2; }
[ -f "$WSL_HELPER" ] || { echo "ERROR: WSL helper missing: $WSL_HELPER" >&2; exit 2; }

HOST_OS="$(uname -s)"
EXECUTION_ENVIRONMENT="native"
WSL_CAPABILITY_STATUS="not-applicable"
WSL_DISTRO_NAME_VALUE=""
WSL_KERNEL=""
WSL_NODE_VERSION=""
WSL_CODEX_VERSION=""
WSL_REPO=""
WSL_PROMPT=""
WSL_HELPER_PATH=""
WSL_CMD=(wsl.exe)
if [ -n "${SOL_WSL_DISTRO:-}" ]; then WSL_CMD+=(-d "$SOL_WSL_DISTRO"); fi
WSL_CMD+=(--exec)

is_windows_host() {
  case "$HOST_OS" in MINGW*|MSYS*|CYGWIN*) return 0;; *) return 1;; esac
}

to_wsl_path() {
  local host_path="$1" windows_path forwarded_wslenv
  command -v cygpath >/dev/null 2>&1 || return 1
  windows_path="$(cygpath -aw "$host_path")" || return 1
  forwarded_wslenv="${WSLENV:+$WSLENV:}DUAL_JUDGE_PATH/p"
  DUAL_JUDGE_PATH="$windows_path" WSLENV="$forwarded_wslenv" \
    "${WSL_CMD[@]}" bash -lc 'printf "%s" "$DUAL_JUDGE_PATH"' 2>/dev/null | tr -d '\r'
}

wsl_codex_version() {
  "${WSL_CMD[@]}" bash -ic '
if command -v codex >/dev/null 2>&1; then
  codex --version
elif [ -x "$HOME/.local/bin/codex" ]; then
  "$HOME/.local/bin/codex" --version
else
  exit 127
fi
' 2>/dev/null | tr -d '\r'
}

prepare_wsl() {
  command -v wsl.exe >/dev/null 2>&1 || return 1
  "${WSL_CMD[@]}" bash -ic '
command -v node >/dev/null 2>&1
node --version >/dev/null 2>&1
if command -v codex >/dev/null 2>&1; then
  codex --version >/dev/null 2>&1
elif [ -x "$HOME/.local/bin/codex" ]; then
  "$HOME/.local/bin/codex" --version >/dev/null 2>&1
else
  exit 127
fi
' >/dev/null 2>&1 || return 1
  WSL_DISTRO_NAME_VALUE="$("${WSL_CMD[@]}" bash -lc 'printf "%s" "${WSL_DISTRO_NAME:-unknown}"' 2>/dev/null | tr -d '\r')" || return 1
  WSL_KERNEL="$("${WSL_CMD[@]}" uname -sr 2>/dev/null | tr -d '\r')" || return 1
  WSL_NODE_VERSION="$("${WSL_CMD[@]}" bash -ic 'node --version' 2>/dev/null | tr -d '\r')" || return 1
  WSL_CODEX_VERSION="$(wsl_codex_version)" || return 1
  WSL_REPO="$(to_wsl_path "$REPO")" || return 1
  WSL_PROMPT="$(to_wsl_path "$PROMPT")" || return 1
  WSL_HELPER_PATH="$(to_wsl_path "$WSL_HELPER")" || return 1
  [ -n "$WSL_REPO" ] && [ -n "$WSL_PROMPT" ] && [ -n "$WSL_HELPER_PATH" ] || return 1
  "${WSL_CMD[@]}" test -d "$WSL_REPO" >/dev/null 2>&1 || return 1
  "${WSL_CMD[@]}" test -f "$WSL_PROMPT" >/dev/null 2>&1 || return 1
  "${WSL_CMD[@]}" test -f "$WSL_HELPER_PATH" >/dev/null 2>&1 || return 1
}

if is_windows_host; then
  WSL_CAPABILITY_STATUS="unavailable"
  if prepare_wsl; then
    EXECUTION_ENVIRONMENT="wsl"
    WSL_CAPABILITY_STATUS="available"
    echo "INFO: using native Linux Codex through WSL distribution '$WSL_DISTRO_NAME_VALUE' ($WSL_CODEX_VERSION, $WSL_NODE_VERSION)" >&2
  else
    echo "INFO: WSL with native Node and Codex is unavailable; using native Windows Codex" >&2
  fi
fi

if [ "$EXECUTION_ENVIRONMENT" = "native" ]; then
  command -v codex >/dev/null || { echo "ERROR: codex missing" >&2; exit 2; }
fi

run_codex() {
  local instruction="$1"
  if [ "$EXECUTION_ENVIRONMENT" = "wsl" ]; then
    "${WSL_CMD[@]}" bash -c 'tr -d "\r" < "$1" | bash -s -- "$2" "$3" "$4" "$5"' \
      bash "$WSL_HELPER_PATH" "$WSL_REPO" "$MODEL" "$EFFORT" "$instruction"
  else
    codex exec -C "$REPO" -s read-only --ephemeral -m "$MODEL" \
      -c "model_reasoning_effort=\"$EFFORT\"" --json "$instruction"
  fi
}

mkdir -p "$(dirname "$RESULT")"; rm -f "$RESULT" "$RAW" "$METRICS" "$PREFLIGHT_RAW" "$PREFLIGHT_STDERR"
if ! run_codex 'Antworte exakt mit: SOL_MAX_AVAILABLE' >"$PREFLIGHT_RAW" 2>"$PREFLIGHT_STDERR"; then
  echo "ERROR: SOL preflight failed in '$EXECUTION_ENVIRONMENT' for model '$MODEL' with reasoning effort '$EFFORT'; no cross-environment fallback after a provider/model/auth failure; see $PREFLIGHT_RAW and $PREFLIGHT_STDERR" >&2
  exit 69
fi
python "$PREFLIGHT_CHECKER_FOR_PYTHON" "$PREFLIGHT_RAW_FOR_PYTHON" || {
  echo "ERROR: SOL preflight validation failed in '$EXECUTION_ENVIRONMENT' for model '$MODEL' with reasoning effort '$EFFORT'" >&2
  exit 69
}
if [ "$EXECUTION_ENVIRONMENT" = "wsl" ]; then PROMPT_FOR_CODEX="$WSL_PROMPT"; else PROMPT_FOR_CODEX="$PROMPT"; fi
run_codex "Lies den vollständigen Auftrag aus dieser Datei und führe ihn exakt aus: $PROMPT_FOR_CODEX. Bleibe vollständig read-only. Gib nur den finalen Markdown-Bericht aus." >"$RAW"
TELEMETRY_ENV=(
  "DUAL_JUDGE_MODEL=$MODEL"
  "DUAL_JUDGE_REASONING_EFFORT=$EFFORT"
  "DUAL_JUDGE_EXECUTION_ENVIRONMENT=$EXECUTION_ENVIRONMENT"
  "DUAL_JUDGE_HOST_OS=$HOST_OS"
  "DUAL_JUDGE_WSL_CAPABILITY_STATUS=$WSL_CAPABILITY_STATUS"
)
if [ "$EXECUTION_ENVIRONMENT" = "wsl" ]; then
  TELEMETRY_ENV+=(
    "DUAL_JUDGE_WSL_DISTRO=$WSL_DISTRO_NAME_VALUE"
    "DUAL_JUDGE_WSL_KERNEL=$WSL_KERNEL"
    "DUAL_JUDGE_NODE_VERSION=$WSL_NODE_VERSION"
    "DUAL_JUDGE_CODEX_VERSION=$WSL_CODEX_VERSION"
    "DUAL_JUDGE_WSL_REPO_PATH=$WSL_REPO"
  )
fi
env "${TELEMETRY_ENV[@]}" python "$PARSER_FOR_PYTHON" codex "$RAW_FOR_PYTHON" "$RESULT_FOR_PYTHON" "$METRICS_FOR_PYTHON"
