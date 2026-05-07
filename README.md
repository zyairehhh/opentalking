# OpenTalking

> 实时陪伴型数字人开源框架 · 一键部署 · 自定义形象 / 音色 / 性格

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
  <a href="https://github.com/datascale-ai/omnirt"><img alt="Inference" src="https://img.shields.io/badge/inference-omnirt-orange"></a>
</p>

![OpenTalking Architecture](docs/assets/images/opentalking_architecture.png)

---

## ✨ 核心能力

- 🎭 **可配置数字人**：形象 / 音色 / 性格 / 技能四维度自定义，前端表单即可创建
- ⚡ **实时交互**：< 2s 首响，支持中途打断
- 🔧 **多硬件**：3090 / 4090 / 910B / CPU 同一套架构
- 🎯 **分层模型**：默认轻量（数百 MB），可选高质量（FlashTalk 14B）
- 🔌 **解耦推理**：基于 [omnirt](https://github.com/datascale-ai/omnirt) 推理服务，扩展模型零侵入业务代码

## 🚀 快速开始（3 行命令）

```bash
git clone https://github.com/<org>/opentalking && cd opentalking
cp .env.example .env                  # 按需填 STT/LLM 凭据
bash scripts/install.sh               # 自动探测硬件 + 拉起所有服务
```

打开 http://localhost:5173 选择内置 avatar 即可对话。

## 📐 架构总览

```
                ┌────────────┐
   user ──HTTP──▶  apps/api  │──▶ Redis ──▶ apps/worker ──▶ omnirt
                │ apps/web   │                  │
                └────────────┘                  ▼
                                          providers/{stt,tts,llm,rtc}
```

**OpenTalking = 业务编排（本仓） + 推理服务（omnirt） + 前端控制台**

所有模型推理（FlashTalk / MuseTalk / Wav2Lip / 音色克隆）由 omnirt 承担，本仓只持有 thin client。

详细设计见 [docs/architecture-review.md](docs/architecture-review.md)。

## 🎨 自定义数字人

1. 进入"角色管理 → 新建"
2. 上传一张参考图（建议正面、肩部以上）
3. 选择合成模型（musetalk / flashtalk / wav2lip）
4. 选择音色（preset 或上传 30s 音频克隆）
5. 写角色 prompt（例："你是一个温柔的语言教师..."）
6. 保存 → 在主页选中 → 开始对话

数字人配置 schema 见 [docs/avatar-format.md](docs/avatar-format.md)。

## 🛠 部署形态

| 形态 | 命令 | 适用 |
|---|---|---|
| Docker（推荐） | `bash scripts/install.sh docker` | 生产 / 一键体验 |
| Native | `bash scripts/install.sh native` | 开发 |
| Dev unified | `docker compose -f deploy/compose/docker-compose.dev.yml up` | 前端联调（无 GPU） |

## 🖥 硬件 profile

| profile | 默认合成模型 | 备注 |
|---|---|---|
| cuda-4090 | musetalk | FlashTalk 可选下载 |
| cuda-3090 | wav2lip | 体积小，跑得动 |
| ascend-910b | flashtalk | 高质量首选 |
| cpu-demo | wav2lip | 仅功能验证 |

profile 详细说明见 [docs/hardware.md](docs/hardware.md)。

## 📚 文档

- [架构设计](docs/architecture-review.md) · [架构现状](docs/architecture.md)
- [部署指南](docs/deployment.md)
- [API 参考](docs/api-reference.md)
- [Avatar manifest 规范](docs/avatar-format.md)
- [硬件适配](docs/hardware.md)
- [配置说明](docs/configuration.md)

## 🔗 上下游

- 推理服务：[omnirt](https://github.com/datascale-ai/omnirt) — 多模态生成统一运行时
- 月度路线图：[docs/2026-05-monthly-roadmap.md](docs/2026-05-monthly-roadmap.md)

## 🤝 贡献

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

<p align="center">
  <img src="docs/assets/images/qq_group_qrcode.png" alt="AI 数字人交流群二维码" width="280">
</p>

## 📄 License

[Apache 2.0](LICENSE)
