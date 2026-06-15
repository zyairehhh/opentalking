# v0.1.0 Release Verification

This runbook records the verification evidence for the OpenTalking v0.1.0 release. Use it to confirm that the GitHub Release, Python artifacts, and GHCR Docker images were produced from the intended release commit.

## Release Coordinates

| Item | Value |
| --- | --- |
| Release branch | `release-v0.1.0` |
| Release commit | `a7e739c28f8edb562a728ca189550188a9e0b4cd` |
| Release tag | `v0.1.0` |
| GitHub Release | <https://github.com/datascale-ai/opentalking/releases/tag/v0.1.0> |
| Release workflow | <https://github.com/datascale-ai/opentalking/actions/runs/27564580360> |

## GitHub Release Artifacts

The release workflow completed successfully and attached these Python artifacts to the GitHub Release:

- `opentalking-0.1.0-py3-none-any.whl`
- `opentalking-0.1.0.tar.gz`

Verification command:

```bash
python -m build
python -m twine check dist/*
```

Observed result on the release worktree:

```text
Checking dist/opentalking-0.1.0-py3-none-any.whl: PASSED
Checking dist/opentalking-0.1.0.tar.gz: PASSED
```

## Docker Images

OpenTalking publishes three GHCR images because the runtime is split into independently deployable services.

| Image | Purpose |
| --- | --- |
| `ghcr.io/datascale-ai/opentalking-web:v0.1.0` | React/Vite web console served by Nginx |
| `ghcr.io/datascale-ai/opentalking-api:v0.1.0` | FastAPI control plane and public HTTP API |
| `ghcr.io/datascale-ai/opentalking-worker:v0.1.0` | Async worker and WebRTC/task execution service |

After the GHCR packages were made public, anonymous manifest checks succeeded from the `146` host without Docker login credentials:

```bash
docker manifest inspect ghcr.io/datascale-ai/opentalking-api:v0.1.0
docker manifest inspect ghcr.io/datascale-ai/opentalking-worker:v0.1.0
docker manifest inspect ghcr.io/datascale-ai/opentalking-web:v0.1.0
```

Observed manifest digest hints:

```text
opentalking-api    sha256:94b64e8992105e5dbb8cf36f58896370f888da0703b989f994c962d6cd72d94b
opentalking-worker sha256:5eb3b1a8a453cd7a7f694ad892c455c6b84a7b11a55268f9ef2c7af63afd0164
opentalking-web    sha256:fcb23be357ed1a3e8d621029d39efcbf9c124ed10d85f00a22baf38291c060b6
```

The smaller `opentalking-web` image was also pulled anonymously from GHCR:

```text
Digest: sha256:c70f5d01ad433fe904bcd95f190c377b2a29d9a3abf144b184cbd5f2fbaa8602
Status: Downloaded newer image for ghcr.io/datascale-ai/opentalking-web:v0.1.0
```

The API and worker images are large because they include Python runtime dependencies for the OpenTalking service stack. For release acceptance, anonymous manifest access proves public GHCR availability; the runtime smoke tests below verify that the v0.1.0 images start correctly on the `146` host.

## Runtime Smoke Tests

The following smoke tests were run on `8.92.9.146` from `/data2/zhongyi/opentalking-release-v0.1.0`.

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

The worker image imports the release package and starts the FastAPI worker service. A Redis sidecar is required for the task consumer path.

```text
worker_import_ok 0.1.0
opentalking-worker-v010-smoke Up 12 seconds 0.0.0.0:18083->9001/tcp, :::18083->9001/tcp
/docs code=200 bytes=1017
/openapi.json code=200 bytes=3747
```

## Acceptance Checklist

- Release branch exists on `datascale-ai/opentalking`.
- `v0.1.0` tag points to the release commit.
- GitHub Release exists and contains wheel and source distribution assets.
- Release workflow completed successfully.
- GHCR package visibility is public enough for anonymous manifest inspection.
