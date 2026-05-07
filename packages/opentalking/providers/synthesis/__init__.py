"""Synthesis providers (audio → video frames).

All implementations are thin clients backed by the omnirt inference runtime.
"""

# Built-in synthesis provider keys exposed via /catalog/synthesis & /models.
# Aligns with configs/inference/omnirt.yaml endpoint names.
SYNTHESIS_PROVIDERS = ("flashtalk", "musetalk", "wav2lip", "flashhead")


def list_available_synthesis() -> list[str]:
    return list(SYNTHESIS_PROVIDERS)
