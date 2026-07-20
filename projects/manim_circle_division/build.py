"""Build a 3Blue1Brown-style "Don't let it fool you!" Shorts about Moser's circle problem.

Pipeline:
1. Generate edge-tts narration per segment and measure exact durations.
2. Write config.json with durations for the Manim scene.
3. Render the Manim vertical 1080x1920 animation.
4. Concatenate audio and burn English subtitles into the final MP4.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT / "audio"
SCENE_FILE = PROJECT / "circle_division.py"
CONFIG_FILE = PROJECT / "config.json"
ASS_FILE = PROJECT / "subtitles.ass"
FINAL_MP4 = PROJECT / "dont_let_it_fool_you.mp4"

# Use the local Manim venv if available
MANIM_ENV = Path("C:/Users/Administrator/manim_env")
PYTHON = MANIM_ENV / "Scripts" / "python.exe"
MANIM = MANIM_ENV / "Scripts" / "manim.exe"

VOICE = "en-US-GuyNeural"

# ---------------------------------------------------------------------------
# Import tools/tts_tools without pulling the heavy tools/__init__.py
# ---------------------------------------------------------------------------
def load_tts_tools() -> Any:
    spec = importlib.util.spec_from_file_location("tts_tools", REPO / "tools" / "tts_tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


import importlib.util

tts_tools = load_tts_tools()

# ---------------------------------------------------------------------------
# Script segments (English narration)
# ---------------------------------------------------------------------------
SEGMENTS: list[dict[str, Any]] = [
    {
        "id": "01_title",
        "type": "title",
        "narration": "Don't let it fool you!",
    },
    {
        "id": "02_intro",
        "type": "intro",
        "narration": "Here's a famous cautionary tale in math, known as Moser's circle problem.",
    },
    {
        "id": "03_one",
        "type": "step",
        "n": 1,
        "count": 1,
        "narration": "Start with a circle, and put one point on it. There's exactly one region.",
    },
    {
        "id": "04_two",
        "type": "step",
        "n": 2,
        "count": 2,
        "narration": "Add a second point and connect them with a chord. The circle is split into two regions.",
    },
    {
        "id": "05_four",
        "type": "step",
        "n": 3,
        "count": 4,
        "narration": "Add a third point and connect it to the previous two. Now we have four regions.",
    },
    {
        "id": "06_eight",
        "type": "step",
        "n": 4,
        "count": 8,
        "narration": "A fourth point, connected to the previous three, gives eight regions.",
    },
    {
        "id": "07_sixteen",
        "type": "step",
        "n": 5,
        "count": 16,
        "narration": "A fifth point, connected to all four, gives sixteen regions.",
    },
    {
        "id": "08_pattern",
        "type": "pattern",
        "sequence": [1, 2, 4, 8, 16],
        "narration": "The pattern looks like powers of two. One, two, four, eight, sixteen.",
    },
    {
        "id": "09_expect",
        "type": "expect",
        "n": 6,
        "wrong_count": 32,
        "narration": "So you'd expect a sixth point to give thirty-two.",
    },
    {
        "id": "10_reveal",
        "type": "reveal",
        "n": 6,
        "correct_count": 31,
        "narration": "But count carefully, and you get thirty-one.",
    },
    {
        "id": "11_outro",
        "type": "outro",
        "sequence": [1, 2, 4, 8, 16, 31],
        "narration": "Just one shy of a power of two. Don't let it fool you.",
    },
]


def run(cmd: list[str | Path], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Run a command and capture output."""
    str_cmd = [str(c) for c in cmd]
    return subprocess.run(str_cmd, capture_output=True, text=True, **kwargs)


def ffprobe_duration(path: Path) -> float:
    """Return audio/video duration in seconds."""
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ]
    )
    return float(result.stdout.strip()) if result.returncode == 0 else 0.0


