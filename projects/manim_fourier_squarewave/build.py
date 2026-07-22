"""Build a high-end Manim Shorts about the Fourier series of a square wave.

Pipeline:
1. Generate edge-tts narration per segment and measure exact durations.
2. Write config.json with timings for the Manim scene.
3. Render the Manim vertical 1080x1920 animation (LaTeX formulas).
4. Loop background music to video length and mix it with narration.
5. Burn English subtitles into the final MP4.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT / "audio"
SCENE_FILE = PROJECT / "fourier_squarewave.py"
CONFIG_FILE = PROJECT / "config.json"
ASS_FILE = PROJECT / "subtitles.ass"
FINAL_MP4 = PROJECT / "fourier_squarewave.mp4"

# External tooling
MANIM_ENV = Path("C:/Users/Administrator/manim_env")
PYTHON = MANIM_ENV / "Scripts" / "python.exe"
MANIM = MANIM_ENV / "Scripts" / "manim.exe"

VOICE = "en-US-AvaNeural"
BG_MUSIC = REPO / "assets" / "music" / "pamgaea.mp3"

# Make TinyTeX available for MathTex rendering
os.environ["PATH"] = str(Path.home() / "AppData" / "Roaming" / "TinyTeX" / "bin" / "windows") + os.pathsep + os.environ.get("PATH", "")

# ---------------------------------------------------------------------------
# Import tools/tts_tools without pulling heavy tools/__init__.py
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
        "id": "01_hook",
        "type": "hook",
        "narration": "What if I told you a square wave is made of spinning circles?",
    },
    {
        "id": "02_setup",
        "type": "setup",
        "narration": "Any repeating shape can be built from sine waves.",
    },
    {
        "id": "03_formula",
        "type": "formula",
        "narration": "A square wave equals four over pi, times the sum of odd sine harmonics.",
    },
    {
        "id": "04_harmonic_1",
        "type": "harmonic_1",
        "narration": "Start with the first harmonic.",
    },
    {
        "id": "05_harmonic_3",
        "type": "harmonic_3",
        "narration": "Add the third harmonic, and the shape starts to sharpen.",
    },
    {
        "id": "06_harmonic_5",
        "type": "harmonic_5",
        "narration": "The fifth harmonic adds more corners.",
    },
    {
        "id": "07_harmonic_7",
        "type": "harmonic_7",
        "narration": "Seven terms, and it already looks like a staircase.",
    },
    {
        "id": "08_harmonic_9",
        "type": "harmonic_9",
        "narration": "Nine terms, the square wave is almost perfect.",
    },
    {
        "id": "09_payoff",
        "type": "payoff",
        "narration": "Keep adding odd harmonics forever, and you get a perfect square wave.",
    },
    {
        "id": "10_formula_reveal",
        "type": "formula_reveal",
        "narration": "This is the Fourier series.",
    },
    {
        "id": "11_cta",
        "type": "cta",
        "narration": "Follow for more math magic.",
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
        "background_color": "#0d0d0d",
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
        "Title: Fourier Square Wave",
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


def make_music_bed(target_duration: float) -> Path:
    """Loop the background music to match the target video duration."""
    bed_path = AUDIO_DIR / "music_bed.mp3"
    result = run(
        [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            BG_MUSIC,
            "-t",
            str(target_duration),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "4",
            bed_path,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"Music bed creation failed: {result.stderr}")
    return bed_path


def render_manim() -> Path:
    """Render the Manim scene."""
    print("Rendering Manim Fourier scene...")
    result = run(
        [
            str(MANIM),
            "-q",
            "l",
            "--disable_caching",
            "-o",
            "FourierSquareWave",
            str(SCENE_FILE),
            "FourierSquareWave",
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr}\n{result.stdout}")
    out = (
        PROJECT
        / "media"
        / "videos"
        / "fourier_squarewave"
        / "1920p30"
        / "FourierSquareWave.mp4"
    )
    if not out.exists():
        matches = list((PROJECT / "media" / "videos" / "fourier_squarewave").rglob("FourierSquareWave.mp4"))
        if matches:
            out = matches[0]
        else:
            raise RuntimeError("Manim did not produce FourierSquareWave.mp4")
    return out


def assemble_final(video: Path, audio: Path, music: Path) -> Path:
    """Combine video + narration + background music and burn English ASS subtitles."""
    result = run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video,
            "-i",
            audio,
            "-i",
            music,
            "-filter_complex",
            "[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.18'[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
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
    print("Building 'Fourier Square Wave' Manim Shorts")
    print("=" * 60)

    print("\n1/6 Generating narration with edge-tts...")
    segments = generate_audio()

    print("\n2/6 Writing config.json for Manim...")
    write_config(segments)

    print("\n3/6 Generating English subtitles...")
    generate_ass(segments)

    print("\n4/6 Rendering Manim animation...")
    video_path = render_manim()
    print(f"    -> {video_path}")
    video_dur = ffprobe_duration(video_path)
    print(f"    video duration: {video_dur:.2f}s")

    print("\n5/6 Preparing background music bed...")
    audio_path = concatenate_audio(segments)
    music_path = make_music_bed(video_dur)

    print("\n6/6 Assembling final video...")
    final = assemble_final(video_path, audio_path, music_path)
    print(f"    -> {final}")

    dur = ffprobe_duration(final)
    print(f"\nDone. Final duration: {dur:.2f}s")


if __name__ == "__main__":
    main()
