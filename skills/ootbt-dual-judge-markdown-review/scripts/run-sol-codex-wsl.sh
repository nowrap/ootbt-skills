#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh"; fi
if command -v codex >/dev/null 2>&1; then
  CODEX_BIN="$(command -v codex)"
elif [ -x "$HOME/.local/bin/codex" ]; then
  CODEX_BIN="$HOME/.local/bin/codex"
else
  echo "ERROR: native Linux Codex missing in WSL" >&2
  exit 127
fi
command -v node >/dev/null 2>&1 || { echo "ERROR: Node missing in WSL" >&2; exit 127; }
if [ "${1:-}" = "--capability" ]; then
  printf 'node_version=%s\n' "$(node --version)"
  printf 'codex_version=%s\n' "$("$CODEX_BIN" --version)"
  exit 0
fi
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <repo-root> <model> <reasoning-effort> <instruction>" >&2
  exit 2
fi
exec "$CODEX_BIN" exec -C "$1" -s read-only --ephemeral -m "$2" \
  -c "model_reasoning_effort=\"$3\"" --json "$4"
