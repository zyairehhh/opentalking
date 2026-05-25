"""Speech-to-text provider selection for DashScope and local ASR runtimes."""

from __future__ import annotations

import os
import queue
import re
import tempfile
import threading
import time
import wave
from pathlib import Path
from typing import Any

import numpy as np

STT_PROVIDERS = frozenset({"dashscope", "funasr", "sensevoice", "sherpa_onnx"})
LOCAL_STT_PROVIDERS = frozenset({"funasr", "sensevoice", "sherpa_onnx"})
_SENSEVOICE_TAG_RE = re.compile(r"<\|[^|<>]+\|>")


def _clean_text(text: str) -> str:
    return _SENSEVOICE_TAG_RE.sub("", text).strip()


_ADAPTER_CACHE: dict[tuple[str, str, str, str], object] = {}
_ADAPTER_CACHE_LOCK = threading.Lock()


def normalize_stt_provider(value: str | None, *, default: str | None = None) -> str | None:
    provider = (value or "").strip().lower()
    if not provider:
        return default
    if provider not in STT_PROVIDERS:
        raise ValueError(f"unsupported stt provider: {value}")
    return provider


def _settings_value(name: str, default: str = "") -> str:
    try:
        from opentalking.core.config import get_settings

        value = getattr(get_settings(), name, default)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    return default


def _provider() -> str:
    raw = os.environ.get("OPENTALKING_STT_PROVIDER", "").strip()
    if raw:
        return normalize_stt_provider(raw, default="dashscope") or "dashscope"
    return (
        normalize_stt_provider(_settings_value("stt_provider", "dashscope"), default="dashscope")
        or "dashscope"
    )


def _model_root() -> Path:
    raw = (
        os.environ.get("OPENTALKING_LOCAL_AUDIO_MODEL_ROOT", "").strip()
        or _settings_value("local_audio_model_root", "")
        or "./models/local-audio"
    )
    return Path(raw).expanduser()


def _device() -> str:
    for value in (
        os.environ.get("OPENTALKING_STT_DEVICE", ""),
        os.environ.get("OPENTALKING_LOCAL_AUDIO_DEVICE", ""),
        _settings_value("stt_device", ""),
        _settings_value("local_audio_device", ""),
    ):
        device = str(value or "").strip()
        if device and device != "auto":
            return device
    return "auto"


def _stt_model(provider: str) -> str:
    direct = os.environ.get("OPENTALKING_STT_MODEL", "").strip()
    if direct:
        return direct
    configured = _settings_value("stt_model", "")
    if configured and configured != "paraformer-realtime-v2":
        return configured
    if provider == "funasr":
        return os.environ.get("OPENTALKING_FUNASR_MODEL", "iic/Fun-ASR-Nano-2512").strip()
    if provider == "sensevoice":
        return os.environ.get("OPENTALKING_SENSEVOICE_MODEL", "iic/SenseVoiceSmall").strip()
    if provider == "sherpa_onnx":
        return os.environ.get("OPENTALKING_SHERPA_ONNX_MODEL", "").strip()
    return configured or "paraformer-realtime-v2"


def _local_path_for_model(model: str) -> Path:
    path = Path(model).expanduser()
    if path.is_absolute() or path.exists():
        return path
    if "/" in model:
        return _model_root() / model.replace("/", "__")
    return _model_root() / model


def _write_pcm_queue_to_wav(
    chunk_queue: "queue.Queue[bytes | None]",
    wav_path: Path,
    *,
    sample_rate: int = 16000,
) -> None:
    chunks: list[bytes] = []
    while True:
        chunk = chunk_queue.get()
        if chunk is None:
            break
        if chunk:
            chunks.append(bytes(chunk))
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(chunks))


def _extract_text(result: Any) -> str:
    if isinstance(result, str):
        return _clean_text(result)
    if isinstance(result, dict):
        text = result.get("text") or result.get("sentence")
        if isinstance(text, str):
            return _clean_text(text)
    if isinstance(result, list):
        return "".join(filter(None, (_extract_text(item) for item in result))).strip()
    return ""


class LocalFunASRSTTAdapter:
    """FunASR/SenseVoice local adapter loaded lazily on first transcription."""

    def __init__(self, *, provider: str, model: str | None = None, device: str | None = None) -> None:
        self.provider = provider
        self.model = (model or _stt_model(provider)).strip()
        self.device = (device or _device()).strip() or "auto"
        self.model_root = _model_root()
        self._runtime: Any | None = None

    def _runtime_model_name(self) -> str:
        local_path = _local_path_for_model(self.model)
        return str(local_path) if local_path.exists() else self.model

    def _load_runtime(self) -> Any:
        if self._runtime is not None:
            return self._runtime
        try:
            from funasr import AutoModel
        except ImportError as exc:
            raise RuntimeError(
                "FunASR local STT requires the local-audio extra: "
                "uv sync --extra dev --extra models --extra local-audio"
            ) from exc

        kwargs: dict[str, Any] = {}
        if self.device and self.device != "auto":
            kwargs["device"] = self.device
        self._runtime = AutoModel(model=self._runtime_model_name(), **kwargs)
        return self._runtime

    def transcribe_wav(self, wav_path: str | Path) -> tuple[str, float]:
        model = self._load_runtime()
        t0 = time.perf_counter()
        result = model.generate(input=str(wav_path), language="auto", use_itn=True)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return _extract_text(result), elapsed_ms

    def transcribe_pcm_queue(
        self,
        chunk_queue: "queue.Queue[bytes | None]",
        *,
        sample_rate: int = 16000,
    ) -> tuple[str, float]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
        try:
            _write_pcm_queue_to_wav(chunk_queue, wav_path, sample_rate=sample_rate)
            return self.transcribe_wav(wav_path)
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass


