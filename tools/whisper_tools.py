"""Speech-to-text / subtitle helpers via faster-whisper."""

from __future__ import annotations

import os
from typing import Any


def transcribe_audio(audio_path: str, model: str = "base") -> list[dict[str, Any]]:
    """Transcribe audio and return word-level segments."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise ImportError("faster-whisper is not installed") from exc

    whisper = WhisperModel(model, device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu")
    segments, _ = whisper.transcribe(audio_path, word_timestamps=True)
    results = []
    for seg in segments:
        results.append(
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
                "words": [
                    {"word": w.word, "start": w.start, "end": w.end} for w in (seg.words or [])
                ],
            }
        )
    return results


def generate_subtitles(audio_path: str, output_srt: str, model: str = "base") -> str:
    """Create an SRT file from audio transcription."""
    segments = transcribe_audio(audio_path, model)
    with open(output_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{_fmt_time(seg['start'])} --> {_fmt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    return output_srt


def _fmt_time(seconds: float) -> str:
    """Format seconds to SRT timestamp."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:06.3f}".replace(".", ",")
