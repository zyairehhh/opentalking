from __future__ import annotations

from fastapi import APIRouter

from opentalking.models.registry import list_available_models

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_registered_models() -> dict[str, list[str]]:
    return {"models": list_available_models()}
