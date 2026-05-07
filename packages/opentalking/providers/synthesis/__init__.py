"""Synthesis providers (audio → video frames).

All implementations are thin clients backed by the omnirt inference runtime.
The same OmniRTSynthesisAdapter class is registered under three synthesis keys;
each instance binds to a different omnirt model name at construction.
"""

from opentalking.core.registry import register
from opentalking.providers.synthesis.omnirt import OmniRTSynthesisAdapter

# One class, three capability keys — model name is supplied at instantiation
# from configs/inference/omnirt.yaml.
register("synthesis", "flashtalk")(OmniRTSynthesisAdapter)
register("synthesis", "musetalk")(OmniRTSynthesisAdapter)
register("synthesis", "wav2lip")(OmniRTSynthesisAdapter)

# FlashHead has its own dedicated WS protocol (kept separate, not via omnirt yet).
from opentalking.providers.synthesis.flashhead.ws_client import FlashHeadWSClient  # noqa: E402

register("synthesis", "flashhead")(FlashHeadWSClient)

SYNTHESIS_PROVIDERS = ("flashtalk", "musetalk", "wav2lip", "flashhead")


def list_available_synthesis() -> list[str]:
    return list(SYNTHESIS_PROVIDERS)


__all__ = [
    "OmniRTSynthesisAdapter",
    "SYNTHESIS_PROVIDERS",
    "list_available_synthesis",
]
