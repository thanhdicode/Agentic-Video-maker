"""AudioCraft / MusicGen / AudioGen wrappers."""

from __future__ import annotations

from typing import Any


def generate_music(prompt: str, output: str, duration: int = 30) -> str:
    """Generate background music from a text prompt."""
    try:
        from audiocraft.models import musicgen
    except ImportError as exc:
        raise ImportError("audiocraft is not installed") from exc

    model = musicgen.MusicGen.get_pretrained("small")
    model.set_generation_params(duration=duration)
    wav = model.generate([prompt])
    model.save(output, wav)
    return output


def generate_sfx(prompt: str, output: str, duration: int = 3) -> str:
    """Generate sound effect from a text prompt."""
    try:
        from audiocraft.models import audiocraft
    except ImportError:
        # AudioGen may not expose the same top-level API in all installs
        pass
    raise NotImplementedError("AudioGen SFX generation is a stub; configure your AudioGen model.")
