"""Character consistency helpers: IP-Adapter, PuLID, LoRA, character sheets.

Useful workflows:
- Generate a character sheet (front / 3/4 / side / expressions) with FLUX + seed.
- Lock identity across shots with IP-Adapter or PuLID in ComfyUI.
- Train a small LoRA for the mascot with kohya_ss.

Repos:
- ComfyUI IP-Adapter: https://github.com/cubiq/ComfyUI_IPAdapter_plus
- PuLID: https://github.com/ToTheBeginning/PuLID
- LoRA training (kohya): https://github.com/bmaltais/Kohya_GUI
- AnimeLoom concept: https://github.com/JoelJohnsonThomas/AnimeLoom
- 2D sprite pipeline: https://github.com/mor-o/comfyui-2d-character-pipeline
"""

from __future__ import annotations

from pathlib import Path


def build_character_sheet_prompt(
    name: str,
    description: str,
    style: str = "AumSum style 2D flat vector cartoon",
) -> str:
    """Return a prompt meant for a 4-view character sheet."""
    return (
        f"{style} character sheet of {name}, {description}, "
        "front view, 3/4 view, side view, back view, "
        "multiple expressions: neutral, happy, surprised, pointing, thumbs up, "
        "big friendly eyes, bold black outlines, bright saturated colors, "
        "white background, no text, no watermark, high quality"
    )


def lora_training_command(
    image_dir: str | Path,
    output_dir: str | Path,
    name: str,
    network_dim: int = 32,
    network_alpha: int = 16,
    batch_size: int = 1,
    epochs: int = 10,
) -> list[str]:
    """Return a kohya-ss LoRA training command for the mascot."""
    return [
        "python", "train_network.py",
        "--pretrained_model_name_or_path", "stabilityai/stable-diffusion-xl-base-1.0",
        "--train_data_dir", str(image_dir),
        "--output_dir", str(output_dir),
        "--network_module", "networks.lora",
        "--network_dim", str(network_dim),
        "--network_alpha", str(network_alpha),
        "--train_batch_size", str(batch_size),
        "--max_train_epochs", str(epochs),
        "--resolution", "1024,1024",
        "--output_name", name,
    ]
