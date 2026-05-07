# OpenTalking

> Real-time companion digital-human framework · one-click deploy · custom avatar / voice / persona

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
  <a href="https://github.com/datascale-ai/omnirt"><img alt="Inference" src="https://img.shields.io/badge/inference-omnirt-orange"></a>
</p>

![OpenTalking Architecture](docs/assets/images/opentalking_architecture.png)

---

## ✨ Features

- 🎭 **Configurable digital human** — appearance / voice / persona / skill, all editable in the UI
- ⚡ **Real-time** — < 2s first response, mid-utterance interrupt
- 🔧 **Multi-hardware** — 3090 / 4090 / 910B / CPU on a single architecture
- 🎯 **Tiered models** — light by default (hundreds of MB), high-quality FlashTalk 14B optional
- 🔌 **Decoupled inference** — backed by [omnirt](https://github.com/datascale-ai/omnirt); adding new models requires zero changes to business code

## 🚀 Quick start (3 commands)

```bash
git clone https://github.com/<org>/opentalking && cd opentalking
cp .env.example .env                  # fill in STT/LLM credentials as needed
bash scripts/install.sh               # auto-detects hardware, brings up everything
```

Open http://localhost:5173 — pick a built-in avatar and start talking.

## 📐 Architecture

```
                ┌────────────┐
   user ──HTTP──▶  apps/api  │──▶ Redis ──▶ apps/worker ──▶ omnirt
                │ apps/web   │                  │
                └────────────┘                  ▼
                                          providers/{stt,tts,llm,rtc}
```

**OpenTalking = orchestration (this repo) + inference (omnirt) + console (web)**

All model inference (FlashTalk / MuseTalk / Wav2Lip / voice cloning) runs in omnirt; this repo holds thin clients only.

Design: [docs/architecture-review.md](docs/architecture-review.md).

## 🎨 Customise a digital human

1. Avatar manager → New
2. Upload a reference image (frontal, shoulder-up recommended)
3. Pick synthesis model (musetalk / flashtalk / wav2lip)
4. Pick voice (preset or upload 30 s for cloning)
5. Write the persona prompt
6. Save → select on home → start chatting

Schema: [docs/avatar-format.md](docs/avatar-format.md).

## 🛠 Deployment modes

| Mode | Command | When |
|---|---|---|
| Docker (recommended) | `bash scripts/install.sh docker` | production / quick demo |
| Native | `bash scripts/install.sh native` | local development |
| Dev unified | `docker compose -f deploy/compose/docker-compose.dev.yml up` | frontend dev (no GPU) |

## 🖥 Hardware profiles

| profile | default synthesis | notes |
|---|---|---|
| cuda-4090 | musetalk | FlashTalk optional |
| cuda-3090 | wav2lip | small footprint |
| ascend-910b | flashtalk | high quality |
| cpu-demo | wav2lip | smoke verify only |

## 📚 Docs

- [Architecture](docs/architecture-review.md) · [Current state](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [API reference](docs/api-reference.md)
- [Avatar manifest](docs/avatar-format.md)
- [Hardware](docs/hardware.md)
- [Configuration](docs/configuration.md)

## 🔗 Upstream

- Inference: [omnirt](https://github.com/datascale-ai/omnirt) — multimodal generation runtime

<p align="center">
  <img src="docs/assets/images/qq_group_qrcode.png" alt="AI Digital Human QQ group QR code" width="280">
</p>

## 📄 License

[Apache 2.0](LICENSE)
