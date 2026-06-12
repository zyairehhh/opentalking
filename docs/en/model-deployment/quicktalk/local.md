# QuickTalk Local Deployment

Use this guide when OpenTalking should load QuickTalk in-process instead of starting OmniRT first. Linux + CUDA remains the recommended realtime path. Apple Silicon can run the full local path with `quicktalk-cpu` for development, demos, and integration checks.

## Choose a Path

| Platform | Install extra | Default device | Notes |
| --- | --- | --- | --- |
| Apple Silicon macOS | `quicktalk-cpu` | `mps`, then `cpu` | Do not install `onnxruntime-gpu`; smaller QuickTalk chunks are used by default to reduce long-text stalls. |
| Linux + NVIDIA GPU | `quicktalk-cuda` | `cuda:0` | Recommended realtime path; keeps 28-frame chunks. |

The public `datascale-ai/quicktalk` weights ship `quicktalk.pth`, not `256.onnx`. If you provide your own `256.onnx`, macOS arm64 tries ONNX Runtime `CoreMLExecutionProvider` first and falls back to CPU; Linux CUDA keeps the CUDA provider path.

## Apple Silicon From Scratch

### 1. Install System Dependencies

```bash title="Terminal"
brew install python@3.11 node uv
```

`ffmpeg` is optional. `quicktalk-cpu` installs `imageio-ffmpeg` as a fallback. To use system ffmpeg:

```bash title="Terminal"
brew install ffmpeg
```

### 2. Clone and Create `.venv`

```bash title="Terminal"
git clone https://github.com/OpenTalker/opentalking.git
cd opentalking

# Optional mirrors for slower networks.
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300
export UV_LINK_MODE=copy

uv sync --extra dev --extra models --extra quicktalk-cpu --python 3.11
source .venv/bin/activate
```

Do not install `quicktalk-cuda` on Apple Silicon: `onnxruntime-gpu` has no macOS arm64 wheel.

### 3. Download QuickTalk Weights

```bash title="Terminal"
mkdir -p models/quicktalk/checkpoints

hf download datascale-ai/quicktalk \
  quicktalk.pth \
  repair.npy \
  chinese-hubert-large/config.json \
  chinese-hubert-large/preprocessor_config.json \
  chinese-hubert-large/pytorch_model.bin \
  --local-dir models/quicktalk/checkpoints

mkdir -p models/quicktalk/checkpoints/auxiliary/models
curl -L \
  https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip \
  -o /tmp/buffalo_l.zip
unzip -o /tmp/buffalo_l.zip \
  -d models/quicktalk/checkpoints/auxiliary/models/buffalo_l
```

The final layout should include:

```text
models/quicktalk/
  checkpoints/
    quicktalk.pth
    repair.npy
    chinese-hubert-large/
      config.json
      preprocessor_config.json
      pytorch_model.bin
    auxiliary/models/buffalo_l/
      *.onnx
```

### 4. Configure `.env`

```bash title="Terminal"
cp .env.example .env
```

Edit these values:

```env title=".env"
OPENTALKING_DEFAULT_MODEL=quicktalk
OPENTALKING_LLM_API_KEY=<your-llm-key>
OPENTALKING_STT_DASHSCOPE_API_KEY=<your-dashscope-stt-key>

OPENTALKING_FFMPEG_BIN=
OPENTALKING_QUICKTALK_BACKEND=local
OPENTALKING_QUICKTALK_ASSET_ROOT=./models/quicktalk
OPENTALKING_QUICKTALK_MODEL_BACKEND=auto
OPENTALKING_QUICKTALK_WORKER_CACHE=1

# Optional. If unset, Apple Silicon auto-selects mps and falls back to cpu.
OPENTALKING_QUICKTALK_DEVICE=mps

# Keep 12 on Apple Silicon; it leaves enough audio budget per generated chunk.
OPENTALKING_QUICKTALK_SLICE_LEN=12

# Optional but recommended on Apple Silicon for long text. This lowers the actual
# generated output cadence from model-native 25fps to 14fps so generation can stay
# ahead of playback on MPS.
OPENTALKING_QUICKTALK_FPS=14
```

Leaving `OPENTALKING_FFMPEG_BIN=` empty lets OpenTalking find system `ffmpeg` first and fall back to `imageio-ffmpeg`. This is safer for fresh Macs than hardcoding `ffmpeg`.

### 5. Check the Local Environment

```bash title="Terminal"
python - <<'PY'
from pathlib import Path
import torch
import onnxruntime as ort
from opentalking.models.quicktalk.runtime_v2 import ensure_ffmpeg

root = Path("models/quicktalk/checkpoints")
for path in [
    root / "quicktalk.pth",
    root / "repair.npy",
    root / "chinese-hubert-large/pytorch_model.bin",
    root / "auxiliary/models/buffalo_l/det_10g.onnx",
]:
    print(path, path.exists())
print("mps:", torch.backends.mps.is_available())
print("onnxruntime providers:", ort.get_available_providers())
print("ffmpeg:", ensure_ffmpeg())
PY
```

### 6. Start API and WebUI

