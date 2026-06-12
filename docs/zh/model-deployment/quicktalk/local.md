# QuickTalk Local 单机部署

本页用于把 QuickTalk 直接加载到 OpenTalking 进程内，不先启动 OmniRT。Linux + CUDA 仍是推荐的实时路径；Apple Silicon 可以用 `quicktalk-cpu` 在本机跑通完整链路，适合开发、演示和集成验证。

## 路径选择

| 平台 | 安装 extra | 默认设备 | 说明 |
| --- | --- | --- | --- |
| Apple Silicon macOS | `quicktalk-cpu` | `mps`，不可用时 `cpu` | 不安装 `onnxruntime-gpu`；默认用较小 QuickTalk chunk 降低长文本卡顿。 |
| Linux + NVIDIA GPU | `quicktalk-cuda` | `cuda:0` | 推荐实时路径；保持 28 帧 chunk。 |

公开权重 `datascale-ai/quicktalk` 提供 `quicktalk.pth`，不提供 `256.onnx`。如果你自己有 `256.onnx`，macOS arm64 上会优先尝试 ONNX Runtime 的 `CoreMLExecutionProvider`，否则回退 CPU；Linux CUDA 会继续优先 CUDA provider。

## Apple Silicon 从零部署

### 1. 准备系统依赖

```bash title="终端"
brew install python@3.11 node uv
```

`ffmpeg` 可选安装。`quicktalk-cpu` 会安装 `imageio-ffmpeg` 作为兜底；如果你想使用系统 ffmpeg：

```bash title="终端"
brew install ffmpeg
```

### 2. 拉代码并创建 `.venv`

```bash title="终端"
git clone https://github.com/OpenTalker/opentalking.git
cd opentalking

# 国内网络较慢时可先设置镜像。
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300
export UV_LINK_MODE=copy

uv sync --extra dev --extra models --extra quicktalk-cpu --python 3.11
source .venv/bin/activate
```

不要在 Apple Silicon 上安装 `quicktalk-cuda`：`onnxruntime-gpu` 没有 macOS arm64 wheel。

### 3. 下载 QuickTalk 权重

```bash title="终端"
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

最终目录应包含：

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

### 4. 配置 `.env`

```bash title="终端"
cp .env.example .env
```

编辑 `.env` 中这些值：

```env title=".env"
OPENTALKING_DEFAULT_MODEL=quicktalk
OPENTALKING_LLM_API_KEY=<your-llm-key>
OPENTALKING_STT_DASHSCOPE_API_KEY=<your-dashscope-stt-key>

OPENTALKING_FFMPEG_BIN=
OPENTALKING_QUICKTALK_BACKEND=local
OPENTALKING_QUICKTALK_ASSET_ROOT=./models/quicktalk
OPENTALKING_QUICKTALK_MODEL_BACKEND=auto
OPENTALKING_QUICKTALK_WORKER_CACHE=1

# 可省略；不设置时 Apple Silicon 会自动选择 mps，不可用时回退 cpu。
OPENTALKING_QUICKTALK_DEVICE=mps

# Apple Silicon 上保持 12；这样每个 generate chunk 有足够音频预算。
OPENTALKING_QUICKTALK_SLICE_LEN=12

# Apple Silicon 上建议开启。它把实际输出从模型原生 25fps 降到 14fps，
# 让 MPS 生成速度更容易跟上长文本播放。
OPENTALKING_QUICKTALK_FPS=14
```

`OPENTALKING_FFMPEG_BIN=` 保持为空时，OpenTalking 会先找系统 `ffmpeg`，找不到再使用 `imageio-ffmpeg`。这比固定写 `ffmpeg` 更适合新 Mac。

### 5. 本地环境自检

```bash title="终端"
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

### 6. 启动 API 和 WebUI

```bash title="终端"
bash scripts/start_unified.sh \
  --backend local \
  --model quicktalk \
  --api-port 8210 \
  --web-port 5280
```

打开 `http://127.0.0.1:5280`，选择内置 `singer` avatar，模型选择 `quicktalk`。首次启动会构建 avatar cache，耗时取决于头像尺寸、MPS/CPU 性能和人脸检测速度。

### 7. API 验证

```bash title="终端"
curl -s http://127.0.0.1:8210/health | python -m json.tool
curl -s http://127.0.0.1:8210/models | python -m json.tool
```

创建会话并发送一句话：

