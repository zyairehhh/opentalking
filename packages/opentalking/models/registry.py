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


def get_adapter(model_type: str):  # pragma: no cover — temporary stub
    """Legacy hook kept for import compatibility.

    Local model adapters were removed; synthesis now flows through
    omnirt-backed providers. Direct callers will be migrated in Phase D
    to use opentalking.core.registry instead.
    """
    raise NotImplementedError(
        f"local model adapter '{model_type}' is no longer in-tree; route via omnirt"
    )


def register_model(model_type: str):  # pragma: no cover — temporary stub
    def decorator(cls):
        return cls
    return decorator
