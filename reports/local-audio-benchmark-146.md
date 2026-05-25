# 146 本地 ASR/TTS 接入与验证报告

日期：2026-05-21 CST
Worktree：`/data2/zhongyi/funasr`
分支：`zyaire/funasr-local-audio`
模型根目录：`/data2/zhongyi/model/opentalking-local-audio`
当前入口：API `0.0.0.0:18310`，CosyVoice3 `127.0.0.1:19090`

## 当前结论

主组合已经端到端跑通：

- ASR：`iic/SenseVoiceSmall`，CPU 部署。
- TTS 默认：`FunAudioLLM/Fun-CosyVoice3-0.5B-2512`，独立本地 CosyVoice service，HTTP chunked PCM 真流式输出。
- TTS 实验：`iic/CosyVoice-300M`，独立 service 已跑通，前端选中该模型时后端会路由到 19091。
- 数字人：`QuickTalk local`，OpenTalking unified 进程内本地运行。
- LLM：DashScope compatible-mode。
- 已验证：`/tts/preview`、`/sessions/{id}/transcribe`、`/sessions/{id}/speak_audio`、`/sessions/{id}/speak_audio_stream`、QuickTalk session speak timing。

关键判断：现在卡顿主要不是 ASR。优化后 QuickTalk worker、session TTS 和首帧 render 预热已前移到 service/session 准备阶段；交互首响主要剩 TTS 首个模型 chunk，LLM 总输出长度主要影响整段结束时间。

## 当前服务

- OpenTalking unified：`0.0.0.0:18310`，PID `25370`。
- CosyVoice3 0.5B service：`127.0.0.1:19090`，PID `8025`。
- CosyVoice-300M service：当前未启动；配置仍保留 `19091` 路由和启动脚本。
- `/health`：`tts_provider=local_cosyvoice`，`stt_provider=sensevoice`，`stt_model=iic/SenseVoiceSmall`，`stt_device=cpu`。
- `/models`：`quicktalk backend=local connected=true default_model=quicktalk`。

当前 TTS model -> service 映射：

```bash
OPENTALKING_LOCAL_COSYVOICE_SERVICE_URL=http://127.0.0.1:19090/synthesize
OPENTALKING_LOCAL_COSYVOICE_SERVICE_URLS=FunAudioLLM/Fun-CosyVoice3-0.5B-2512=http://127.0.0.1:19090/synthesize,iic/CosyVoice-300M=http://127.0.0.1:19091/synthesize
```

这意味着前端选择 `Fun-CosyVoice3 0.5B` 会打 19090，选择 `CosyVoice 300M（本地实验）` 会打 19091。请求了未配置的本地 CosyVoice 模型会直接报错，不会静默回退云端或误用默认模型。

本轮新增优化配置：

```bash
OPENTALKING_CHAT_FIRST_SENT_MIN_CHARS=6
OPENTALKING_CHAT_FIRST_SENT_MAX_CHARS=14
OPENTALKING_TTS_PREWARM_ON_PREPARE=1
OPENTALKING_TTS_PREWARM_TEXT=你好
OPENTALKING_TTS_EDGE_FALLBACK_ON_EMPTY_ERROR=0
OPENTALKING_PREWARM_AVATARS=office-woman
OPENTALKING_PREWARM_MODEL=quicktalk
```

CosyVoice3 service 启动脚本开启：

```bash
OPENTALKING_LOCAL_COSYVOICE_PRELOAD=1
OPENTALKING_LOCAL_COSYVOICE_WARMUP_TEXT=你好
```

## ASR 模块

### 接入状态

已完成：

- 新增本地 STT factory，支持 `OPENTALKING_STT_PROVIDER=dashscope|funasr|sensevoice|sherpa_onnx`。
- `/sessions/{id}/transcribe`、`/sessions/{id}/speak_audio`、`/sessions/{id}/speak_audio_stream` 统一接入 STT factory。
- `sensevoice/funasr` 通过 FunASR `AutoModel` 本地识别，支持上传文件和 WebSocket PCM 两种入口。
- SenseVoice 输出 tag 清理已接入，例如 `<|zh|><|NEUTRAL|>` 不进入最终文本。
- 本地 STT adapter 有进程内缓存，避免每次请求重新加载模型。
- 前端设置区显示当前 ASR provider/model，当前是 `ASR: Local FunASR` + `iic/SenseVoiceSmall`。

