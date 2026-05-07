from __future__ import annotations

from pathlib import Path

from opentalking.avatars.manifest import parse_manifest
from opentalking.avatars.validator import validate_avatar_dir
from opentalking.providers.synthesis import list_available_synthesis


def test_list_models() -> None:
    keys = list_available_synthesis()
    assert "wav2lip" in keys
    assert "musetalk" in keys
    assert "flashtalk" in keys
    assert "flashhead" in keys


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
