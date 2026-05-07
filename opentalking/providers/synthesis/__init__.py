"""Synthesis providers (audio → video frames).

Real backends are thin clients to the omnirt inference runtime. A `mock`
provider is also registered for frontend-only dev and first-run experiences.
"""

from opentalking.core.registry import register
from opentalking.providers.synthesis import mock as _mock  # noqa: F401  side-effect register
from opentalking.providers.synthesis.omnirt import (
    auth_headers as omnirt_auth_headers,
    derive_audio2video_ws_url,
    resolve_synthesis_ws_url,
)
from opentalking.providers.synthesis.flashtalk.ws_client import FlashTalkWSClient

# All audio2video models behind OmniRT speak the FlashTalk-compatible WS
# protocol. The same client class is registered under three keys; the runtime
# picks the right WS URL via resolve_synthesis_ws_url(model, settings).
register("synthesis", "flashtalk")(FlashTalkWSClient)
register("synthesis", "musetalk")(FlashTalkWSClient)
register("synthesis", "wav2lip")(FlashTalkWSClient)

# FlashHead has its own dedicated WS protocol (kept separate, not via omnirt yet).
from opentalking.providers.synthesis.flashhead.ws_client import FlashHeadWSClient  # noqa: E402

register("synthesis", "flashhead")(FlashHeadWSClient)

SYNTHESIS_PROVIDERS = ("mock", "flashtalk", "musetalk", "wav2lip", "flashhead")


def list_available_synthesis() -> list[str]:
    return list(SYNTHESIS_PROVIDERS)


__all__ = [
    "SYNTHESIS_PROVIDERS",
    "derive_audio2video_ws_url",
    "list_available_synthesis",
    "omnirt_auth_headers",
    "resolve_synthesis_ws_url",
]
