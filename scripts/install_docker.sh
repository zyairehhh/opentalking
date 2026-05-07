#!/usr/bin/env bash
set -euo pipefail
profile=${1:?profile required}
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)

[[ -f "$ROOT/.env" ]] || cp "$ROOT/.env.example" "$ROOT/.env"

case "$profile" in
  cuda-*)        compose_file="deploy/compose/docker-compose.cuda.yml" ;;
  ascend-910b)   compose_file="deploy/compose/docker-compose.ascend.yml" ;;
  cpu-demo)      compose_file="deploy/compose/docker-compose.dev.yml" ;;
  *)             echo "unknown profile: $profile"; exit 2 ;;
esac

if [[ ! -f "$ROOT/$compose_file" ]]; then
  echo "ERROR: $compose_file not found." >&2
  echo "Profiles for ascend / cpu are not yet shipped — open an issue or use cuda profile." >&2
  exit 3
fi

cd "$ROOT"
echo "Pulling images for $profile ..."
docker compose -f "$compose_file" pull || true
