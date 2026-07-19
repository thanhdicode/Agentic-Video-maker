"""FFmpeg automation helpers."""

from __future__ import annotations

import os
import subprocess
from typing import Any

import ffmpeg


def run_ffmpeg_cmd(args: list[str]) -> None:
    """Run an ffmpeg CLI command and raise on failure."""
    cmd = ["ffmpeg", "-y"] + args
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def assemble_video(clips: list[str], output: str, transition: str = "fade") -> str:
    """Concatenate video clips with a transition."""
    if not clips:
        raise ValueError("No video clips provided")

    list_path = output + ".txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    run_ffmpeg_cmd(
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_path,
            "-c",
            "copy",
            output,
        ]
    )
    os.remove(list_path)
    return output


def burn_subtitles(video: str, subtitle: str, output: str, style: str = "") -> str:
    """Burn subtitles into a video using FFmpeg."""
    vf = f"subtitles={subtitle}"
    if style:
        vf += f":force_style='{style}'"
    run_ffmpeg_cmd(["-i", video, "-vf", vf, "-c:a", "copy", output])
    return output


def mix_audio(video: str, music: str, output: str, music_db: float = -20.0) -> str:
    """Mix background music under a video."""
    run_ffmpeg_cmd(
        [
            "-i",
            video,
            "-i",
            music,
            "-filter_complex",
            f"[1:a]volume={music_db}dB[m];[0:a][m]amix=inputs=2:duration=first[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            output,
        ]
    )
    return output


def add_lut(video: str, lut_path: str, output: str) -> str:
    """Apply a color grading LUT."""
    run_ffmpeg_cmd(["-i", video, "-vf", f"lut3d='{lut_path}'", "-c:a", "copy", output])
    return output
