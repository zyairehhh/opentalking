#!/usr/bin/env bash
# OpenTalking one-click installer.
#   bash scripts/install.sh           # auto-detect, default to docker
#   bash scripts/install.sh native    # native venv install
#   bash scripts/install.sh docker    # explicit docker mode
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)

profile=$(bash "$HERE/detect_hardware.sh")
mode=${1:-docker}
echo "Detected hardware profile: $profile"
echo "Install mode: $mode"

case "$mode" in
  docker) bash "$HERE/install_docker.sh" "$profile" ;;
  native) bash "$HERE/install_native.sh" "$profile" ;;
  *)
    echo "Usage: install.sh [docker|native]"
    exit 2
    ;;
esac

# Optional: for high-end hardware, offer to pre-pull FlashTalk weights into omnirt.
if [[ "$profile" =~ ^(cuda-4090|ascend-910b)$ ]]; then
  read -rp "High-end hardware detected. Pre-pull FlashTalk 14B (37GB) into omnirt now? [y/N] " yn
  if [[ "$yn" =~ ^[Yy]$ ]]; then
    bash "$HERE/download_flashtalk.sh"
  fi
fi

bash "$HERE/up.sh" "$profile"
echo ""
echo "✅ OpenTalking is up at http://localhost:5173 (API: http://localhost:8000)"
echo "   Run 'bash scripts/down.sh' to stop."