class SherpaOnnxSTTAdapter:
    def __init__(self, *, model: str | None = None) -> None:
        self.model = (model or _stt_model("sherpa_onnx")).strip()

    def transcribe_wav(self, wav_path: str | Path) -> tuple[str, float]:
        try:
            import sherpa_onnx
        except ImportError as exc:
            raise RuntimeError("sherpa-onnx local STT requires the local-audio extra.") from exc
        if not self.model:
            raise RuntimeError("OPENTALKING_STT_MODEL must point to a sherpa-onnx model path.")
        t0 = time.perf_counter()
        recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=self.model,
            tokens="",
            num_threads=2,
        )
        stream = recognizer.create_stream()
        samples = _read_wav_float32_mono(Path(wav_path))
        stream.accept_waveform(16000, samples)
        recognizer.decode_stream(stream)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return str(stream.result.text).strip(), elapsed_ms

    def transcribe_pcm_queue(
        self,
        chunk_queue: "queue.Queue[bytes | None]",
        *,
        sample_rate: int = 16000,
    ) -> tuple[str, float]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
        try:
            _write_pcm_queue_to_wav(chunk_queue, wav_path, sample_rate=sample_rate)
            return self.transcribe_wav(wav_path)
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass


def _read_wav_float32_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        channels = wf.getnchannels()
        raw = wf.readframes(wf.getnframes())
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        pcm = pcm.reshape(-1, channels).mean(axis=1)
    if sr != 16000 and pcm.size:
        n_dst = max(1, int(round(pcm.size * 16000 / sr)))
        x_old = np.linspace(0.0, pcm.size - 1.0, num=pcm.size)
        x_new = np.linspace(0.0, pcm.size - 1.0, num=n_dst)
        pcm = np.interp(x_new, x_old, pcm).astype(np.float32)
    return pcm


def create_stt_adapter(provider: str | None = None):
    selected = normalize_stt_provider(provider, default=None) or _provider()
    model = _stt_model(selected)
    device = _device()
    cache_key = (selected, model, device, str(_model_root()))
    with _ADAPTER_CACHE_LOCK:
        cached = _ADAPTER_CACHE.get(cache_key)
        if cached is not None:
            return cached
    if selected in {"funasr", "sensevoice"}:
        adapter = LocalFunASRSTTAdapter(provider=selected, model=model, device=device)
    elif selected == "sherpa_onnx":
        adapter = SherpaOnnxSTTAdapter(model=model)
    else:
        return None
    with _ADAPTER_CACHE_LOCK:
        return _ADAPTER_CACHE.setdefault(cache_key, adapter)


def clear_stt_adapter_cache() -> None:
    with _ADAPTER_CACHE_LOCK:
        _ADAPTER_CACHE.clear()


def transcribe_wav_path_sync(wav_path: str | Path, *, provider: str | None = None) -> tuple[str, float]:
    selected = normalize_stt_provider(provider, default=None) or _provider()
    if selected == "dashscope":
        from opentalking.providers.stt.dashscope.adapter import _recognize_wav_sync

        return _recognize_wav_sync(Path(wav_path))

    adapter = create_stt_adapter(selected)
    if adapter is None:
        raise RuntimeError(f"unsupported local STT provider: {selected}")
    return adapter.transcribe_wav(wav_path)


def transcribe_pcm_chunk_queue_sync(
    chunk_queue: "queue.Queue[bytes | None]",
    *,
    sample_rate: int = 16000,
    provider: str | None = None,
) -> tuple[str, float]:
    selected = normalize_stt_provider(provider, default=None) or _provider()
    if selected == "dashscope":
        from opentalking.providers.stt.dashscope.adapter import (
            transcribe_pcm_chunk_queue_sync as dashscope_transcribe_pcm_chunk_queue_sync,
        )

        return dashscope_transcribe_pcm_chunk_queue_sync(chunk_queue)

    adapter = create_stt_adapter(selected)
    if adapter is None:
        raise RuntimeError(f"unsupported local STT provider: {selected}")
    return adapter.transcribe_pcm_queue(chunk_queue, sample_rate=sample_rate)


def stt_status() -> dict[str, str]:
    selected = _provider()
    return {"provider": selected, "model": _stt_model(selected), "device": _device()}
