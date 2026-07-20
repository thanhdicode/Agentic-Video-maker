"""Text-to-speech helper.

Prefers ``pyttsx3`` when available. On Windows without pyttsx3, falls back to
the built-in .NET ``System.Speech.Synthesis`` synthesizer via PowerShell.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class TTSError(Exception):
    """Raised when TTS cannot produce audio."""

    pass


def _sapi_text_to_speech(text: str, output: str | Path, voice: Optional[str] = None) -> Path:
    """Use Windows PowerShell + System.Speech.Synthesis to render a WAV file."""
    out_path = Path(output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    voice_select = ""
    if voice:
        voice_select = f"$synth.SelectVoice('{voice}');"

    ps = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
{voice_select}
$synth.SetOutputToWaveFile('{out_path}')
$synth.Speak('{text.replace("'", "''")}')
$synth.Dispose()
"""

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise TTSError(f"SAPI TTS failed: {result.stderr}")
    if not out_path.exists():
        raise TTSError("SAPI TTS did not produce an output file")
    return out_path


def text_to_speech(
    text: str,
    output: str | Path,
    voice: Optional[str] = None,
) -> Path:
    """Render ``text`` to a WAV file.

    Args:
        text: The text to speak.
        output: Destination path (``.wav``).
        voice: Optional voice name (e.g. ``Microsoft Zira Desktop``).
               On Windows with pyttsx3 this is passed through; with the
               SAPI fallback it selects the voice before speaking.
    """
    try:
        import pyttsx3
    except ImportError:
        pyttsx3 = None  # type: ignore[assignment]

    if pyttsx3 is not None:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        engine = pyttsx3.init()
        if voice:
            engine.setProperty("voice", voice)
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        return out_path

    if os.name == "nt":
        return _sapi_text_to_speech(text, output, voice=voice)

    raise TTSError(
        "No TTS backend available. Install pyttsx3 or run on Windows with SAPI."
    )


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter for segmenting a script."""
    parts = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".")]
    return [p for p in parts if p]
