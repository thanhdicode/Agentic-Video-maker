"""ToonCrafter cartoon keyframe interpolation wrapper.

Repo: https://github.com/Doubiiu/ToonCrafter
ComfyUI node: https://github.com/kijai/ComfyUI-DynamiCrafterWrapper
Model: https://huggingface.co/Kijai/DynamiCrafter_pruned/resolve/main/tooncrafter_512_interp-fp16.safetensors

VRAM: 512p fp16 ~8-15 GB, full ~24-27 GB.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def interpolate(
    first_frame: str | Path,
    last_frame: str | Path,
    prompt: str,
    output: str | Path,
    ckpt: str | Path = "ComfyUI/models/diffusion_models/tooncrafter_512_interp-fp16.safetensors",
    fps: int = 8,
    num_frames: int = 16,
    seed: int = 2026,
) -> Path:
    """Generate in-between frames between two cartoon keyframes."""
    # The actual invocation depends on ComfyUI-DynamiCrafterWrapper or the original repo.
    # This function documents the parameters and shell call.
    cmd = [
        "python", "scripts/tooncrafter_inference.py",
        "--first", str(first_frame),
        "--last", str(last_frame),
        "--prompt", prompt,
        "--ckpt", str(ckpt),
        "--fps", str(fps),
        "--num_frames", str(num_frames),
        "--seed", str(seed),
        "--output", str(output),
    ]
    subprocess.run(cmd, check=True)
    return Path(output)
