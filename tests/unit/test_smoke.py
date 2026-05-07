from __future__ import annotations

from pathlib import Path

import opentalking.models
from opentalking.avatars.manifest import parse_manifest
from opentalking.avatars.validator import validate_avatar_dir


def test_list_models() -> None:
    assert "wav2lip" in opentalking.models.list_models()
    assert "musetalk" in opentalking.models.list_models()
    assert "flashtalk" in opentalking.models.list_models()
    assert "flashhead" in opentalking.models.list_models()


def test_demo_avatar_valid() -> None:
    root = Path(__file__).resolve().parents[2]
    demo = root / "examples" / "avatars" / "demo-avatar"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_flashhead_demo_avatar_valid() -> None:
    root = Path(__file__).resolve().parents[2]
    demo = root / "examples" / "avatars" / "flashhead-demo"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_parse_demo_manifest() -> None:
    root = Path(__file__).resolve().parents[2]
    m = parse_manifest(root / "examples" / "avatars" / "demo-avatar" / "manifest.json")
    assert m.id == "demo-avatar"
    assert m.model_type == "wav2lip"