### 实测结果

模型：`iic/SenseVoiceSmall`
路径：`/data2/zhongyi/model/opentalking-local-audio/iic__SenseVoiceSmall`
放置：CPU，不占 GPU 显存。

- 5.616s 中文 WAV 直接识别：约 396ms，文本为 `开饭时间早上9点至下午5点。`。
- `/sessions/{id}/transcribe` 缓存后：`stt_ms` 约 427-451ms，接口总耗时约 0.55s。
- `/sessions/{id}/speak_audio_stream`：近期日志 `stt_ms=335-497ms`，如果用户录音本身持续 1.3-1.6s，`wall_total_ms` 约等于录音接收时间 + 识别时间。

### ASR 结论

- SenseVoiceSmall CPU 已经足够交互使用，建议 8G/12G 都放 CPU。
- 当前 WebSocket ASR 是“边收 PCM，结束后 final text”，不是逐字 partial streaming；要做实时字幕需要后续接真正 incremental ASR。
- `Fun-ASR-Nano-2512` 本轮未实测，之前 ModelScope ID 返回 404；如从 Hugging Face `FunAudioLLM/Fun-ASR-Nano-2512` 下载，可以后续单独做 CPU/GPU 对照。

## TTS 模块

### 接入状态

已完成：

- 新增 `local_cosyvoice` 和 `local_qwen3_tts` provider。
- `local_cosyvoice` adapter 对齐现有 `synthesize_stream()`，输出 OpenTalking `AudioChunk`，下游 QuickTalk/WebRTC 不感知模型来源。
- CosyVoice service 使用模型级 `stream=True`，HTTP 返回 `audio/L16; rate=16000; channels=1` chunked PCM。
- adapter 支持 `audio/L16` 流式消费，处理 chunk 跨 16-bit sample 边界，不再等待完整 WAV。
- 前端标注 `Local CosyVoice`、`Local Qwen3-TTS`、`本地模型`，并列出 `Fun-CosyVoice3 0.5B（本地模型）` 和 `CosyVoice 300M（本地实验）`。
- 本地失败不自动回退云端；本地模型未配置 service URL 时直接报错。

### Fun-CosyVoice3-0.5B-2512

模型来源：ModelScope / FunAudioLLM
路径：`/data2/zhongyi/model/opentalking-local-audio/FunAudioLLM__Fun-CosyVoice3-0.5B-2512`
服务：`127.0.0.1:19090/synthesize`
显存：PID `3851612` 约 `4954 MiB`。
CPU 内存：历史观测 service RSS 约 `4.9GB`。

实测：

- 同文本 direct service 热态：首包约 4.03s，总耗时 7.55s，输出约 12.56s 音频。
- 短句 `/tts/preview`：HTTP 总耗时 1.98s，service `first_pcm=1.876s`，输出 2.36s 音频。
- 完整 session 第二次短文本：`tts_first_pcm_ms=2412.5`，`first_video_frame_enqueued_ms=2474.1`，`render_total_ms=923.1`，`total_ms=3336.2`。

效果：中文可用，音频有效，QuickTalk 可消费。短 prompt/短文本时日志会出现 `text too short than prompt text` 警告，短句音色稳定性仍要靠更好的内置 prompt 和用户 prompt_text 优化。

### CosyVoice-300M

模型来源：ModelScope `iic/CosyVoice-300M`
路径：`/data2/zhongyi/model/opentalking-local-audio/iic__CosyVoice-300M`
服务：`127.0.0.1:19091/synthesize`
目录体积：约 `5.4GB`。
显存：PID `4130069` 约 `3270 MiB`，另有约 `254 MiB` CUDA 上下文。
CPU 内存：未精确拆分，运行在同一个 CosyVoice service venv。

接入修复：300M 对应的 `CosyVoice.__init__()` 不支持 `load_vllm` 参数，已在 `scripts/local_cosyvoice_service.py` 增加兼容逻辑，遇到该 TypeError 时去掉 `load_vllm` 重试。

实测：