```bash title="Terminal"
bash scripts/start_unified.sh \
  --backend local \
  --model quicktalk \
  --api-port 8210 \
  --web-port 5280
```

Open `http://127.0.0.1:5280`, choose the built-in `singer` avatar, and select `quicktalk`. The first run builds the avatar cache; time depends on avatar size, MPS/CPU speed, and face detection.

### 7. Verify the API

```bash title="Terminal"
curl -s http://127.0.0.1:8210/health | python -m json.tool
curl -s http://127.0.0.1:8210/models | python -m json.tool
```

Create a session and speak:

```bash title="Terminal"
curl -s -X POST http://127.0.0.1:8210/sessions \
  -H 'Content-Type: application/json' \
  -d '{"avatar_id":"singer","model":"quicktalk","tts_provider":"edge"}' \
  | tee /tmp/opentalking-session.json | python -m json.tool

sid=$(python - <<'PY'
import json
print(json.load(open("/tmp/opentalking-session.json"))["session_id"])
PY
)

curl -s -X POST "http://127.0.0.1:8210/sessions/$sid/start" \
  -H 'Content-Type: application/json' \
  -d '{}' | python -m json.tool

curl -s -X POST "http://127.0.0.1:8210/sessions/$sid/speak" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Please confirm in one sentence that QuickTalk is running locally on this Mac.","tts_provider":"edge"}' \
  | python -m json.tool
```

When state returns from `speaking` to `ready` and logs include QuickTalk generate / `Speak pipeline timing`, the local path is working.

## Linux + CUDA Path

Linux GPU users should keep using the CUDA extra:

```bash title="Terminal"
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300
export UV_LINK_MODE=copy

uv sync --extra dev --extra models --extra quicktalk-cuda --python 3.11
source .venv/bin/activate
```

`.env` example:

```env title=".env"
OPENTALKING_DEFAULT_MODEL=quicktalk
OPENTALKING_QUICKTALK_BACKEND=local
OPENTALKING_QUICKTALK_ASSET_ROOT=/absolute/path/to/opentalking/models/quicktalk
OPENTALKING_QUICKTALK_WORKER_CACHE=1
OPENTALKING_QUICKTALK_DEVICE=cuda:0
OPENTALKING_TORCH_DEVICE=cuda:0

# Linux CUDA defaults to 28; usually leave unset.
# OPENTALKING_QUICKTALK_SLICE_LEN=28
```

Start command:

```bash title="Terminal"
bash scripts/start_unified.sh --backend local --model quicktalk --api-port 8000 --web-port 5173
```

To prebuild avatar cache on Linux CUDA:

```bash title="Terminal"
opentalking-prepare-cache \
  --model quicktalk \
  --avatars-root examples/avatars \
  --quicktalk-asset-root models/quicktalk \
  --device cuda:0 \
  --model-backend pth \
  --verify
```

On Apple Silicon, replace `--device cuda:0` with `--device mps`, but initial cache building can still be slow.

## Performance Knobs

| Variable | macOS default | Linux CUDA default | Effect |
| --- | ---: | ---: | --- |
| `OPENTALKING_QUICKTALK_SLICE_LEN` | `12` | `28` | Number of QuickTalk video frames per generate chunk. Keep `12` on Mac; smaller values shorten audio budget and can make long text less stable. |
| `OPENTALKING_QUICKTALK_FPS` | unset | unset | Optional output FPS override. Set `14` on Apple Silicon when smooth long-text playback matters more than 25fps motion. Leave unset on Linux CUDA. |
| `OPENTALKING_QUICKTALK_MAX_LONG_EDGE` | `900` | `900` | Avatar template long-edge cap. Lowering to `720` can slightly reduce Mac load at the cost of output size, but the main bottleneck is model generation. |
| `OPENTALKING_QUICKTALK_WORKER_CACHE` | `1` | `1` | Reuses the QuickTalk worker for the same avatar. |

If long text still stalls on Mac, try:

```env title=".env"
OPENTALKING_QUICKTALK_SLICE_LEN=12
OPENTALKING_QUICKTALK_FPS=14
OPENTALKING_QUICKTALK_MAX_LONG_EDGE=720
```

This trades motion FPS or image size for smoother playback. For stable 25fps realtime output, use Linux + CUDA or OmniRT.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `onnxruntime-gpu` fails to install | Use `quicktalk-cpu` on Apple Silicon; do not install `quicktalk-cuda`. |
| `ffmpeg` is missing | Keep `OPENTALKING_FFMPEG_BIN=` empty, or install `brew install ffmpeg`. |
| `/sessions` reports missing STT key | Set `OPENTALKING_STT_DASHSCOPE_API_KEY`, or choose local SenseVoice in the WebUI. |
| LLM 401 / unauthorized | Set `OPENTALKING_LLM_API_KEY` and confirm base URL / model compatibility. |
| MPS shows an SVD CPU fallback warning | This is a PyTorch MPS operator coverage limitation. It usually does not block execution, but can affect speed. |
| Port already in use | Change `--api-port` / `--web-port`, or stop the process using the port. |
| First startup is slow | The first run loads HuBERT, QuickTalk, and face cache. Reusing the same avatar is faster after cache is built. |
