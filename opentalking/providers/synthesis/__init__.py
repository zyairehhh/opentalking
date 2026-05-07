"""Synthesis providers (audio → video frames).

Real backends are thin clients to the omnirt inference runtime. A `mock`
provider is also registered for frontend-only dev and first-run experiences.
"""

from opentalking.core.registry import register
from opentalking.providers.synthesis.omnirt import OmniRTSynthesisAdapter
from opentalking.providers.synthesis import mock as _mock  # noqa: F401  side-effect register

# One class, three capability keys — model name is supplied at instantiation
# from configs/inference/omnirt.yaml.
register("synthesis", "flashtalk")(OmniRTSynthesisAdapter)
register("synthesis", "musetalk")(OmniRTSynthesisAdapter)
register("synthesis", "wav2lip")(OmniRTSynthesisAdapter)

# FlashHead has its own dedicated WS protocol (kept separate, not via omnirt yet).
from opentalking.providers.synthesis.flashhead.ws_client import FlashHeadWSClient  # noqa: E402

register("synthesis", "flashhead")(FlashHeadWSClient)

SYNTHESIS_PROVIDERS = ("mock", "flashtalk", "musetalk", "wav2lip", "flashhead")


def list_available_synthesis() -> list[str]:
    return list(SYNTHESIS_PROVIDERS)


__all__ = [
    "OmniRTSynthesisAdapter",
    "SYNTHESIS_PROVIDERS",
    "list_available_synthesis",
]
