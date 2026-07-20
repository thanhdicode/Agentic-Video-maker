"""Text-to-speech helper.

Prefers ``edge-tts`` (free Microsoft Azure online voices) when available.
Falls back to ``pyttsx3`` or, on Windows, the built-in .NET
``System.Speech.Synthesis`` synthesizer via PowerShell.
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


def _edge_tts_to_speech(
    text: str,
    output: str | Path,
    voice: str = "en-US-AriaNeural",
) -> Path:
    """Use edge-tts to render an MP3/WAV file.

    edge-tts produces MP3; if the requested output has a ``.wav`` extension the
    file is converted with ffmpeg.
    """
    import asyncio
    from pathlib import Path

    import edge_tts

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mp3_path = out_path.with_suffix(".mp3")

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(mp3_path))

    asyncio.run(_run())

    if out_path.suffix.lower() == ".mp3":
        return mp3_path

    # Convert to WAV if requested.
    wav_path = out_path.with_suffix(".wav")
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_path),
            "-ar",
            "22050",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise TTSError(f"edge-tts WAV conversion failed: {result.stderr}")
    mp3_path.unlink(missing_ok=True)
    return wav_path


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
    """Render ``text`` to an audio file.

    Args:
        text: The text to speak.
        output: Destination path (``.mp3`` or ``.wav``).
        voice: Optional voice name. For edge-tts use an Azure voice such as
               ``en-US-AriaNeural``; for pyttsx3/SAPI use the installed voice
               name (e.g. ``Microsoft Zira Desktop``).
    """
    # Prefer edge-tts for high-quality free AI voices.
    try:
        import edge_tts
    except ImportError:
        edge_tts = None  # type: ignore[assignment]

    if edge_tts is not None:
        ai_voice = voice or "en-US-AriaNeural"
        return _edge_tts_to_speech(text, output, voice=ai_voice)

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
        "No TTS backend available. Install edge-tts, pyttsx3, or run on Windows with SAPI."
    )


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter for segmenting a script."""
    parts = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".")]
    return [p for p in parts if p]
