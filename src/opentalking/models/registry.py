from __future__ import annotations

# Legacy registry — superseded by opentalking.core.registry in the v2 layout.
# Kept as a thin shim during the refactor; will be deleted after Phase D wiring
# moves all consumers to the new registry.

_REMOTE_MODELS: set[str] = {"flashtalk", "flashhead", "musetalk", "wav2lip"}


def list_models() -> list[str]:
    return sorted(_REMOTE_MODELS)


def list_available_models() -> list[str]:
    return list_models()


def ensure_models_imported() -> None:
    return None
