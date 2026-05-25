from __future__ import annotations

from pathlib import Path


WEB = Path("apps/web/src")


def test_frontend_lists_local_tts_models_and_labels():
    constants = (WEB / "constants" / "ttsBailian.ts").read_text(encoding="utf-8")
    settings = (WEB / "components" / "SettingsPanel.tsx").read_text(encoding="utf-8")
    app = (WEB / "App.tsx").read_text(encoding="utf-8")

    assert "local_cosyvoice" in constants
    assert "Local CosyVoice" in settings
    assert "本地模型" in constants
    assert "local_cosyvoice" in app
    assert "FunAudioLLM/Fun-CosyVoice3-0.5B-2512" in constants
    assert "iic/CosyVoice-300M" not in constants
    assert "local_qwen3_tts" not in settings


def test_frontend_shows_local_asr_status_copy():
    settings = (WEB / "components" / "SettingsPanel.tsx").read_text(encoding="utf-8")
    app = (WEB / "App.tsx").read_text(encoding="utf-8")

    assert "ASR" in settings
    assert "SenseVoiceSmall" in settings
    assert "Local FunASR" not in settings
    assert "Local sherpa-onnx" not in settings
    assert "OPENTALKING_STT_PROVIDER" in settings
    assert "asrProvider" in app
    assert "asrModel" in app


def test_frontend_exposes_api_asr_provider_selection():
    settings = (WEB / "components" / "SettingsPanel.tsx").read_text(encoding="utf-8")
    chat_input = (WEB / "components" / "ChatInput.tsx").read_text(encoding="utf-8")
    app = (WEB / "App.tsx").read_text(encoding="utf-8")

    assert "API 语音识别" in settings
    assert "DashScope API" in settings
    assert "onAsrProviderChange" in settings
    assert "stt_provider" in chat_input
    assert "fd.append(\"stt_provider\"" in app


def test_voice_clone_recorder_has_error_copy_and_upload_fallback():
    clone = (WEB / "components" / "BailianVoiceClone.tsx").read_text(encoding="utf-8")

    assert "navigator.mediaDevices" in clone
    assert "麦克风不可用" in clone
    assert "请改用上传音频" in clone
    assert "麦克风权限被拒绝" in clone
    assert "type=\"file\"" in clone
    assert "accept=\"audio/*,.webm,.mp3,.wav,.m4a,.aac,.flac,.ogg\"" in clone
    assert "handleAudioFileChange" in clone


def test_frontend_does_not_seed_local_default_voice():
    constants = (WEB / "constants" / "ttsBailian.ts").read_text(encoding="utf-8")

    assert "local-default" not in constants


def test_local_cosyvoice_clone_submits_prompt_text():
    clone = (WEB / "components" / "BailianVoiceClone.tsx").read_text(encoding="utf-8")

    assert "fd.append(\"prompt_text\"" in clone
    assert "setPromptText" in clone
    assert "<textarea" in clone


def test_frontend_hides_other_local_audio_experiments():
    constants = (WEB / "constants" / "ttsBailian.ts").read_text(encoding="utf-8")
    settings = (WEB / "components" / "SettingsPanel.tsx").read_text(encoding="utf-8")

    assert "iic/CosyVoice-300M" not in constants
    assert "CosyVoice 300M" not in constants
    assert "本地实验" not in constants
    assert "Qwen3-TTS" not in settings
    assert "FunASR" not in settings
    assert "sherpa-onnx" not in settings