- 冷启动：模型加载 `12.311s`；第一次请求首字节 `18.965s`，总耗时 `27.290s`。
- 热态同文本 direct service：`first_pcm=2.630s`，总耗时 `10.126s`，输出约 `10.855s` 音频。
- 短句 `/tts/preview`：HTTP 总耗时 `3.67s`，service `first_pcm=2.669s`，输出 `3.553s` 音频。

效果和建议：300M 显存比 0.5B 低约 1.7GB，但短句首包并不比 0.5B 更快，输出时长/节奏也更不稳定。它适合作为 8G/显存紧张场景的实验候选，不建议现在替换默认 0.5B。

### Qwen3-TTS

状态：代码 scaffold 和前端选项已接入，但本轮未完成真实可用服务。

原因：`qwen-tts` 默认安装的 torch/CUDA 组合与 146 driver 环境不匹配；尝试重装 CUDA 12.8 compatible torch wheel 时遇到大 wheel 下载中断。当前不建议把它作为今晚可用主线。

## QuickTalk / 端到端

当前配置：

```bash
OPENTALKING_QUICKTALK_BACKEND=local
OPENTALKING_DEFAULT_MODEL=quicktalk
OPENTALKING_TORCH_DEVICE=cuda:1
OPENTALKING_QUICKTALK_HUBERT_DEVICE=cuda:0
OPENTALKING_QUICKTALK_ASSET_ROOT=/data2/zhongyi/model/quicktalk
```

依赖修复：

- 之前 `pyproject.toml` 把 CPU `onnxruntime` 放在 base/models extra，导致 QuickTalk/InsightFace 只能看到 CPU provider 或和 GPU wheel 冲突。
- 已改为互斥 extra：`quicktalk-cpu = onnxruntime`，`quicktalk-cuda = onnxruntime-gpu`。
- 当前 `.venv` 已安装 GPU ORT：`ort 1.26.0`，providers 为 `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`。
- API 已重启，新的 `.venv` provider 对当前进程生效。

端到端 timing（2026-05-21 优化后复测）：

- CosyVoice3 service 启动预加载：模型加载约 `22.364s`，启动阶段 warmup 首包约 `5.250s`。这部分发生在 service 启动，不进入用户首句。
- CosyVoice3 热态短句 direct service：`first_byte_ms=1892.7`，`total_ms=2529.3`。
- OpenTalking 启动阶段 QuickTalk avatar 预热：`office-woman + quicktalk`，face cache hit，`v3_restore_context_seconds=0.822-0.844s`。
- QuickTalk session 创建现在等待 runner ready，并在 prepare 阶段执行 TTS 预热和 QuickTalk 静音 render 预热；复测 `create_ms=5188.5`，返回 `status=created`。
- 第一轮 speak：`tts_first_pcm_ms=2868.4`，`first_render_chunk_ready_ms=2916.7`，`first_video_frame_enqueued_ms=2976.9`，`first_audio_chunk_enqueued_ms=2977.0`，`render_total_ms=1813.4`，`total_ms=5733.8`。
- 第二轮同 session speak：`tts_first_pcm_ms=1986.1`，`first_render_chunk_ready_ms=2000.6`，`first_video_frame_enqueued_ms=2018.6`，`first_audio_chunk_enqueued_ms=2018.7`，`render_total_ms=1525.1`，`total_ms=5131.7`。

对比优化前：

- 过早 speak 的首轮同 session 曾出现 `first_video_frame_enqueued_ms=7474.1`，后来等待 create ready 后仍有 `5734.7ms`。
- 加入 QuickTalk 静音 render 预热后，第一轮 `first_video_frame_enqueued_ms` 降到 `2976.9ms`。
- 稳定同 session 第二轮约 `2018.6ms`，基本贴近 CosyVoice 首包。

卡顿归因：

- ASR：CPU SenseVoice 通常 0.3-0.5s，不是主瓶颈。
- LLM：首 token 约 0.3-0.4s，但总输出可能 2.6-11s；回答越长，整体越慢。
- TTS：热态首包常见 1.8-2.9s，是交互首响应的主要瓶颈。
- QuickTalk：worker、session 和首帧 render 预热后，第一帧基本紧跟 TTS 首包；不预热时第一轮会额外多 2.7-4.5s。

## 模型与资源表

