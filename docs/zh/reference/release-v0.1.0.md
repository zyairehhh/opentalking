# v0.1.0 发版验证

本文记录 OpenTalking v0.1.0 的发版验证证据，供维护者确认 GitHub Release、Python artifacts 和 GHCR Docker 镜像是否来自预期的 release commit。

## 发版坐标

| 项目 | 值 |
| --- | --- |
| 发版分支 | `release-v0.1.0` |
| 发版 commit | `a7e739c28f8edb562a728ca189550188a9e0b4cd` |
| 发版 tag | `v0.1.0` |
| GitHub Release | <https://github.com/datascale-ai/opentalking/releases/tag/v0.1.0> |
| Release workflow | <https://github.com/datascale-ai/opentalking/actions/runs/27564580360> |

## GitHub Release Artifacts

Release workflow 已成功完成，并在 GitHub Release 中挂载以下 Python artifacts：

- `opentalking-0.1.0-py3-none-any.whl`
- `opentalking-0.1.0.tar.gz`

验证命令：

```bash
python -m build
python -m twine check dist/*
```

release worktree 上观察到的结果：

```text
Checking dist/opentalking-0.1.0-py3-none-any.whl: PASSED
Checking dist/opentalking-0.1.0.tar.gz: PASSED
```

## Docker 镜像

OpenTalking 本次发布三个 GHCR 镜像，因为运行时被拆成可独立部署的服务。

| 镜像 | 用途 |
| --- | --- |
| `ghcr.io/datascale-ai/opentalking-web:v0.1.0` | 由 Nginx 托管的 React/Vite Web 控制台 |
| `ghcr.io/datascale-ai/opentalking-api:v0.1.0` | FastAPI 控制面和对外 HTTP API |
| `ghcr.io/datascale-ai/opentalking-worker:v0.1.0` | 异步 worker、WebRTC 与任务执行服务 |

GHCR packages 改为 public 后，在没有 Docker 登录态的 `146` 验证机上匿名 manifest 检查成功：

```bash
docker manifest inspect ghcr.io/datascale-ai/opentalking-api:v0.1.0
docker manifest inspect ghcr.io/datascale-ai/opentalking-worker:v0.1.0
docker manifest inspect ghcr.io/datascale-ai/opentalking-web:v0.1.0
```

观察到的 manifest digest hints：

```text
opentalking-api    sha256:94b64e8992105e5dbb8cf36f58896370f888da0703b989f994c962d6cd72d94b
opentalking-worker sha256:5eb3b1a8a453cd7a7f694ad892c455c6b84a7b11a55268f9ef2c7af63afd0164
opentalking-web    sha256:fcb23be357ed1a3e8d621029d39efcbf9c124ed10d85f00a22baf38291c060b6
```

体积较小的 `opentalking-web` 镜像也完成了匿名 pull：

```text
Digest: sha256:c70f5d01ad433fe904bcd95f190c377b2a29d9a3abf144b184cbd5f2fbaa8602
Status: Downloaded newer image for ghcr.io/datascale-ai/opentalking-web:v0.1.0
```

API 和 worker 镜像较大，因为包含 OpenTalking 服务栈所需的 Python 运行时依赖。发版验收中，匿名 manifest 可读证明 GHCR public 可访问；下面的 runtime smoke tests 则验证 v0.1.0 镜像能在 `146` 机器上启动。

## Runtime Smoke Tests

以下 smoke tests 在 `8.92.9.146` 上执行，release worktree 位于 `/data2/zhongyi/opentalking-release-v0.1.0`。

### Web

```text
opentalking-web-v010-smoke Up 3 seconds 0.0.0.0:18082->80/tcp, :::18082->80/tcp
web_http_ok bytes=697
```

### API

```text
opentalking-api-v010-smoke Up 12 seconds 0.0.0.0:18080->8000/tcp, :::18080->8000/tcp
api_health_ok ok tts_provider edge stt_provider dashscope
```

### Worker

worker 镜像可以导入 release 包并启动 FastAPI worker 服务；任务消费者路径需要 Redis sidecar。

```text
worker_import_ok 0.1.0
opentalking-worker-v010-smoke Up 12 seconds 0.0.0.0:18083->9001/tcp, :::18083->9001/tcp
/docs code=200 bytes=1017
/openapi.json code=200 bytes=3747
```

## 验收清单

- `datascale-ai/opentalking` 上存在 release 分支。
- `v0.1.0` tag 指向 release commit。
- GitHub Release 已创建，并包含 wheel 与 source distribution assets。
- Release workflow 成功完成。
- GHCR package visibility 已足够公开，支持匿名 manifest inspection。
