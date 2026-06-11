from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path(os.environ.get("OPENTALKING_LOCAL_AUDIO_MODEL_ROOT", "./models/local-audio"))

MODELS: dict[str, tuple[str, str]] = {
    "sensevoice-small": ("modelscope", "iic/SenseVoiceSmall"),
    "fun-cosyvoice3-0.5b-2512": ("modelscope", "FunAudioLLM/Fun-CosyVoice3-0.5B-2512"),
    "indextts2": ("modelscope", "IndexTeam/IndexTTS-2"),
    "indextts2-w2v-bert": ("hf", "facebook/w2v-bert-2.0"),
    "indextts2-maskgct": ("hf", "amphion/MaskGCT"),
    "indextts2-campplus": ("hf", "funasr/campplus"),
    "indextts2-bigvgan": ("hf", "nvidia/bigvgan_v2_22khz_80band_256x"),
}

HF_ALLOW_PATTERNS: dict[str, list[str]] = {
    # IndexTTS2 only needs the feature extractor, model weights, and conformer shim.
    "indextts2-w2v-bert": [
        "README.md",
        "config.json",
        "configuration.json",
        "conformer_shaw.pt",
        "model.safetensors",
        "preprocessor_config.json",
    ],
    # The sidecar maps hf_hub_download("amphion/MaskGCT", "semantic_codec/model.safetensors") here.
    "indextts2-maskgct": [
        "README.md",
        "config.json",
        "semantic_codec/model.safetensors",
        "acoustic_codec/model.safetensors",
        "acoustic_codec/model_1.safetensors",
        "s2a_model/s2a_model_full/model.safetensors",
        "t2s_model/model.safetensors",
    ],
    "indextts2-campplus": [
        "README.md",
        "config.yaml",
        "configuration.json",
        "campplus_cn_common.bin",
        "quickstart.md",
    ],
    # Avoid training and optimizer checkpoints; IndexTTS2 inference loads only the generator and code files.
    "indextts2-bigvgan": [
        "*.py",
        "LICENSE",
        "README.md",
        "config.json",
        "bigvgan_generator.pt",
        "alias_free_activation/**",
    ],
}


def default_model_keys() -> list[str]:
    return ["sensevoice-small", "fun-cosyvoice3-0.5b-2512"]


def local_audio_model_ids() -> tuple[str, ...]:
    return tuple(model_id for _, model_id in MODELS.values())


def _target(root: Path, model_id: str) -> Path:
    return root / model_id.replace("/", "__")


def _download_modelscope(model_id: str, target: Path) -> None:
    from modelscope import snapshot_download

    cached = Path(snapshot_download(model_id, local_dir=str(target)))
    if cached != target and cached.exists() and not target.exists():
        shutil.copytree(cached, target)


def _download_hf(model_id: str, target: Path, *, model_key: str) -> None:
    from huggingface_hub import snapshot_download

    endpoint = os.environ.get("HF_ENDPOINT", "").strip()
    kwargs = {"repo_id": model_id, "local_dir": str(target)}
    if endpoint:
        kwargs["endpoint"] = endpoint
    if patterns := HF_ALLOW_PATTERNS.get(model_key):
        kwargs["allow_patterns"] = patterns
    snapshot_download(**kwargs)


def _git_lfs_pull_if_needed(target: Path) -> None:
    if (target / ".git").exists() and shutil.which("git"):
        subprocess.run(["git", "-C", str(target), "lfs", "pull"], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the supported local STT/TTS model weights.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--model",
        action="append",
        choices=sorted(MODELS),
        help="Model key to download. Defaults to SenseVoiceSmall and CosyVoice3-0.5B-2512.",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    selected = args.model or default_model_keys()

    failures: list[tuple[str, str]] = []
    for key in selected:
        source, model_id = MODELS[key]
        target = _target(root, model_id)
        print(f"[{key}] {source}:{model_id} -> {target}", flush=True)
        target.mkdir(parents=True, exist_ok=True)
        try:
            if source == "modelscope":
                _download_modelscope(model_id, target)
            else:
                _download_hf(model_id, target, model_key=key)
            _git_lfs_pull_if_needed(target)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            failures.append((key, message))
            print(f"[{key}] failed: {message}", file=sys.stderr, flush=True)
            continue

    if failures:
        print("\nFailed downloads:", file=sys.stderr)
        for key, message in failures:
            print(f"- {key}: {message}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
