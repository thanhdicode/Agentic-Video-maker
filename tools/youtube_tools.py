"""YouTube ingestion helpers using yt-dlp.

Downloads a video and/or extracts metadata and automatic captions. Requires
``yt-dlp`` to be installed and available on PATH (or set ``YTDLP_EXECUTABLE``).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


class YouTubeError(Exception):
    """Raised when yt-dlp cannot fetch a YouTube video or its metadata."""

    pass


def _find_ytdlp() -> str:
    env = os.environ.get("YTDLP_EXECUTABLE")
    if env and Path(env).exists():
        return env

    name = "yt-dlp.exe" if os.name == "nt" else "yt-dlp"
    found = shutil.which(name)
    if found:
        return found

    raise YouTubeError(
        "yt-dlp not found. Install it from https://github.com/yt-dlp/yt-dlp"
    )


def _run_ytdlp(*args: str) -> subprocess.CompletedProcess[str]:
    exe = _find_ytdlp()
    cmd = [exe, "--no-warnings", "--no-progress", "--encoding", "utf8"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def get_video_info(url: str) -> dict[str, Any]:
    """Return title, duration, description and other metadata for a video."""
    result = _run_ytdlp(
        "--dump-json",
        "--skip-download",
        "--extractor-args",
        "youtube:player_client=web",
        url,
    )
    if result.returncode != 0:
        raise YouTubeError(result.stderr or "yt-dlp failed to extract video info")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise YouTubeError(f"Could not parse yt-dlp output: {exc}") from exc

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "duration": data.get("duration"),
        "description": data.get("description"),
        "uploader": data.get("uploader"),
        "thumbnail": data.get("thumbnail"),
    }


def download_video(url: str, output_dir: str | Path, quality: str = "720") -> Path:
    """Download the best video+audio stream at or below ``quality`` height."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / "%(id)s.%(ext)s")

    result = _run_ytdlp(
        "-f",
        f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best",
        "-o",
        template,
        "--extractor-args",
        "youtube:player_client=web",
        url,
    )
    if result.returncode != 0:
        raise YouTubeError(result.stderr or "yt-dlp failed to download video")

    files = sorted(out_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise YouTubeError("No output file found after download")
    return files[0]


def extract_transcript(
    url: str,
    output_dir: str | Path,
    languages: list[str] | None = None,
) -> Path | None:
    """Download automatic captions as an SRT file.

    Returns the path to the SRT file, or ``None`` if captions are unavailable.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    langs = ",".join(languages or ["en"])
    template = str(out_dir / "%(id)s.%(ext)s")

    result = _run_ytdlp(
        "--skip-download",
        "--write-auto-subs",
        "--sub-langs",
        langs,
        "--convert-subs",
        "srt",
        "--extractor-args",
        "youtube:player_client=web",
        "-o",
        template,
        url,
    )
    if result.returncode != 0:
        raise YouTubeError(result.stderr or "yt-dlp failed to extract transcript")

    srts = list(out_dir.glob("*.srt"))
    return srts[0] if srts else None