```bash title="终端"
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
  -d '{"text":"请用一句话确认 QuickTalk 已在 Mac 本地运行。","tts_provider":"edge"}' \
  | python -m json.tool
```

状态从 `speaking` 回到 `ready`，且日志里出现 QuickTalk generate / `Speak pipeline timing`，表示本地链路已跑通。

## Linux + CUDA 路径

Linux GPU 用户继续使用 CUDA extra：

```bash title="终端"
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300
export UV_LINK_MODE=copy

uv sync --extra dev --extra models --extra quicktalk-cuda --python 3.11
source .venv/bin/activate
```

`.env` 示例：

```env title=".env"
OPENTALKING_DEFAULT_MODEL=quicktalk
OPENTALKING_QUICKTALK_BACKEND=local
OPENTALKING_QUICKTALK_ASSET_ROOT=/absolute/path/to/opentalking/models/quicktalk
OPENTALKING_QUICKTALK_WORKER_CACHE=1
OPENTALKING_QUICKTALK_DEVICE=cuda:0
OPENTALKING_TORCH_DEVICE=cuda:0

# Linux CUDA 默认 28；通常不需要设置。
# OPENTALKING_QUICKTALK_SLICE_LEN=28
```

启动命令不变：

```bash title="终端"
bash scripts/start_unified.sh --backend local --model quicktalk --api-port 8000 --web-port 5173
```

提前生成 avatar cache 时，Linux CUDA 可继续使用：

```bash title="终端"
opentalking-prepare-cache \
  --model quicktalk \
  --avatars-root examples/avatars \
  --quicktalk-asset-root models/quicktalk \
  --device cuda:0 \
  --model-backend pth \
  --verify
```

Apple Silicon 上也可以把 `--device cuda:0` 改成 `--device mps`，但首次 cache 构建仍可能较慢。

## 性能参数

| 参数 | Mac 默认 | Linux CUDA 默认 | 作用 |
| --- | ---: | ---: | --- |
| `OPENTALKING_QUICKTALK_SLICE_LEN` | `12` | `28` | 每个 QuickTalk generate chunk 的视频帧数。Mac 上保持 `12`；更小的值会缩短音频预算，长文本反而可能更不稳定。 |
| `OPENTALKING_QUICKTALK_FPS` | 未设置 | 未设置 | 可选输出帧率覆盖。Apple Silicon 上如果优先要长文本顺滑，可设为 `14`；Linux CUDA 保持未设置。 |
| `OPENTALKING_QUICKTALK_MAX_LONG_EDGE` | `900` | `900` | avatar 模板长边上限。降到 `720` 可小幅减轻 Mac 压力，但主要瓶颈仍是模型生成。 |
| `OPENTALKING_QUICKTALK_WORKER_CACHE` | `1` | `1` | 缓存 QuickTalk worker，避免同一 avatar 重复加载模型。 |

Mac 上如果长文本仍明显卡顿，优先尝试：

```env title=".env"
OPENTALKING_QUICKTALK_SLICE_LEN=12
OPENTALKING_QUICKTALK_FPS=14
OPENTALKING_QUICKTALK_MAX_LONG_EDGE=720
```

这会牺牲动作帧率或画面尺寸来换取播放顺滑。需要稳定 25fps 实时输出时，仍建议 Linux + CUDA 或 OmniRT。

## 常见问题

| 现象 | 处理 |
| --- | --- |
| `onnxruntime-gpu` 安装失败 | Apple Silicon 使用 `quicktalk-cpu`，不要安装 `quicktalk-cuda`。 |
| `ffmpeg` 找不到 | `.env` 中保持 `OPENTALKING_FFMPEG_BIN=`，或安装 `brew install ffmpeg`。 |
| `/sessions` 报 STT key 缺失 | 设置 `OPENTALKING_STT_DASHSCOPE_API_KEY`，或在 WebUI 选择本地 SenseVoice。 |
| LLM 401 / unauthorized | 设置 `OPENTALKING_LLM_API_KEY`，并确认 `OPENTALKING_LLM_BASE_URL` 与模型匹配。 |
| MPS 出现 SVD CPU fallback 警告 | 属于 PyTorch MPS 的算子覆盖限制，通常不影响跑通，但会影响速度。 |
| 端口被占用 | 换 `--api-port` / `--web-port`，或停止占用端口的进程。 |
| 首次启动很慢 | 首次会加载 HuBERT、QuickTalk 和人脸缓存；同一 avatar 后续可复用 cache。 |
