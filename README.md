<h1 align="center">OpenTalking</h1>

<p align="center">
  <b>面向实时对话的开源数字人产线：LLM、TTS、WebRTC、角色音色与外部 OmniRT 模型服务</b>
</p>

<p align="center">
  <a href="./README.en.md">English</a> ·
  <a href="https://github.com/datascale-ai/opentalking">GitHub</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18-61dafb.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/WebRTC-realtime-orange.svg" alt="WebRTC">
</p>

<p align="center">
  <a href="#当前能力">当前能力</a> ·
  <a href="#交流与联系">交流与联系</a> ·
  <a href="#视频展示">视频展示</a> ·
  <a href="#系统架构">系统架构</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="#致谢">致谢</a>
</p>

---

## 项目简介

OpenTalking 是一个开源实时数字人框架，目标是把 **数字人对话产品** 需要的链路串起来：前端交互、会话状态、LLM 回复、TTS/音色选择、打断控制、字幕事件、WebRTC 音视频播放，以及外部模型服务调用。

OpenTalking 关注的是 **产线编排层**，支持调用外部 API 和本地部署模型。默认入口优先让新用户先跑通完整链路，再按需要升级模型能力：

- **快速体验**：`demo-avatar / wav2lip`，不需要独立模型服务，适合第一次验证 API、TTS、WebRTC 和前端。
- **轻量适配验证**：`wav2lip / musetalk`，用于验证 Avatar 资产格式、模型适配器和端到端编排。
- **高质量部署**：通过 [OmniRT](https://github.com/datascale-ai/omnirt) 接入 FlashTalk-compatible WebSocket，面向消费级 GPU 和企业私有化推理服务。

## 当前能力

- **实时数字人对话**：LLM 回复、流式 TTS、字幕事件、状态事件和 WebRTC 播放在一条链路中完成。
- **FlashTalk 兼容路径**：支持本地或远端 FlashTalk 风格推理服务，作为高质量数字人渲染后端。
- **轻量 Demo 路径**：无需先下载完整 FlashTalk 权重，也可以跑通 API、TTS、WebRTC 和前端体验。
- **基础打断能力**：当前说话轮次已有打断基础，后续会升级为全链路取消。
- **OpenAI 兼容 LLM**：支持 DashScope、Ollama、vLLM、DeepSeek 等 OpenAI-compatible endpoint。
- **多部署形态**：支持单进程 demo、API/Worker 分布式模式和 Docker Compose。

## 交流与联系

欢迎加入 QQ 交流群，讨论实时数字人、FlashTalk、OmniRT、模型部署和产品场景。

<p align="center">
  <img src="docs/assets/images/qq_group_qrcode.png" alt="AI 数字人交流群二维码" width="280">
</p>

<p align="center">
  <b>AI 数字人交流群</b> · 群号：<code>1103327938</code>
</p>

## 视频展示

以下是 OpenTalking 典型场景演示视频，用来展示实时数字人产线在不同内容形态下的表现。横屏示例单独占一行，其余为竖屏，避免同一行里行高被横屏拉高导致竖屏看起来像被裁切。

<table>
  <tr>
    <td align="center" colspan="3">
      <b>实时手机录制</b><br/>
      <video src="https://github.com/user-attachments/assets/a3abce76-12c0-4b8b-844f-bbc5c3227dc7" controls width="100%"></video><br/>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" width="33%">
      <b>动漫脱口秀</b><br/>
      <video src="https://github.com/user-attachments/assets/b3743604-7f50-40d1-9248-f2df80ea7308" controls width="100%"></video><br/>
    </td>
    <td align="center" valign="top" width="33%">
      <b>电商带货</b><br/>
      <video src="https://github.com/user-attachments/assets/826c777b-a9d2-49be-a1a0-b295c8a4b498" controls width="100%"></video><br/>
    </td>
    <td align="center" valign="top" width="33%">
      <b>新闻女主播</b><br/>
      <video src="https://github.com/user-attachments/assets/34a282da-84cb-4134-bc4b-644356ac4f6f" controls width="100%"></video><br/>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="3">
      <table>
        <tr>
          <td align="center" valign="top" width="50%">
            <b>创意演唱 / 模仿秀</b><br/>
            <video src="https://github.com/user-attachments/assets/98e813c2-f170-4cc8-b934-a77a72061d2e" controls width="100%"></video><br/>
          </td>
          <td align="center" valign="top" width="50%">
            <b>陪伴类角色</b><br/>
            <video src="https://github.com/user-attachments/assets/44bbf1d9-75b1-4b0a-9704-c7f81c39446e" controls width="100%"></video><br/>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

## 系统架构

![OpenTalking Architecture](docs/assets/images/opentalking_architecture.png)

## 项目结构

```text
opentalking/
├── opentalking/                  # 编排层 Python 包（flat layout，根目录直接 import）
│   ├── core/                     # 接口协议、类型、配置、registry
│   ├── providers/                # 能力适配器（按"能力域 / 提供方"两级）
│   │   ├── stt/dashscope/        # 语音识别
│   │   ├── tts/{edge,dashscope_qwen,cosyvoice_ws,...}/   # 语音合成 + 复刻
│   │   ├── llm/openai_compatible/                        # 大语言模型
│   │   ├── rtc/aiortc/                                   # WebRTC 推流
│   │   └── synthesis/{flashtalk,flashhead,omnirt,mock}/  # 数字人合成（thin client）
│   ├── avatar/                   # 数字人形象资产管理
│   ├── voice/                    # 音色资产管理
│   ├── media/                    # 中性算子工具
│   ├── pipeline/{session,speak,recording}/   # 业务编排
│   └── runtime/                  # 进程胶水（task_consumer / bus / timing）
├── apps/
│   ├── api/                      # FastAPI 服务
│   ├── unified/                  # 单进程模式（开发友好）
│   ├── web/                      # React 前端
│   └── cli/                      # download_models / doctor / ...
├── configs/                      # YAML 配置（profiles / inference / synthesis）
├── docker/ + docker-compose.yml  # 容器化部署
├── scripts/                      # 辅助脚本（run_omnirt.sh / prepare-avatar.sh）
├── tests/                        # 单元 / 集成测试
└── docs/                         # 文档
```

## 快速开始

OpenTalking 的**编排层**（API + Worker + 前端）和**推理服务**（[OmniRT](https://github.com/datascale-ai/omnirt)）独立部署，可以在同一台机器，也可以分开。下面三条路径按"你想做什么"组织，按需挑一条。Docker 部署见 [docs/deployment.md](docs/deployment.md)。

### 公共第 0 步：装编排层

```bash
git clone https://github.com/datascale-ai/opentalking.git && cd opentalking
uv sync && uv pip install -e ".[dev]"
source .venv/bin/activate
cp .env.example .env
```

环境要求：UV, Python ≥ 3.10、Node.js ≥ 18、FFmpeg。

> 装完随时可以跑 `opentalking-doctor` 看清环境差什么。

### 路径 1：快速体验（推荐第一次跑）

**目标**：5 分钟内浏览器看到数字人对话，**不用 GPU、不用部署任何模型服务**。
**做法**：合成层用内置 Mock，LLM/STT/TTS 走云 API。

在 `.env` 里只需要填两件事：

```env
# 启用 Mock 合成（用 avatar 参考图作为静态视频帧）
OPENTALKING_INFERENCE_MOCK=1

# LLM：百炼 / DashScope / 任何 OpenAI 兼容 endpoint
OPENTALKING_LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENTALKING_LLM_API_KEY=sk-your-key
OPENTALKING_LLM_MODEL=qwen-flash

# STT：复用 LLM 的 DashScope key
DASHSCOPE_API_KEY=sk-your-key

# TTS：默认 Edge TTS，无需 key（什么都不用改）
```

启动两个终端：

```bash
# 终端 1：后端（单进程模式，内存 bus，不需要 Redis）
opentalking-unified

# 终端 2：前端
cd apps/web && npm ci && npm run dev -- --host 0.0.0.0
```

打开 `http://localhost:5173`，选内置 avatar 即可对话。视频帧是参考图静态展示——**完整链路（LLM 回复、TTS 流式、字幕事件、WebRTC 推流）都是真的**，只有口型同步是假的。

### 路径 2：轻量适配验证

**目标**：调 Avatar 资产、验证模型适配器、跑 wav2lip / musetalk / flashtalk 这类真实模型。
**做法**：本地或远端跑一个 SoulX FlashTalk WS 推理服务，OpenTalking 直连。

起一个推理后端（OmniRT / FlashTalk / 其它兼容服务都行）：

```bash
# 本地容器（默认 cuda；CPU 改 OMNIRT_BACKEND=cpu）
bash scripts/run_omnirt.sh

# 或远端：在 GPU 服务器上启动 SoulX FlashTalk 服务（参考其官方仓库）
```

`.env` 里去掉 Mock，指向推理服务：

```env
# OPENTALKING_INFERENCE_MOCK=0          ← 删除或注释
OPENTALKING_FLASHTALK_WS_URL=ws://<host>:8765

# 默认合成模型
OPENTALKING_DEFAULT_MODEL=flashtalk      # 或 musetalk / wav2lip（取决于你的推理服务支持）
```

> **`OPENTALKING_FLASHTALK_WS_URL` vs `OMNIRT_ENDPOINT`**：当前代码直连 FlashTalk WebSocket 协议（`OPENTALKING_FLASHTALK_WS_URL`）。`OMNIRT_ENDPOINT` 是后续把多模型推理统一收口到 OmniRT HTTP API 的占位字段，**当前不生效**。

启动方式跟路径 1 完全一样（`opentalking-unified` + 前端）。Avatar 配置见 [docs/avatar-format.md](docs/avatar-format.md)。

### 路径 3：高质量部署

**目标**：上 FlashTalk 14B / FlashHead 等高质量模型，面向私有化或生产。
**做法**：跟路径 2 一样配 `OPENTALKING_FLASHTALK_WS_URL`，再加多进程 / Redis / GPU 编排：

```env
OPENTALKING_FLASHTALK_WS_URL=ws://<gpu-host>:8765
OPENTALKING_DEFAULT_MODEL=flashtalk     # 或 flashhead

OPENTALKING_TORCH_DEVICE=cuda           # 编排层加速（音频 PCM 处理）
OPENTALKING_REDIS_URL=redis://redis:6379/0    # 多进程必须用真实 Redis
```

启动多进程模式（生产推荐）：

```bash
opentalking-api &
opentalking-worker &
# 前端单独构建并放到 nginx 后面
cd apps/web && npm ci && npm run build
```

Avatar manifest、推理 endpoint 映射、硬件 profile 见 [docs/configuration.md](docs/configuration.md) 和 [docs/hardware.md](docs/hardware.md)。

### 三条路径速查

| 路径 | 推理后端 | GPU 要求 | 适用场景 |
| --- | --- | --- | --- |
| 1. 快速体验 | 内置 Mock | 不需要 | 第一次跑、前端开发、链路验证 |
| 2. 轻量适配验证 | 本地 OmniRT + 轻量模型 | 入门 GPU 即可（3060+） | 模型/Avatar 适配开发 |
| 3. 高质量部署 | OmniRT + FlashTalk/FlashHead | 4090 / 910B | 私有化、生产、高质量 |

### 模型支持

| 模型 | 输入 | OpenTalking 接入 | 推荐路径 |
| --- | --- | --- | --- |
| `mock` | reference image | 内置静态帧 | 路径 1 |
| `wav2lip` | frames + audio | OmniRT 轻量口型同步 | 路径 2 |
| `musetalk` | full frames + audio | OmniRT 轻量 talking-head | 路径 2 |
| `soulx-flashtalk-14b` | portrait + audio | OmniRT 高质量 FlashTalk | 路径 3 |
| `soulx-flashhead-1.3b` | portrait + audio | 直连 FlashHead WebSocket | 路径 3 |


## Roadmap

- [x] **实时数字人基础体验**  
  Web 控制台、LLM 对话、TTS、字幕事件、WebRTC 音视频播放。

- [ ] **更自然的实时对话（进行中）**  
  支持打断、会话状态、低延迟响应、音画同步和异常恢复。

- [ ] **OmniRT 模型服务接入**  
  通过 OmniRT 统一调用 FlashTalk、轻量 talking-head、ASR、语音合成和音色服务。

- [ ] **消费级显卡可用**  
  面向 RTX 3090 / 4090 提供轻量模型、单卡实时配置和端到端 benchmark。

- [ ] **高质量私有化部署（进行中）**  
  面向企业私有化场景，支持外部 OmniRT 推理服务、容量调度、健康检查和生产监控；昇腾 910B 等企业级 GPU/NPU 路线已在构建中。

- [ ] **自定义角色和音色**  
  支持角色配置、内置音色选择、上传参考音频、自然语言描述音色，并通过 OmniRT 生成语音。

- [ ] **Agent 与记忆能力**  
  对接 OpenClaw 或外部 Agent，复用其 memory、工具调用和知识库能力。

- [ ] **生产级平台能力**  
  多会话调度、观测指标、安全合规、授权音色、合成内容标识。

## 文档

- [快速开始](docs/quickstart.md)
- [FlashTalk + OmniRT 部署](docs/flashtalk-omnirt.md)
- [架构说明](docs/architecture.md)
- [配置说明](docs/configuration.md)
- [部署文档](docs/deployment.md)（Docker Compose、分布式部署）
- [硬件指南](docs/hardware.md)
- [模型适配](docs/model-adapter.md)
- [贡献指南](CONTRIBUTING.md)（开发环境、CLI 工具、ruff / mypy / pytest）

## 致谢

OpenTalking 参考并受益于实时数字人生态中的优秀项目：

- [SoulX-FlashTalk](https://github.com/Soul-AILab/SoulX-FlashTalk) 和 [SoulX-FlashTalk-14B](https://huggingface.co/Soul-AILab/SoulX-FlashTalk-14B)
- [LiveTalking](https://github.com/lipku/LiveTalking)
- [OmniRT](https://github.com/datascale-ai/omnirt)
- [Edge TTS](https://github.com/rany2/edge-tts)
- [aiortc](https://github.com/aiortc/aiortc)
- [Wan Video](https://github.com/Wan-Video)

## License

[Apache License 2.0](LICENSE)