| 模型/模块 | 放置 | 路径/服务 | 显存 | CPU 内存 | 结论 |
| --- | --- | --- | ---: | ---: | --- |
| SenseVoiceSmall | CPU | `iic__SenseVoiceSmall` | 0 | 主进程内，未单独拆分 | 推荐默认 ASR |
| Fun-CosyVoice3-0.5B | GPU | `19090/synthesize` | 约 4.95GiB | 约 4.9GB | 推荐默认本地 TTS |
| CosyVoice-300M | GPU | `19091/synthesize` | 约 3.27GiB + 上下文 | 未精确拆分 | 低显存实验，不建议默认 |
| QuickTalk local + HuBERT | GPU1/GPU0 | OpenTalking API 进程 | 当前进程约 GPU0 `1.55GiB` + GPU1 `0.74GiB` | OpenTalking 进程约 5GB 级 | 可用，必须预热 |
| Qwen3-TTS 0.6B | 未完成 | scaffold 已有 | 未测 | 未测 | 暂不推荐 |

146 上 GPU 环境有其他进程，整卡总 used 不适合直接归因；上表以 per-process `nvidia-smi --query-compute-apps` 为准。

## 8G / 12G 建议

12G 默认组合：

```bash
SenseVoiceSmall CPU + Fun-CosyVoice3-0.5B GPU + QuickTalk local GPU
```

建议 TTS 和 QuickTalk 尽量分卡。如果必须同卡，0.5B + QuickTalk 理论显存接近 7.5GB 级别，但还要留 CUDA 上下文、峰值和前端/浏览器测试余量，12G 比较稳，8G 风险高。

8G 降级组合：

```bash
SenseVoiceSmall CPU + CosyVoice-300M GPU + QuickTalk local GPU
```

这只解决显存，不保证更低延迟。300M 首包当前并不优于 0.5B；如果 8G 上要追求交互流畅，仍建议 TTS 和 QuickTalk 分卡，或继续找更低首包的 TTS。

## 验证结果

已通过：

```bash
uv run --extra dev --extra models --extra local-audio --extra quicktalk-cuda pytest \
  tests/unit/test_local_audio_providers.py \
  tests/unit/test_local_audio_frontend.py \
  tests/unit/test_voice_store.py \
  apps/api/tests/test_voice_labels.py \
  apps/api/tests/test_tts_preview.py -q
# 44 passed

uv run --extra dev --extra models --extra local-audio --extra quicktalk-cuda ruff check \
  apps/api/routes/health.py apps/api/routes/sessions.py apps/api/routes/tts_preview.py \
  opentalking/core/config.py opentalking/models/quicktalk/adapter.py \
  opentalking/providers/stt/factory.py opentalking/providers/tts/factory.py \
  opentalking/providers/tts/providers.py opentalking/providers/tts/local_cosyvoice \
  opentalking/providers/tts/local_qwen3_tts scripts/download_local_audio_models.py \
  scripts/local_cosyvoice_service.py scripts/local_qwen3_tts_service.py \
  tests/unit/test_local_audio_providers.py tests/unit/test_local_audio_frontend.py \
  tests/unit/test_voice_store.py apps/api/tests/test_voice_labels.py apps/api/tests/test_tts_preview.py
# All checks passed

cd apps/web && npm run typecheck && npm run build
# passed
```

已知全仓 ruff 仍有旧 baseline lint：`opentalking/pipeline/session/runner.py` 和 `opentalking/pipeline/speak/synthesis_runner.py` 有既存 `E402`/unused import，本轮没有扩大处理范围。

## 后续建议

1. 保持默认 `Fun-CosyVoice3-0.5B-2512`，把 `CosyVoice-300M` 作为前端可选实验项。当前优化已把第一轮首帧压到约 3.0s，继续降低需要换更低首包 TTS 或进一步约束 LLM 首句长度。
2. 做更好的内置 prompt 音色库，保证每个系统音色有不同 prompt audio/prompt_text，否则听起来会趋同。
3. 针对卡顿优先优化 TTS 首包：文本切分、prompt 长度、CosyVoice 参数和更轻量 TTS 对照，比继续优化 ASR 更有收益。
4. 如果要 8G 单卡跑完整链路，需要单独做显存压力测试，不要只看 24GB 卡上的 per-process 数值线性推断。
