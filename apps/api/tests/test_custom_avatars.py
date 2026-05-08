from __future__ import annotations

import json
from io import BytesIO
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from apps.api.routes import avatars


def _png_bytes() -> bytes:
    out = BytesIO()
    Image.new("RGB", (8, 8), (10, 180, 210)).save(out, format="PNG")
    return out.getvalue()


def test_create_custom_avatar_adds_listed_asset_with_preview(tmp_path):
    base = tmp_path / "base-avatar"
    base.mkdir()
    (base / "preview.png").write_bytes(_png_bytes())
    (base / "reference.png").write_bytes(_png_bytes())
    (base / "manifest.json").write_text(
        json.dumps(
            {
                "id": "base-avatar",
                "name": "Base Avatar",
                "model_type": "flashtalk",
                "fps": 25,
                "sample_rate": 16000,
                "width": 416,
                "height": 704,
                "version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    app = FastAPI()
    app.state.settings = SimpleNamespace(avatars_dir=str(tmp_path))
    app.include_router(avatars.router)
    client = TestClient(app)

    response = client.post(
        "/avatars/custom",
        data={"base_avatar_id": "base-avatar", "name": "我的形象"},
        files={"image": ("avatar.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    created = response.json()
    assert created["id"].startswith("custom-")
    assert created["name"] == "我的形象"
    assert created["model_type"] == "flashtalk"

    custom_dir = tmp_path / created["id"]
    assert (custom_dir / "manifest.json").is_file()
    assert (custom_dir / "preview.png").is_file()
    assert (custom_dir / "reference.png").is_file()

    listed = client.get("/avatars").json()
    assert any(item["id"] == created["id"] and item["name"] == "我的形象" for item in listed)

    preview = client.get(f"/avatars/{created['id']}/preview")
    assert preview.status_code == 200
    assert preview.headers["content-type"] == "image/png"


def test_delete_custom_avatar_removes_directory(tmp_path):
    base = tmp_path / "base-avatar"
    base.mkdir()
    (base / "preview.png").write_bytes(_png_bytes())
    (base / "reference.png").write_bytes(_png_bytes())
    (base / "manifest.json").write_text(
        json.dumps(
            {
                "id": "base-avatar",
                "name": "Base",
                "model_type": "flashtalk",
                "fps": 25,
                "sample_rate": 16000,
                "width": 416,
                "height": 704,
                "version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    app = FastAPI()
    app.state.settings = SimpleNamespace(avatars_dir=str(tmp_path))
    app.include_router(avatars.router)
    client = TestClient(app)

    created = client.post(
        "/avatars/custom",
        data={"base_avatar_id": "base-avatar", "name": "tmp"},
        files={"image": ("a.png", _png_bytes(), "image/png")},
    ).json()

    response = client.delete(f"/avatars/{created['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert not (tmp_path / created["id"]).exists()
    assert not any(item["id"] == created["id"] for item in client.get("/avatars").json())


def test_delete_builtin_avatar_forbidden(tmp_path):
    """Built-in demos lack metadata.custom_avatar, so DELETE → 403."""
    base = tmp_path / "demo-avatar"
    base.mkdir()
    (base / "preview.png").write_bytes(_png_bytes())
    (base / "reference.png").write_bytes(_png_bytes())
    (base / "manifest.json").write_text(
        json.dumps(
            {
                "id": "demo-avatar",
                "name": "Demo",
                "model_type": "flashtalk",
                "fps": 25,
                "sample_rate": 16000,
                "width": 416,
                "height": 704,
                "version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    app = FastAPI()
    app.state.settings = SimpleNamespace(avatars_dir=str(tmp_path))
    app.include_router(avatars.router)
    client = TestClient(app)

    response = client.delete("/avatars/demo-avatar")
    assert response.status_code == 403
    assert "built-in" in response.json()["detail"]
    assert (tmp_path / "demo-avatar").exists()


def test_delete_unknown_avatar_404(tmp_path):
    app = FastAPI()
    app.state.settings = SimpleNamespace(avatars_dir=str(tmp_path))
    app.include_router(avatars.router)
    client = TestClient(app)

    assert client.delete("/avatars/does-not-exist").status_code == 404
