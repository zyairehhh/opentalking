<h1 align="center">OpenTalking</h1>

<p align="center">
  <b>Open-source real-time digital-human pipeline: LLM, TTS, WebRTC, character voices, and external OmniRT model services</b>
</p>

<p align="center">
  <a href="./README.md">中文</a> ·
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
  <a href="#capabilities">Capabilities</a> ·
  <a href="#community">Community</a> ·
  <a href="#demo-videos">Demo videos</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#quickstart">Quickstart</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="#acknowledgements">Acknowledgements</a>
</p>

---

## Overview

OpenTalking is an open-source real-time digital-human framework. The goal is to wire up everything a **digital-human conversational product** needs: frontend interaction, session state, LLM replies, TTS / voice selection, barge-in control, subtitle events, WebRTC media playback, and calls into external model services.

OpenTalking focuses on the **pipeline orchestration layer** and supports both external API providers and locally deployed models. The default entrypoint is optimized for getting a first working loop quickly, then upgrading model quality as needed:

- **Quick experience**: `demo-avatar / wav2lip`, no standalone model service required, ideal for validating the API, TTS, WebRTC, and frontend.
- **Lightweight adapter validation**: `wav2lip / musetalk`, useful for Avatar assets, model adapters, and end-to-end orchestration checks.
- **High-quality deployment**: FlashTalk-compatible WebSocket via [OmniRT](https://github.com/datascale-ai/omnirt), targeting consumer GPUs and enterprise private inference services.

## Capabilities

- **Real-time digital-human dialogue**: LLM reply, streaming TTS, subtitle events, status events, and WebRTC playback all happen in one pipeline.
- **FlashTalk-compatible path**: speaks the FlashTalk WebSocket protocol, with either local or remote inference servers behind it as the high-quality renderer.
- **Lightweight demo path**: the API, TTS, WebRTC, and frontend can be exercised without first downloading the full FlashTalk weights.
- **Basic barge-in**: current speaking turns can already be interrupted; full pipeline cancellation is on the roadmap.
- **OpenAI-compatible LLM**: works with DashScope, Ollama, vLLM, DeepSeek, and any other OpenAI-compatible endpoint.
- **Multiple deployment shapes**: single-process demo, distributed API + Worker mode, and Docker Compose.

## Community

Join our QQ group to discuss real-time digital humans, FlashTalk, OmniRT, model deployment, and product use cases.

<p align="center">
  <img src="docs/assets/images/qq_group_qrcode.png" alt="AI Digital Human QQ group QR code" width="280">
</p>

<p align="center">
  <b>AI Digital Human QQ group</b> · ID: <code>1103327938</code>
</p>

## Demo videos

These demo videos show how the OpenTalking pipeline behaves across different real-time digital-human scenarios. The landscape clip spans the full width on its own row; portrait clips follow so row height is not dominated by the landscape video (which can make portrait previews look vertically clipped).

<table>
  <tr>
    <td align="center" colspan="3">
      <b>Realtime mobile capture</b><br/>
      <video src="https://github.com/user-attachments/assets/a3abce76-12c0-4b8b-844f-bbc5c3227dc7" controls width="100%"></video><br/>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" width="33%">
      <b>Anime stand-up</b><br/>
      <video src="https://github.com/user-attachments/assets/b3743604-7f50-40d1-9248-f2df80ea7308" controls width="100%"></video><br/>
    </td>
    <td align="center" valign="top" width="33%">
      <b>E-commerce livestream</b><br/>
      <video src="https://github.com/user-attachments/assets/826c777b-a9d2-49be-a1a0-b295c8a4b498" controls width="100%"></video><br/>
    </td>
    <td align="center" valign="top" width="33%">
      <b>News anchor</b><br/>
      <video src="https://github.com/user-attachments/assets/34a282da-84cb-4134-bc4b-644356ac4f6f" controls width="100%"></video><br/>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="3">
      <table>
        <tr>
          <td align="center" valign="top" width="50%">
            <b>Singing / impression</b><br/>
            <video src="https://github.com/user-attachments/assets/98e813c2-f170-4cc8-b934-a77a72061d2e" controls width="100%"></video><br/>
          </td>
          <td align="center" valign="top" width="50%">
            <b>Companion character</b><br/>
            <video src="https://github.com/user-attachments/assets/44bbf1d9-75b1-4b0a-9704-c7f81c39446e" controls width="100%"></video><br/>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

## Architecture

![OpenTalking Architecture](docs/assets/images/opentalking_architecture.png)

## Project layout

```text
opentalking/
├── src/opentalking/
│   ├── core/         # config, interface protocols, type definitions
│   ├── engine/       # FlashTalk-compatible local inference path
│   ├── server/       # distributed WebSocket inference service
│   ├── models/       # avatar model adapters
│   ├── worker/       # session orchestration
│   ├── llm/          # OpenAI-compatible LLM client
│   ├── tts/          # TTS adapters
│   ├── rtc/          # WebRTC transport
│   ├── voices/       # voice profiles and provider integration
│   └── events/       # SSE and runtime events
├── apps/
│   ├── api/          # FastAPI service
│   ├── unified/      # single-process mode
│   ├── web/          # React frontend
│   └── cli/          # model download, video generation, demo tools
├── configs/          # YAML config samples
├── docker/           # Docker Compose
├── scripts/          # startup and deployment scripts
├── tests/            # unit / integration tests
└── docs/             # documentation
```

## Quickstart

OpenTalking decouples the **orchestration layer** (API + Worker + frontend) from the **inference service** ([OmniRT](https://github.com/datascale-ai/omnirt))—they can run on the same machine or on separate hosts. Pick one of the two paths below.

> **Three things to remember**
> - LLM / STT / TTS go through cloud APIs (an OpenAI-compatible key is enough; TTS defaults to Edge TTS, no key).
> - The inference service runs independently. **For the first run you can use the built-in Mock and skip a real backend**—works on CPU.
> - Run `opentalking-doctor` any time to see what's missing.

### Path A: Docker (fastest, 5-minute experience)

For **first-run** and **single-host** users. One command brings up Redis + API + Worker + frontend with mock synthesis.

```bash
git clone https://github.com/datascale-ai/opentalking.git && cd opentalking
cp .env.example .env                               # set OPENTALKING_LLM_API_KEY
docker compose up                                  # mock synthesis, runs on CPU
```

Open `http://localhost:5173`, pick a built-in avatar, and start chatting.

Upgrade to real synthesis (NVIDIA GPU + nvidia-container-toolkit required):

```bash
docker compose --profile gpu -f docker-compose.yml -f docker-compose.gpu.yml up
```

This additionally pulls and starts an [OmniRT](https://github.com/datascale-ai/omnirt) container and switches API/Worker to the real inference path.

### Path B: Python venv (development / multi-host deployments)

For **frontend work**, **adapter development**, and **OpenTalking-and-inference-on-different-hosts** scenarios. The orchestration layer is installed locally; the inference backend is **yours to control**.

```bash
# 1. Install the orchestration layer
git clone https://github.com/datascale-ai/opentalking.git && cd opentalking
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# 2. Edit .env
#    - At minimum set OPENTALKING_LLM_API_KEY (DashScope / OpenAI / Bailian)
#    - Pick one inference path:
#       (a) Built-in mock:    add  OPENTALKING_INFERENCE_MOCK=1
#       (b) Local OmniRT:     bash scripts/run_omnirt.sh   then write OMNIRT_ENDPOINT
#       (c) Remote OmniRT:    just point OMNIRT_ENDPOINT at it
$EDITOR .env

# 3. Health check
opentalking-doctor

# 4. Start
opentalking-unified                                 # single process, in-memory bus, no redis needed
# Multi-process:
# opentalking-api & opentalking-worker &
```

Frontend:

```bash
cd apps/web && npm ci && npm run dev -- --host 0.0.0.0
```

Open `http://localhost:5173`.

Requirements: Python ≥ 3.10, Node.js ≥ 18, FFmpeg; distributed mode also requires Redis.

### About the inference service (OmniRT)

OmniRT is an independent multimodal inference runtime serving FlashTalk / MuseTalk / Wav2Lip and others. It does **not** need to live on the same machine as OpenTalking:

| Your situation | Recommended approach |
|---|---|
| 5-minute demo | Path A default (mock) |
| Single host with GPU, want real output | `docker compose --profile gpu` or `bash scripts/run_omnirt.sh` |
| Remote GPU server already available | Run OmniRT there, set `OMNIRT_ENDPOINT=http://<gpu-host>:9000` locally |
| Enterprise / Ascend 910B | See the [OmniRT docs](https://github.com/datascale-ai/omnirt) |

Full notes in [docs/quickstart.en.md](docs/quickstart.en.md).

### Supported models

| Model | Input | OpenTalking integration |
| --- | --- | --- |
| `mock` (default, no GPU required) | reference image | Pipeline / frontend validation only; not real lip-sync |
| `wav2lip` | frames + audio | OmniRT, lightweight lip-sync |
| `musetalk` | full frames + audio | OmniRT, lightweight talking-head |
| `soulx-flashtalk-14b` | portrait + audio | OmniRT, high-quality FlashTalk |
| `soulx-flashhead-1.3b` | portrait + audio | direct FlashHead WebSocket |


## Roadmap

- [x] **Real-time digital-human baseline**  
  Web console, LLM dialogue, TTS, subtitle events, WebRTC media playback.

- [ ] **More natural realtime dialogue(in progress)**  
  Barge-in, session state, low-latency response, audio-video sync, error recovery.

- [ ] **OmniRT model service integration**  
  Unified access via OmniRT for FlashTalk, lightweight talking-head, ASR, speech synthesis, and voice services.

- [ ] **Consumer-grade GPU support**  
  Lightweight models, single-card realtime configs, end-to-end benchmarks for RTX 3090 / 4090.

- [ ] **High-quality private deployment(in progress)**  
  Enterprise private deployment with external OmniRT inference, capacity scheduling, health checks, production monitoring; Ascend 910B and similar enterprise GPU / NPU paths in progress.

- [ ] **Custom characters and voices**  
  Character config, built-in voice selection, reference audio upload, natural-language voice description, and OmniRT-driven voice synthesis.

- [ ] **Agent and memory capabilities**  
  Integration with OpenClaw or external agents to reuse their memory, tool use, and knowledge-base capabilities.

- [ ] **Production-grade platform**  
  Multi-session scheduling, observability, security and compliance, licensed voices, synthetic-content provenance.

## Documentation

- [Quickstart](docs/quickstart.en.md)
- [FlashTalk + OmniRT deployment](docs/flashtalk-omnirt.en.md)
- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Deployment](docs/deployment.md) (Docker Compose, distributed deployment)
- [Hardware guide](docs/hardware.md)
- [Model adapters](docs/model-adapter.md)
- [Contributing](CONTRIBUTING.md) (dev environment, CLI tools, ruff / mypy / pytest)

## Acknowledgements

OpenTalking draws inspiration from and benefits from outstanding projects in the real-time digital-human ecosystem:

- [SoulX-FlashTalk](https://github.com/Soul-AILab/SoulX-FlashTalk) and [SoulX-FlashTalk-14B](https://huggingface.co/Soul-AILab/SoulX-FlashTalk-14B)
- [LiveTalking](https://github.com/lipku/LiveTalking)
- [OmniRT](https://github.com/datascale-ai/omnirt)
- [Edge TTS](https://github.com/rany2/edge-tts)
- [aiortc](https://github.com/aiortc/aiortc)
- [Wan Video](https://github.com/Wan-Video)

## License

[Apache License 2.0](LICENSE)
