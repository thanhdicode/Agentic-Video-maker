"""Wrappers for AI voice, music, and SFX generation.

- F5-TTS: https://github.com/SWivid/F5-TTS
- Kokoro: https://github.com/hexgrad/kokoro
- AudioCraft / MusicGen / AudioGen: https://github.com/facebookresearch/audiocraft
- FoleyCrafter: https://github.com/open-mmlab/FoleyCrafter
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def f5_tts(
    ref_audio: str | Path,
    ref_text: str,
    gen_text: str,
    output: str | Path,
    model: str = "SWivid/F5-TTS",
) -> Path:
    """Run F5-TTS inference. Requires `pip install f5-tts` and a voice reference."""
    cmd = [
        "f5-tts-infer",
        "--ref_audio", str(ref_audio),
        "--ref_text", ref_text,
        "--gen_text", gen_text,
        "--output", str(output),
        "--model", model,
    ]
    subprocess.run(cmd, check=True)
    return Path(output)


def kokoro_tts(
    text: str,
    output: str | Path,
    voice: str = "af_heart",
) -> Path:
    """Run Kokoro TTS. Requires `pip install kokoro`."""
    # Native Python API is cleaner than CLI; wrapper uses a small inline script.
    script = f"""
from kokoro import KPipeline
import soundfile as sf
pipeline = KPipeline(lang_code='a')
generator = pipeline('{text.replace(chr(39), chr(39)+chr(39))}', voice='{voice}')
audio = None
for _, _, wav in generator:
    audio = wav
sf.write('{output}', audio, 24000)
"""
    subprocess.run(["python", "-c", script], check=True)
    return Path(output)


def musicgen(
    prompt: str,
    output: str | Path,
    model: str = "facebook/musicgen-medium",
    duration: int = 30,
) -> Path:
    """Generate background music with AudioCraft MusicGen."""
    script = f"""
from audiocraft.models import MusicGen
import torchaudio
model = MusicGen.get_pretrained('{model}')
model.set_generation_params(duration={duration})
wav = model.generate(['{prompt.replace(chr(39), chr(39)+chr(39))}'])
torchaudio.save('{output}', wav[0].cpu(), sample_rate=32000)
"""
    subprocess.run(["python", "-c", script], check=True)
    return Path(output)


def foley(
    video: str | Path,
    prompt: str,
    output: str | Path,
) -> Path:
    """Generate SFX synchronized to a silent video with FoleyCrafter."""
    cmd = [
        "python", "inference.py",
        "--input", str(video),
        "--prompt", prompt,
        "--save_dir", str(Path(output).parent),
    ]
    subprocess.run(cmd, check=True)
    return Path(output)
