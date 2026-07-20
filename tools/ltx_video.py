"""Lightricks LTX-Video / LTX-2 wrapper.

Models: https://huggingface.co/Lightricks/LTX-Video
ComfyUI nodes: https://github.com/Lightricks/ComfyUI-LTXVideo

VRAM: 2B distilled ~6-10 GB, 13B distilled ~16-24 GB, 13B BF16 ~38 GB.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def i2v(
    image: str | Path,
    prompt: str,
    output: str | Path,
    ckpt_dir: str | Path,
    width: int = 1280,
    height: int = 704,
    num_frames: int = 97,
    seed: int = 2026,
) -> Path:
    """Run LTX-Video image-to-video from a local checkpoint."""
    # Use ComfyUI-LTXVideo or the native inference script once available.
    # This wrapper documents the intended CLI shape.
    cmd = [
        "python", "inference.py",
        "--ckpt_dir", str(ckpt_dir),
        "--image", str(image),
        "--prompt", prompt,
        "--width", str(width),
        "--height", str(height),
        "--num_frames", str(num_frames),
        "--seed", str(seed),
        "--output", str(output),
    ]
    subprocess.run(cmd, check=True)
    return Path(output)
