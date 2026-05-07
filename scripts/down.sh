#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
profile=${1:-$(bash "$HERE/detect_hardware.sh")}

case "$profile" in
  cuda-*)      compose_file="deploy/compose/docker-compose.cuda.yml" ;;
  ascend-910b) compose_file="deploy/compose/docker-compose.ascend.yml" ;;
  *)           compose_file="deploy/compose/docker-compose.dev.yml" ;;
esac

cd "$ROOT"
docker compose -f "$compose_file" down
