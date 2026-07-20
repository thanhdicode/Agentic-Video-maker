"""Generate simple educational visual clips from text prompts and narration audio."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


class VisualGenerationError(Exception):
    """Raised when a visual clip cannot be rendered."""

    pass


def _esc(s: str) -> str:
    """Escape drawtext special characters."""
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _resolve_font(font: str | None) -> str:
    if font and Path(font).exists():
        return str(Path(font).resolve())

    env_font = os.environ.get("EDU_VIDEO_FONT")
    if env_font and Path(env_font).exists():
        return env_font

    common = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in common:
        if Path(p).exists():
            return p

    raise VisualGenerationError(
        "No font found. Set EDU_VIDEO_FONT or place a TTF in the project."
    )


def generate_visual_clip(
    visual_text: str,
    audio_path: str | Path,
    output: str | Path,
    bg_color: str = "0x3B82F6",
    font: str | None = None,
    text_color: str = "white",
    font_size: int = 60,
    text_y_ratio: float = 0.12,
) -> Path:
    """Create an H.264 MP4 clip from a colored background, text, and narration audio."""
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    font_path = _resolve_font(font)

    # drawtext cannot parse Windows drive letters (C:) in fontfile, so copy
    # the font next to the output and reference it by name.
    local_font = out_path.parent / "arial.ttf"
    if not local_font.exists():
        shutil.copy(font_path, local_font)
    font_arg = "arial.ttf"

    vf = (
        f"drawtext=fontfile={font_arg}:text={_esc(visual_text)}:"
        f"fontsize={font_size}:fontcolor={text_color}:"
        f"x=(w-text_w)/2:y=(h-text_h)*{text_y_ratio}:"
        f"box=1:boxcolor=black@0.5:boxborderw=10"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s=1280x720:r=30",
        "-i", str(audio_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest",
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(out_path.parent))
    if result.returncode != 0:
        raise VisualGenerationError(
            f"ffmpeg visual clip failed: {result.stderr}\n{result.stdout}"
        )
    if not out_path.exists():
        raise VisualGenerationError("Visual clip output not found")
    return out_path


def assemble_edu_video(
    scene_paths: list[str | Path],
    output: str | Path,
    music_path: str | Path | None = None,
    music_volume: float = 0.2,
) -> Path:
    """Concatenate scene clips and optionally mix background music."""
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    concat_dir = out_path.parent / ".concat"
    concat_dir.mkdir(parents=True, exist_ok=True)
    list_file = concat_dir / "list.txt"
    list_file.write_text(
        "\n".join(f"file '{Path(p).resolve()}'" for p in scene_paths), encoding="utf-8"
    )

    if music_path and Path(music_path).exists():
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex", f"[0:a][1:a]amix=inputs=2:duration=first:weights=1 {music_volume}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy",
            str(out_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise VisualGenerationError(
            f"ffmpeg assembly failed: {result.stderr}\n{result.stdout}"
        )
    if not out_path.exists():
        raise VisualGenerationError("Assembled video output not found")
    return out_path