def generate_audio() -> list[dict[str, Any]]:
    """Render narration audio for every segment and record exact durations."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for seg in SEGMENTS:
        mp3_path = AUDIO_DIR / f"{seg['id']}.mp3"
        if not mp3_path.exists():
            print(f"  TTS -> {mp3_path.name}: {seg['narration'][:50]}...")
            tts_tools.text_to_speech(seg["narration"], mp3_path, voice=VOICE)
        seg["duration"] = ffprobe_duration(mp3_path)
        seg["audio"] = str(mp3_path)
        print(f"    duration: {seg['duration']:.3f}s")
    return SEGMENTS


def write_config(segments: list[dict[str, Any]]) -> None:
    """Write the Manim scene config with timings and color palette."""
    config = {
        "background_color": "#111111",
        "circle_radius": 3.2,
        "point_color": "#FF5252",
        "line_color": "#4FC3F7",
        "text_color": "#FFFFFF",
        "accent_color": "#FFD600",
        "voice": VOICE,
        "segments": [
            {
                "type": seg["type"],
                "duration": seg["duration"],
                **{
                    k: v
                    for k, v in seg.items()
                    if k in {"n", "count", "wrong_count", "correct_count", "sequence"}
                },
            }
            for seg in segments
        ],
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def split_caption(text: str, pieces: int = 2) -> list[str]:
    """Split a narration line into a few short subtitle phrases by words."""
    words = text.split()
    if len(words) <= 5 or pieces <= 1:
        return [text]
    k = len(words) // pieces
    parts = []
    start = 0
    for i in range(pieces - 1):
        parts.append(" ".join(words[start : start + k]))
        start += k
    parts.append(" ".join(words[start:]))
    return [p for p in parts if p]


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS h:mm:ss.cc."""
    cs = int(round(seconds * 100))
    s = cs // 100
    cs -= s * 100
    m = s // 60
    s -= m * 60
    h = m // 60
    m -= h * 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_ass(segments: list[dict[str, Any]]) -> None:
    """Generate an ASS subtitle file with bottom-center white text + black outline."""
    entries = []
    cursor = 0.0
    for seg in segments:
        dur = seg["duration"]
        text = seg["narration"]
        # Split long narrations into 1-3 short phrases for better readability
        pieces = 1 if dur < 2.5 else (2 if dur < 5.0 else 3)
        phrases = split_caption(text, pieces)

        word_count = len(text.split())
        for phrase in phrases:
            phrase_words = len(phrase.split())
            phrase_dur = dur * (phrase_words / max(word_count, 1))
            start = cursor
            end = cursor + phrase_dur
            # ASS dialogue text: replace newlines with \N, strip wrapping
            clean = phrase.replace("\n", "\\N")
            entries.append((format_ass_time(start), format_ass_time(end), clean))
            cursor += phrase_dur

    ass_lines = [
        "[Script Info]",
        "Title: Don't let it fool you!",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,44,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,10,10,80,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for start, end, text in entries:
        ass_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    ASS_FILE.write_text("\n".join(ass_lines), encoding="utf-8")


def concatenate_audio(segments: list[dict[str, Any]]) -> Path:
    """Join all segment MP3s into one narration track."""
    concat_txt = AUDIO_DIR / "concat.txt"
    concat_txt.write_text(
        "\n".join(f"file '{Path(seg['audio']).resolve()}'" for seg in segments),
        encoding="utf-8",
    )
    full_mp3 = AUDIO_DIR / "narration_full.mp3"
    result = run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_txt,
            "-c",
            "copy",
            full_mp3,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"Audio concat failed: {result.stderr}")
    return full_mp3


def render_manim() -> Path:
    """Render the Manim scene."""
    print("Rendering Manim scene...")
    result = run(
        [
            str(MANIM),
            "-q",
            "l",
            "--disable_caching",
            "-o",
            "CircleDivision",
            str(SCENE_FILE),
            "CircleDivision",
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr}\n{result.stdout}")
    # Manim writes to media/videos/circle_division/1920p15/CircleDivision.mp4
    # because the scene sets a vertical 1080x1920 resolution.
    out = PROJECT / "media" / "videos" / "circle_division" / "1920p15" / "CircleDivision.mp4"
    if not out.exists():
        # Fallback search
        matches = list(PROJECT.rglob("CircleDivision.mp4"))
        if matches:
            out = matches[0]
        else:
            raise RuntimeError("Manim did not produce CircleDivision.mp4")
    return out


def assemble_final(video: Path, audio: Path) -> Path:
    """Combine video + audio and burn English ASS subtitles."""
    result = run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video,
            "-i",
            audio,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-vf",
            "subtitles=subtitles.ass",
            FINAL_MP4.name,
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Final assembly failed: {result.stderr}")
    return FINAL_MP4


def main() -> None:
    print("=" * 60)
    print("Building 'Don't let it fool you!' Manim Shorts")
    print("=" * 60)

    print("\n1/5 Generating narration with edge-tts...")
    segments = generate_audio()

    print("\n2/5 Writing config.json for Manim...")
    write_config(segments)

    print("\n3/5 Generating English subtitles...")
    generate_ass(segments)

    print("\n4/5 Rendering Manim animation...")
    video_path = render_manim()
    print(f"    -> {video_path}")

    print("\n5/5 Assembling final video...")
    audio_path = concatenate_audio(segments)
    final = assemble_final(video_path, audio_path)
    print(f"    -> {final}")

    dur = ffprobe_duration(final)
    print(f"\nDone. Final duration: {dur:.2f}s")


if __name__ == "__main__":
    main()
