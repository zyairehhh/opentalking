"""Environment-variable helpers for the synthesis pipeline.

Extracted from synthesis_runner.py to keep that file focused on orchestration.
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


def default_flashtalk_ws_url() -> str:
    server_host = os.environ.get("SERVER_HOST", "localhost")
    return os.environ.get("OPENTALKING_FLASHTALK_WS_URL", f"ws://{server_host}:8765")


def env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None and name.startswith("FLASHTALK_"):
        raw = os.environ.get(f"OPENTALKING_{name}")
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        log.warning("Invalid %s=%r, using %.1f", name, raw, default)
        return default


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None and name.startswith("FLASHTALK_"):
        raw = os.environ.get(f"OPENTALKING_{name}")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        log.warning("Invalid %s=%r, using %d", name, raw, default)
        return default


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None and name.startswith("FLASHTALK_"):
        raw = os.environ.get(f"OPENTALKING_{name}")
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}
