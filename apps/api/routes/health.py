from __future__ import annotations

from fastapi import APIRouter, Request

from opentalking.core.queue_status import get_flashtalk_queue_status
from opentalking.providers.stt.factory import stt_status

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "status": "ok",
        "tts_provider": getattr(settings, "normalized_tts_provider", "edge"),
        **{f"stt_{key}": value for key, value in stt_status().items()},
    }


@router.get("/queue/status")
async def queue_status(request: Request) -> dict[str, bool | int]:
    try:
        return await get_flashtalk_queue_status(request.app.state.redis)
    except Exception:
        return {"slot_occupied": False, "queue_size": 0}
