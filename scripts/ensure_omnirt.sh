#!/usr/bin/env bash
# Wait for the omnirt service to report healthy before continuing.
set -euo pipefail
endpoint=${OMNIRT_ENDPOINT:-http://localhost:9000}
echo "Waiting for omnirt at $endpoint/health ..."
for _ in {1..30}; do
  if curl -fsS "$endpoint/health" >/dev/null 2>&1; then
    echo "✅ omnirt healthy"
    exit 0
  fi
  sleep 2
done
echo "❌ omnirt not healthy after 60s — check container logs"
exit 1
