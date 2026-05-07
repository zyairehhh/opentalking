#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
profile=${1:-$(bash "$HERE/detect_hardware.sh")}

case "$profile" in
  cuda-*)      compose_file="deploy/compose/docker-compose.cuda.yml" ;;
  ascend-910b) compose_file="deploy/compose/docker-compose.ascend.yml" ;;
  cpu-demo)    compose_file="deploy/compose/docker-compose.dev.yml" ;;
  *)           echo "unknown profile: $profile"; exit 2 ;;
esac

cd "$ROOT"
docker compose -f "$compose_file" up -d
bash "$HERE/ensure_omnirt.sh" || true
docker compose -f "$compose_file" ps
