"""Wan2.1 / Wan2.2 video generation wrapper.

Models:
- Wan2.2-I2V-14B: https://huggingface.co/Wan-AI/Wan2.2-I2V-14B-720P
- Wan2.2-T2V-1.3B: https://huggingface.co/Wan-AI/Wan2.2-T2V-1.3B
- Wan-Animate: https://huggingface.co/wan-animate/wananimate
- Code: https://github.com/wan-video/wan2.1

VRAM: 14B ~24-40 GB, 1.3B ~8-12 GB.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def i2v(
    image: str | Path,
    prompt: str,
    output: str | Path,
    ckpt_dir: str | Path,
    size: str = "1280*720",
    task: str = "i2v-14B",
    seed: int = 2026,
) -> Path:
    """Run Wan2.2 image-to-video from a local checkpoint."""
    cmd = [
        "python", "generate.py",
        "--task", task,
        "--size", size,
        "--ckpt_dir", str(ckpt_dir),
        "--image", str(image),
        "--prompt", prompt,
        "--seed", str(seed),
    ]
    # The official Wan2.1 repo writes output next to the image by default.
    # This wrapper assumes you run it from inside the Wan2.1 source directory
    # and copy the result afterward.
    subprocess.run(cmd, check=True)
    return Path(output)


def t2v(
    prompt: str,
    output: str | Path,
    ckpt_dir: str | Path,
    size: str = "1280*720",
    task: str = "t2v-14B",
    seed: int = 2026,
) -> Path:
    """Run Wan2.2 text-to-video from a local checkpoint."""
    cmd = [
        "python", "generate.py",
        "--task", task,
        "--size", size,
        "--ckpt_dir", str(ckpt_dir),
        "--prompt", prompt,
        "--seed", str(seed),
    ]
    subprocess.run(cmd, check=True)
    return Path(output)
