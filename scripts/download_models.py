#!/usr/bin/env python3
"""Download recommended model weights for the AI Video Studio.

Usage:
    python scripts/download_models.py [--profile hybrid-professional]

This script uses `huggingface_hub` and direct HTTP downloads. Some models are
large; ensure at least 200 GB free disk space.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import requests
from huggingface_hub import hf_hub_download, snapshot_download


REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_huggingface(repo_id: str, local_dir: Path, allow_patterns: list[str] | None = None) -> None:
    """Download a Hugging Face model repo to a local directory."""
    print(f"[HF] {repo_id} -> {local_dir}")
    ensure_dir(local_dir)
    snapshot_download(
        repo_id,
        local_dir=str(local_dir),
        allow_patterns=allow_patterns,
        resume_download=True,
    )


def download_file(url: str, dest: Path) -> None:
    """Download a single file with progress."""
    if dest.exists():
        print(f"[SKIP] {dest} already exists")
        return
    print(f"[HTTP] {url} -> {dest}")
    ensure_dir(dest.parent)
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  {pct:.1f}%", end="")
    print()


def download_realesrgan() -> None:
    dest = MODELS_DIR / "real-esrgan" / "realesr-general-x4v3.pth"
    if dest.exists():
        return
    url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"
    download_file(url, dest)


def download_rife() -> None:
    dest_dir = MODELS_DIR / "practical-rife"
    if any(dest_dir.glob("*.pkl")):
        return
    # Practical-RIFE models are stored in a GitHub release folder; fetch the default model
    base = "https://github.com/GWD99/Practical-RIFE/releases/download/v1/"
    for name in ["train_log_rife.pth", "rife.pkl"]:
        download_file(base + name, dest_dir / name)


def download_kokoro() -> None:
    """Kokoro downloads ONNX models on first import; pre-fetch one voice."""
    try:
        from kokoro import KPipeline
        pipeline = KPipeline(lang_code="a")
        print("[Kokoro] first-run download triggered (models cached in ~/.kokoro)")
    except Exception as exc:
        print(f"[Kokoro] could not pre-fetch: {exc}")


def download_all(profile: str) -> None:
    print(f"Downloading models for profile: {profile}")
    print(f"Target directory: {MODELS_DIR}")
    print("Estimated total: 150-250 GB\n")

    # Image generation
    download_huggingface("black-forest-labs/FLUX.1-schnell", MODELS_DIR / "flux-schnell")
    if profile == "maximum-quality":
        download_huggingface("black-forest-labs/FLUX.1-dev", MODELS_DIR / "flux-dev")

    # Video generation
    if profile in ("hybrid-professional", "maximum-quality"):
        download_huggingface(
            "Wan-AI/Wan2.1-I2V-14B-480P",
            MODELS_DIR / "wan2.1-i2v-14b-480p",
            allow_patterns=["*.json", "*.safetensors", "*.txt"],
        )
    else:
        download_huggingface(
            "Wan-AI/Wan2.1-I2V-1.3B-480P",
            MODELS_DIR / "wan2.1-i2v-1.3b-480p",
            allow_patterns=["*.json", "*.safetensors", "*.txt"],
        )
    download_huggingface("Lightricks/LTX-Video", MODELS_DIR / "ltx-video")
    download_huggingface("Doubiiu/ToonCrafter", MODELS_DIR / "tooncrafter")

    # Character consistency
    download_huggingface("h94/IP-Adapter", MODELS_DIR / "ip-adapter")
    # PuLID weights name/location varies; try common repo
    try:
        download_huggingface("ToTheBeginning/PuLID", MODELS_DIR / "pulid")
    except Exception as exc:
        print(f"[PuLID] {exc}")

    # Upscale / interpolation
    download_realesrgan()
    download_rife()

    # TTS
    download_huggingface("hexgrad/kokoro", MODELS_DIR / "kokoro")
    download_huggingface("fishaudio/fish-speech-1.5", MODELS_DIR / "fish-speech")
    download_huggingface("SWivid/F5-TTS", MODELS_DIR / "f5-tts")
    download_huggingface("FunAudioLLM/CosyVoice", MODELS_DIR / "cosyvoice")
    download_kokoro()

    # Whisper
    download_huggingface(
        "Systran/faster-whisper-large-v2",
        MODELS_DIR / "whisper" / "large-v2",
    )

    # Audio (MusicGen / AudioGen weights download on first use; try to trigger)
    try:
        import audiocraft
        from audiocraft.models import musicgen, audiogen
        _ = musicgen.MusicGen.get_pretrained("small")
        _ = audiogen.AudioGen.get_pretrained("facebook/audiogen-medium")
        print("[AudioCraft] first-run download triggered")
    except Exception as exc:
        print(f"[AudioCraft] could not pre-fetch: {exc}")

    print("\nDone. Run `scripts/health-check.sh` to verify.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download AI Video Studio model weights")
    parser.add_argument(
        "--profile",
        choices=["local-open-source", "hybrid-professional", "maximum-quality"],
        default="hybrid-professional",
        help="Which production profile to download models for",
    )
    parser.add_argument(
        "--hf-token",
        default=os.environ.get("HF_TOKEN"),
        help="Hugging Face access token for gated models (FLUX.1-dev, etc.)",
    )
    args = parser.parse_args()

    if shutil.which("git-lfs") is None:
        print("Warning: git-lfs not found. Install with `sudo apt install git-lfs`.")

    if args.hf_token:
        os.environ.setdefault("HF_TOKEN", args.hf_token)

    download_all(args.profile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
