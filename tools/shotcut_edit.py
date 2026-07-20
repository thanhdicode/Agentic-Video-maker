"""Shotcut / MLT headless editor wrapper.

Drives the `melt` command-line renderer from the Shotcut/MLT distribution.
This works without a GPU and is suitable for CPU-only automated cuts,
cross-fades, and audio mixing.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional


class ShotcutNotFoundError(Exception):
    """Raised when the melt executable cannot be located."""

    pass


class ShotcutRenderError(Exception):
    """Raised when melt exits with an error or the output is missing."""

    pass


class ShotcutEditor:
    """High-level controller for assembling and rendering video with MLT/melt."""

    def __init__(self, executable: Optional[str] = None, verbose: bool = False) -> None:
        self.executable = executable or self._find_executable()
        self.verbose = verbose

    @staticmethod
    def _find_executable() -> str:
        """Locate the melt binary from env, PATH, or common install paths."""
        env = os.environ.get("SHOTCUT_MELT") or os.environ.get("MLT_MELT")
        if env and Path(env).exists():
            return env

        name = "melt.exe" if sys.platform == "win32" else "melt"
        found = shutil.which(name)
        if found:
            return found

        common = [
            r"C:\Users\Administrator\shotcut\Shotcut\melt.exe",
            r"C:\Program Files\Shotcut\melt.exe",
            r"C:\Program Files\Shotcut\bin\melt.exe",
            r"C:\Program Files (x86)\Shotcut\melt.exe",
        ]
        for p in common:
            if Path(p).exists():
                return p

        raise ShotcutNotFoundError(
            "melt executable not found. Install Shotcut or set SHOTCUT_MELT."
        )

    @staticmethod
    def _probe_duration(path: str | Path) -> float:
        """Return the duration of a media file in seconds using ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return 0.0
        try:
            return float(result.stdout.strip())
        except ValueError:
            return 0.0

    @staticmethod
    def _db_from_ratio(ratio: float) -> float:
        """Convert a linear volume ratio to decibels for the volume filter."""
        if ratio <= 0:
            return -100.0
        return 20.0 * math.log10(ratio)

    @staticmethod
    def _select_profile(width: int, height: int, fps: int) -> str:
        """Pick a built-in MLT profile that matches fps and orientation."""
        if width < height:  # portrait
            if fps >= 60:
                return "vertical_hd_60"
            return "vertical_hd_30"

        if fps >= 60:
            return "atsc_1080p_60"
        if fps >= 50:
            return "atsc_1080p_50"
        if fps == 24:
            return "atsc_1080p_24"
        if fps == 25:
            return "atsc_1080p_25"
        return "atsc_1080p_30"

    def render(
        self,
        video_paths: list[str | Path],
        output: str | Path,
        audio_clips: Optional[list[dict[str, Any]]] = None,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30,
        transition_frames: int = 0,
    ) -> Path:
        """Build and run a melt command to assemble and render a video.

        Args:
            video_paths: Video clips to concatenate. Each clip is assumed to be
                at the same frame rate as ``fps`` when interpreting frame counts.
            output: Destination MP4 path.
            audio_clips: Optional list of audio dicts with keys ``path``,
                ``volume`` (0..1 ratio), and ``fit_to_timeline`` (bool).
            resolution: Output (width, height).
            fps: Target frames per second.
            transition_frames: Cross-fade length in frames. ``0`` means hard cuts.
        """
        if not video_paths:
            raise ShotcutRenderError("No video paths provided")

        output_path = Path(output).resolve()
        width, height = resolution

        durations = [self._probe_duration(p) for p in video_paths]
        total_duration = sum(durations) - (transition_frames / fps) * (
            len(video_paths) - 1
        )
        total_frames = max(1, int(round(total_duration * fps)))

        cmd: list[str] = [self.executable]
        for i, path in enumerate(video_paths):
            cmd.append(str(path))
            if i > 0 and transition_frames:
                cmd.extend(["-mix", str(transition_frames), "-mixer", "luma"])

        for audio in audio_clips or []:
            apath = audio["path"]
            cmd.extend(["-audio-track", str(apath)])

            if audio.get("fit_to_timeline"):
                cmd.append(f"out={total_frames}")
            elif audio.get("out_frames"):
                cmd.append(f"out={int(audio['out_frames'])}")

            volume = float(audio.get("volume", 1.0))
            if volume != 1.0:
                db = self._db_from_ratio(volume)
                cmd.extend(["-attach-track", "volume", f"level={db:.2f}"])

        profile = self._select_profile(width, height, fps)
        cmd.extend(["-profile", profile])
        cmd.extend(
            [
                "-consumer",
                f"avformat:{output_path}",
                "vcodec=libx264",
                "acodec=aac",
                "ab=192k",
                f"width={width}",
                f"height={height}",
            ]
        )

        if self.verbose:
            print("melt command:", " ".join(cmd), file=sys.stderr)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if self.verbose:
            print(result.stdout, file=sys.stderr)

        if result.returncode != 0:
            raise ShotcutRenderError(
                f"melt failed with code {result.returncode}.\n"
                f"STDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
            )

        if not output_path.exists():
            raise ShotcutRenderError(f"Output not found: {output_path}")

        return output_path

    def assemble(
        self,
        video_paths: list[str | Path],
        output: str | Path,
        audio_clips: Optional[list[dict[str, Any]]] = None,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30,
        transition_frames: int = 0,
    ) -> Path:
        """Convenience alias for :meth:`render`."""
        return self.render(
            video_paths=video_paths,
            output=output,
            audio_clips=audio_clips,
            resolution=resolution,
            fps=fps,
            transition_frames=transition_frames,
        )
