#!/usr/bin/env bash
# Output one of: cuda-4090 | cuda-3090 | ascend-910b | cpu-demo
set -euo pipefail

if command -v npu-smi >/dev/null 2>&1; then
  echo "ascend-910b"
  exit 0
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  name=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | tr -d ' ' | tr 'A-Z' 'a-z')
  case "$name" in
    *4090*) echo "cuda-4090" ;;
    *3090*) echo "cuda-3090" ;;
    *)      echo "cuda-3090" ;;
  esac
  exit 0
fi

echo "cpu-demo"
