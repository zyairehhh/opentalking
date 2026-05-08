"""Avatar/model compatibility groups (sessions route)."""
from __future__ import annotations

from apps.api.routes.sessions import (
    _avatar_compatible_with_model,
    _compatible_models,
    _input_form_for,
)


def test_portrait_group_is_swappable():
    # FlashHead-demo (avatar.model_type=flashhead) + body.model=flashtalk should pass
    assert _avatar_compatible_with_model("flashhead", "flashtalk")
    # And vice-versa
    assert _avatar_compatible_with_model("flashtalk", "flashhead")


def test_frames_group_is_swappable():
    assert _avatar_compatible_with_model("musetalk", "wav2lip")
    assert _avatar_compatible_with_model("wav2lip", "musetalk")


def test_cross_group_is_blocked():
    # wav2lip avatar (frames) cannot run on flashtalk (portrait-only)
    assert not _avatar_compatible_with_model("wav2lip", "flashtalk")
    assert not _avatar_compatible_with_model("flashtalk", "wav2lip")


def test_mock_accepts_any_avatar():
    assert _avatar_compatible_with_model("flashtalk", "mock")
    assert _avatar_compatible_with_model("musetalk", "mock")
    assert _avatar_compatible_with_model("wav2lip", "mock")
    assert _avatar_compatible_with_model("flashhead", "mock")


def test_input_form_lookup():
    assert _input_form_for("flashtalk") == "portrait+audio"
    assert _input_form_for("flashhead") == "portrait+audio"
    assert _input_form_for("wav2lip") == "frames+audio"
    assert _input_form_for("musetalk") == "frames+audio"
    assert _input_form_for("totally-unknown") is None


def test_compatible_models_includes_mock():
    assert "mock" in _compatible_models("flashtalk")
    assert "mock" in _compatible_models("wav2lip")
