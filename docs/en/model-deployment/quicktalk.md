# QuickTalk

## Support Status

| Item | Value |
|------|-------|
| Model ID | `quicktalk` |
| Backend | `local` |
| Evidence level | Built in, verified |
| Best for | Local realtime adapter, development reference, QuickTalk asset validation |

## Recommended Hardware

Local CUDA GPU. Validate `mock` first, then connect QuickTalk assets and a template video.

## Weights

The QuickTalk local adapter loads weights in the OpenTalking process and does not require OmniRT. Place the model weights, HuBERT files, InsightFace assets, and caches under repository-root `models/quicktalk/`.

## Directory Layout

```text
models/
  quicktalk/
    checkpoints/
      quicktalk.pth or 256.onnx
      repair.npy
      chinese-hubert-large/
        pytorch_model.bin
      auxiliary/models/buffalo_l/ or auxiliary_min/
        det_10g.onnx
```

If you already have a legacy asset bundle organized as `hdModule/checkpoints/`, `OPENTALKING_QUICKTALK_ASSET_ROOT` may point either to the parent directory or to `hdModule`; the adapter normalizes it to the directory that contains `checkpoints/`.

## Configuration

```env title=".env"
OPENTALKING_QUICKTALK_ASSET_ROOT=/absolute/path/to/opentalking/models/quicktalk
# Optional: built-in QuickTalk avatars declare template_video in their manifests; custom avatars may override it here.
# OPENTALKING_QUICKTALK_TEMPLATE_VIDEO=/absolute/path/to/template.mp4
OPENTALKING_QUICKTALK_WORKER_CACHE=1
OPENTALKING_TORCH_DEVICE=cuda:0
```

Avatar manifest:

```json title="manifest.json"
{
  "model_type": "quicktalk",
  "metadata": {
    "asset_root": "/absolute/path/to/opentalking/models/quicktalk",
    "template_video": "/absolute/path/to/template.mp4"
  }
}
```

## Start

```bash title="Terminal"
export OPENTALKING_TORCH_DEVICE=cuda:0
export OPENTALKING_QUICKTALK_ASSET_ROOT="$DIGITAL_HUMAN_HOME/opentalking/models/quicktalk"
export OPENTALKING_QUICKTALK_WORKER_CACHE=1

cd "$DIGITAL_HUMAN_HOME/opentalking"
bash scripts/start_unified.sh --backend local --model quicktalk --api-port 8210 --web-port 5280
```

Open `http://localhost:5280`, select the `QuickTalk Local` avatar, and select the `quicktalk` model. If you omit `--web-port`, the default frontend URL is `http://localhost:5173`.

## Prepare Avatar Cache

QuickTalk generates per-avatar runtime cache files:

- `examples/avatars/<avatar>/quicktalk/template_<width>x<height>.mp4`
- `examples/avatars/<avatar>/quicktalk/face_cache_v3_<width>x<height>.npz`

These files depend on the local model runtime and avatar contents. Treat them as deployment artifacts and do not commit them to the source repository. To prepare them ahead of time:

```bash title="Terminal"
cd "$DIGITAL_HUMAN_HOME/opentalking"

opentalking-prepare-cache \
  --model quicktalk \
  --avatars-root examples/avatars \
  --quicktalk-model-root models/quicktalk \
  --device cuda:0 \
  --model-backend pth \
  --verify
```

To prepare one avatar:

```bash title="Terminal"
opentalking-prepare-cache \
  --model quicktalk \
  --avatars-root examples/avatars \
  --avatar singer \
  --quicktalk-model-root models/quicktalk \
  --device cuda:0 \
  --model-backend pth \
  --verify
```

## `/models` Verification

```bash title="Terminal"
curl -s http://127.0.0.1:8210/models | jq '.statuses[] | select(.id=="quicktalk")'
```

Expected:

```json
{"id":"quicktalk","backend":"local","connected":true,"reason":"local_runtime"}
```

## Common Errors

| Symptom | Action |
|---------|--------|
| `connected=false` | Check QuickTalk dependencies, asset paths, and `OPENTALKING_TORCH_DEVICE`. |
| Long first turn | Enable `OPENTALKING_QUICKTALK_WORKER_CACHE=1`. |
| Avatar load failure | `asset_root` and `template_video` must be reachable absolute paths. |
