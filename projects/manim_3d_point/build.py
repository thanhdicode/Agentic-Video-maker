"""Build a 3Blue1Brown-style Shorts about plotting a point in 3D space.

Pipeline:
1. Generate edge-tts narration per segment and measure exact durations.
2. Write config.json with durations for the Manim scene.
3. Render the Manim vertical 1080x1920 animation.
4. Concatenate audio and burn English subtitles into the final MP4.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT / "audio"
SCENE_FILE = PROJECT / "plot_point_3d.py"
CONFIG_FILE = PROJECT / "config.json"
ASS_FILE = PROJECT / "subtitles.ass"
FINAL_MP4 = PROJECT / "plot_point_in_space.mp4"

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


tts_tools = load_tts_tools()

# ---------------------------------------------------------------------------
# Script segments (English narration)
# ---------------------------------------------------------------------------
SEGMENTS: list[dict[str, Any]] = [
    {
        "id": "01_title",
        "type": "title",
        "narration": "Plot a point in space.",
    },
    {
        "id": "02_axes",
        "type": "axes",
        "narration": "We need three axes: x, y, and z.",
    },
    {
        "id": "03_coords",
        "type": "coords",
        "narration": "A point in 3D is written as x, y, z.",
    },
    {
        "id": "04_plot_x",
        "type": "plot_x",
        "narration": "Start at the origin, and move 3 units along x.",
    },
    {
        "id": "05_plot_y",
        "type": "plot_y",
        "narration": "Then 2 units parallel to y.",
    },
    {
        "id": "06_plot_z",
        "type": "plot_z",
        "narration": "Finally, 5 units up, parallel to z.",
    },
    {
        "id": "07_reveal",
        "type": "reveal",
        "narration": "So the point is (3, 2, 5).",
    },
    {
        "id": "08_outro",
        "type": "outro",
        "narration": "Plotting in 3D is just three steps.",
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
        "axis_x_color": "#FF5252",
        "axis_y_color": "#69F0AE",
        "axis_z_color": "#4FC3F7",
        "point_color": "#FFD600",
        "voice": VOICE,
        "segments": [
            {
                "type": seg["type"],
                "duration": seg["duration"],
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
            clean = phrase.replace("\n", "\\N")
            entries.append((format_ass_time(start), format_ass_time(end), clean))
            cursor += phrase_dur

    ass_lines = [
        "[Script Info]",
        "Title: Plot a Point in Space",
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
    print("Rendering Manim 3D scene...")
    result = run(
        [
            str(MANIM),
            "-q",
            "l",
            "--disable_caching",
            "-o",
            "PlotPoint3D",
            str(SCENE_FILE),
            "PlotPoint3D",
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr}\n{result.stdout}")
    # Manim writes to media/videos/plot_point_3d/<quality>/PlotPoint3D.mp4
    out = (
        PROJECT
        / "media"
        / "videos"
        / "plot_point_3d"
        / "1920p30"
        / "PlotPoint3D.mp4"
    )
    if not out.exists():
        matches = list((PROJECT / "media" / "videos" / "plot_point_3d").rglob("PlotPoint3D.mp4"))
        if matches:
            out = matches[0]
        else:
            raise RuntimeError("Manim did not produce PlotPoint3D.mp4")
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
    print("Building 'Plot a Point in Space' Manim Shorts")
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
