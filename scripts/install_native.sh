#!/usr/bin/env bash
set -euo pipefail
profile=${1:?profile required}
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
cd "$ROOT"

# Prefer uv if available (project default), otherwise fall back to venv + pip.
if command -v uv >/dev/null 2>&1; then
  uv sync --extra dev
  case "$profile" in
    ascend-910b) uv pip install ".[ascend]" ;;
  esac
else
  [[ -d .venv ]] || python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -U pip
  pip install -e ".[dev]"
  case "$profile" in
    ascend-910b) pip install ".[ascend]" ;;
  esac
fi

echo "Native environment ready. Start omnirt separately, then run scripts/up.sh native."
