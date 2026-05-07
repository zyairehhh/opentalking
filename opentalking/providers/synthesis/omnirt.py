"""OmniRT thin client — single adapter, registered under flashtalk/musetalk/wav2lip keys.

omnirt is the upstream multimodal inference runtime
(https://github.com/datascale-ai/omnirt). Per-key model binding is provided
via configs/inference/omnirt.yaml at construction time.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import AsyncIterator

logger = logging.getLogger(__name__)


@dataclass
class OmniRTSynthesisAdapter:
    endpoint: str
    model: str
    timeout_s: float = 30.0

    async def stream_audio_to_video(
        self,
        audio_chunks: AsyncIterator[bytes],
        *,
        reference_image: bytes,
        params: dict | None = None,
    ) -> AsyncIterator[bytes]:
        """Stream audio chunks to omnirt's audio2video task and yield decoded frames.

        Wire protocol is intentionally not finalized here — the canonical
        endpoint shape is defined in configs/inference/omnirt.yaml and
        implemented against omnirt's stable schema in a follow-up PR.

        Until omnirt's streaming RPC is wired in, callers go through the
        existing FlashTalkWSClient / FlashHeadWSClient paths under
        opentalking.providers.synthesis.{flashtalk,flashhead}.
        """
        raise NotImplementedError(
            "OmniRTSynthesisAdapter streaming is pending the omnirt schema lock-in; "
            "current sessions still use FlashTalk/FlashHead WS clients directly."
        )
