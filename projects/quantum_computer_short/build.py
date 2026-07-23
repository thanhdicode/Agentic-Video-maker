"""Build a production-grade Vietnamese Manim Shorts about quantum computing.

Pipeline:
1. Generate edge-tts narration per scene and measure exact durations.
2. Write config.json with timings for the Manim scene.
3. Render the Manim vertical 1080x1920 (60/30 fps) 3D animation.
4. Synthesize sound effects and mix them with voice and ambient bed.
5. Burn Vietnamese subtitles into the final MP4.
6. Post-process for cinematic look.
7. Run automated QA and generate contact sheets.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT / "audio"
SCENE_FILE = PROJECT / "quantum_short.py"
CONFIG_FILE = PROJECT / "config.json"
ASS_FILE = PROJECT / "subtitles.ass"
FINAL_MP4 = PROJECT / "quantum_short_voice_sfx.mp4"
POLISHED_MP4 = PROJECT / "quantum_short_voice_sfx_polished.mp4"
MUSIC_MIX_MP4 = PROJECT / "quantum_short_reference_music_mix.mp4"

MANIM_ENV = Path("C:/Users/Administrator/manim_env")
PYTHON = MANIM_ENV / "Scripts" / "python.exe"
MANIM = MANIM_ENV / "Scripts" / "manim.exe"

VOICE = "vi-VN-NamMinhNeural"
BG_MUSIC = REPO / "assets" / "music" / "bensound-softvibes.mp3"

os.environ["PATH"] = str(Path.home() / "AppData" / "Roaming" / "TinyTeX" / "bin" / "windows") + os.pathsep + os.environ.get("PATH", "")


def run(cmd: list[str | Path], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    str_cmd = [str(c) for c in cmd]
    return subprocess.run(
        str_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **kwargs,
    )


def load_tts_tools() -> Any:
    spec = importlib.util.spec_from_file_location("tts_tools", REPO / "tools" / "tts_tools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


tts_tools = load_tts_tools()

SEGMENTS: list[dict[str, Any]] = [
    {
        "id": "01_hook",
        "type": "hook",
        "narration": "Máy tính lượng tử không nhanh vì thử mọi đáp án cùng lúc.",
    },
    {
        "id": "02_classical_bit",
        "type": "classical_bit",
        "narration": "Bí mật thật sự là: nó điều khiển sóng xác suất. Máy tính thường dùng bit, mỗi lúc chỉ là không hoặc một.",
    },
    {
        "id": "03_qubit_bloch",
        "type": "qubit_bloch",
        "narration": "Qubit có trạng thái an-pha nhân ket không, cộng bê-ta nhân ket một. Trước khi đo, hai biên độ cùng tồn tại, nhưng không thể đọc như hai đáp án.",
    },
    {
        "id": "04_hadamard",
        "type": "hadamard",
        "narration": "Cổng Hadamard xoay qubit trên mặt cầu Bloch. Khi đo, ta vẫn chỉ nhận không hoặc một.",
    },
    {
        "id": "05_bell",
        "type": "bell",
        "narration": "Với hai qubit, Hadamard rồi C-NOT tạo trạng thái Bell: chỉ không-không và một-một xuất hiện, với kết quả tương quan.",
    },
    {
        "id": "06_interference",
        "type": "interference",
        "narration": "Sức mạnh nằm ở giao thoa. Thuật toán chỉnh pha để đường sai triệt tiêu, còn đường hữu ích cộng hưởng.",
    },
    {
        "id": "07_measurement",
        "type": "measurement",
        "narration": "Phép đo biến mẫu xác suất thành kết quả cổ điển.",
    },
    {
        "id": "08_outro",
        "type": "outro",
        "narration": "Máy tính lượng tử không thay laptop. Nó là cỗ máy chuyên dụng để thiết kế giao thoa. Đó mới là điều kỳ lạ.",
    },
]


def ffprobe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    if result.returncode == 0 and result.stdout.strip():
        try:
            return float(result.stdout.strip())
        except ValueError:
            pass
    return 0.0


def generate_audio() -> list[dict[str, Any]]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    segments = []
    for seg in SEGMENTS:
        out = AUDIO_DIR / f"{seg['id']}.mp3"
        if not out.exists():
            print(f"  generating TTS for {seg['id']}...")
            tts_tools.text_to_speech(seg["narration"], str(out), voice=VOICE)
        dur = ffprobe_duration(out)
        segments.append({**seg, "duration": dur, "path": out})
    return segments


def pad_segments(segments: list[dict[str, Any]], target: float = 59.0) -> list[dict[str, Any]]:
    """Pad each segment with silence so the sum matches the target total."""
    total = sum(s["duration"] for s in segments)
    if total >= target:
        return segments
    slack = target - total
    per_seg = slack / len(segments)
    for s in segments:
        s["padded_duration"] = s["duration"] + per_seg
    return segments


def write_config(segments: list[dict[str, Any]]) -> None:
    durations = [round(s.get("padded_duration", s["duration"]), 3) for s in segments]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"segments": durations, "segment_types": [s["type"] for s in segments]}, f, indent=2, ensure_ascii=False)
    total = sum(durations)
    print(f"    config written, total target: {total:.2f}s")


def split_caption(text: str, max_chars: int = 24) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    clauses = [p.strip() for p in re.split(r"(?<=[.,:;!?])\s+", text) if p.strip()]
    result: list[str] = []
    for clause in clauses:
        if len(clause) <= max_chars:
            result.append(clause)
            continue
        words = clause.split()
        line = ""
        for w in words:
            if line and len(line) + 1 + len(w) > max_chars:
                result.append(line.strip())
                line = w
            else:
                line = f"{line} {w}" if line else w
        if line:
            result.append(line.strip())
    return [p for p in result if p]


def generate_ass(segments: list[dict[str, Any]]) -> None:
    header = """[Script Info]
Title: Quantum Computer Short Vietnamese Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,50,50,160,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines: list[str] = []
    cursor = 0.0
    for s in segments:
        start = cursor
        end = cursor + s["duration"]
        for phrase in split_caption(s["narration"], max_chars=24):
            dur_share = (end - start) / max(len(split_caption(s["narration"], max_chars=24)), 1)
            p_start = start
            p_end = min(start + dur_share, end)
            lines.append(
                f"Dialogue: 0,{ass_time(p_start)},{ass_time(p_end)},Default,,0,0,0,,{phrase}"
            )
            start = p_end
        cursor = end
    with open(ASS_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))
        f.write("\n")


def ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    sec = seconds % 60
    return f"{h}:{m:02d}:{sec:05.2f}".replace(".", ",")


def concatenate_audio(segments: list[dict[str, Any]]) -> Path:
    list_file = PROJECT / "concat_list.txt"
    out = AUDIO_DIR / "narration_padded.mp3"
    entries = []
    for i, s in enumerate(segments):
        entries.append(s["path"])
        pad = s.get("padded_duration", s["duration"]) - s["duration"]
        if pad > 0.001:
            silence = AUDIO_DIR / f"silence_{i:02d}.mp3"
            if not silence.exists():
                result = run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        "anullsrc=r=24000:cl=mono",
                        "-t",
                        f"{pad:.3f}",
                        "-c:a",
                        "libmp3lame",
                        "-q:a",
                        "9",
                        silence,
                    ]
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Silence generation failed: {result.stderr}\n{result.stdout}")
            entries.append(silence)
    with open(list_file, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"file '{e.resolve().as_posix()}'\n")
    result = run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", out],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Audio concat failed: {result.stderr}\n{result.stdout}")
    return out


def render_manim() -> Path:
    print("Rendering Manim quantum scene...")
    result = run(
        [
            str(MANIM),
            "-q",
            "l",
            "--disable_caching",
            "-o",
            "QuantumComputerShort",
            str(SCENE_FILE),
            "QuantumComputerShort",
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr}\n{result.stdout}")
    out = (
        PROJECT
        / "media"
        / "videos"
        / "quantum_short"
        / "1080p60"
        / "QuantumComputerShort.mp4"
    )
    if not out.exists():
        matches = list((PROJECT / "media" / "videos" / "quantum_short").rglob("QuantumComputerShort.mp4"))
        if matches:
            out = matches[0]
        else:
            raise RuntimeError("Manim did not produce QuantumComputerShort.mp4")
    return out


def make_sfx(name: str, expr: str, duration: float, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return
    result = run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            expr,
            "-t",
            str(duration),
            "-ar",
            "48000",
            "-ac",
            "2",
            out,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"SFX {name} failed: {result.stderr}")


def generate_sfx_library() -> dict[str, Path]:
    print("\nSynthesizing sound effects...")
    sfx_dir = AUDIO_DIR / "sfx"
    sfx: dict[str, Path] = {}

    # Low bass impact for binary tunnel hit
    make_sfx(
        "bass_impact",
        "aevalsrc=0.6*sin(2*PI*80*t)*exp(-t*8):s=48000",
        0.5,
        sfx_dir / "bass_impact.wav",
    )
    sfx["bass_impact"] = sfx_dir / "bass_impact.wav"

    # Digital snap / shatter
    make_sfx(
        "digital_snap",
        "anoisesrc=a=0.4:d=0.08:color=pink",
        0.08,
        sfx_dir / "digital_snap.wav",
    )
    sfx["digital_snap"] = sfx_dir / "digital_snap.wav"

    # Quantum pulse
    make_sfx(
        "quantum_pulse",
        "aevalsrc=0.4*sin(2*PI*800*t)*exp(-t*10):s=48000",
        0.12,
        sfx_dir / "quantum_pulse.wav",
    )
    sfx["quantum_pulse"] = sfx_dir / "quantum_pulse.wav"

    # Switch click
    make_sfx(
        "switch_click",
        "aevalsrc=0.4*sgn(sin(2*PI*1200*t))*exp(-t*15):s=48000",
        0.05,
        sfx_dir / "switch_click.wav",
    )
    sfx["switch_click"] = sfx_dir / "switch_click.wav"

    # Electric riser
    make_sfx(
        "riser",
        "aevalsrc=0.25*sin(2*PI*(200+1800*t)*t)*exp(-t*0.2):s=48000",
        2.0,
        sfx_dir / "riser.wav",
    )
    sfx["riser"] = sfx_dir / "riser.wav"

    # Interference hit
    make_sfx(
        "interference_hit",
        "aevalsrc=0.5*sin(2*PI*(60*exp(t*2)))*exp(-t*3):s=48000",
        0.6,
        sfx_dir / "interference_hit.wav",
    )
    sfx["interference_hit"] = sfx_dir / "interference_hit.wav"

    # Measurement sweep whoosh + snap
    make_sfx(
        "sweep_snap",
        "aevalsrc=0.35*sin(2*PI*(200+2000*t)*t)*exp(-t*2.5):s=48000",
        0.5,
        sfx_dir / "sweep_snap.wav",
    )
    sfx["sweep_snap"] = sfx_dir / "sweep_snap.wav"

    return sfx


def make_music_bed(duration: float) -> Path:
    """Loop/trim the royalty-free background music to the video duration."""
    bed_path = AUDIO_DIR / "music_bed.wav"
    if not bed_path.exists() or ffprobe_duration(bed_path) < duration - 1:
        if BG_MUSIC.exists():
            result = run(
                [
                    "ffmpeg",
                    "-y",
                    "-stream_loop",
                    "-1",
                    "-i",
                    BG_MUSIC,
                    "-t",
                    str(duration + 2),
                    "-af",
                    "volume=0.18",
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    bed_path,
                ]
            )
            if result.returncode != 0:
                raise RuntimeError(f"Music bed creation failed: {result.stderr}\n{result.stdout}")
        else:
            # fallback generated drone if music file missing
            result = run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "anoisesrc=a=0.04:color=brown",
                    "-af",
                    "lowpass=f=600, volume=0.35, asetrate=48000*0.8",
                    "-t",
                    str(duration + 2),
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    bed_path,
                ]
            )
            if result.returncode != 0:
                raise RuntimeError(f"Ambient bed creation failed: {result.stderr}\n{result.stdout}")
    return bed_path


def build_sfx_timeline(sfx: dict[str, Path], duration: float) -> Path:
    """Mix all SFX on a dedicated track aligned to storyboard events."""
    timeline = [
        ("bass_impact", 0.0, 0.5, 0.8),
        ("digital_snap", 1.1, 0.08, 0.7),
        ("quantum_pulse", 1.7, 0.12, 0.6),
        ("riser", 3.5, 2.0, 0.35),
        ("switch_click", 6.0, 0.05, 0.5),
        ("switch_click", 7.0, 0.05, 0.5),
        ("quantum_pulse", 9.5, 0.12, 0.5),
        ("quantum_pulse", 17.0, 0.12, 0.6),
        ("riser", 18.5, 2.0, 0.3),
        ("sweep_snap", 23.0, 0.5, 0.7),
        ("quantum_pulse", 26.5, 0.12, 0.5),
        ("quantum_pulse", 28.0, 0.12, 0.5),
        ("digital_snap", 30.5, 0.08, 0.6),
        ("sweep_snap", 33.5, 0.5, 0.6),
        ("riser", 35.0, 5.0, 0.3),
        ("interference_hit", 43.0, 0.6, 0.9),
        ("sweep_snap", 49.5, 0.5, 0.7),
        ("digital_snap", 56.0, 0.08, 0.5),
    ]
    inputs: list[str] = []
    filter_parts: list[str] = []
    for i, (name, start, dur, vol) in enumerate(timeline):
        if name not in sfx:
            continue
        inputs.extend(["-i", str(sfx[name])])
        filter_parts.append(f"[{i}:a]adelay={int(start*1000)}|{int(start*10000)},volume={vol}[s{i}]")
    if not filter_parts:
        # empty SFX track: silence
        silence = AUDIO_DIR / "sfx_silence.wav"
        make_sfx("silence", "aevalsrc=0:s=48000", duration, silence)
        inputs = ["-i", str(silence)]
        filter_parts = ["[0:a]acopy[s0]"]
    mix_input_labels = "".join(f"[s{i}]" for i in range(len(filter_parts)))
    filter_complex = ";".join(filter_parts) + f";{mix_input_labels}amix=inputs={len(filter_parts)}:duration=longest[sfxmix]"
    out = AUDIO_DIR / "sfx_track.wav"
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[sfxmix]", "-ar", "48000", "-ac", "2", out]
    result = run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"SFX timeline mix failed: {result.stderr}\n{result.stdout}")
    return out


def assemble_final(video: Path, narration: Path, sfx: Path, music: Path, music_file: Path | None = None) -> Path:
    if music_file and music_file.exists():
        # Reference music mix: duck music under voice
        result = run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video,
                "-i",
                narration,
                "-i",
                sfx,
                "-i",
                music_file,
                "-filter_complex",
                "[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.9',volume=1.5[voice_sfx];"
                "[3:a]afade=t=in:ss=0:d=1,afade=t=out:st=57:d=2,asetnsamples=n=480*100[bed];"
                "[voice_sfx][bed]amix=inputs=2:duration=first:weights='1 0.18'[aout]",
                "-map",
                "0:v",
                "-map",
                "[aout]",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-preset",
                "medium",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-pix_fmt",
                "yuv420p",
                "-vf",
                "subtitles=subtitles.ass",
                "-movflags",
                "+faststart",
                str(MUSIC_MIX_MP4),
            ],
            cwd=str(PROJECT),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Music mix assembly failed: {result.stderr}\n{result.stdout}")
        return MUSIC_MIX_MP4

    # Voice + SFX + ambient bed
    result = run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video,
            "-i",
            narration,
            "-i",
            sfx,
            "-i",
            music,
            "-filter_complex",
            "[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.8',volume=1.5[voice_sfx];"
            "[voice_sfx][3:a]amix=inputs=2:duration=first:weights='1 0.12'[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "subtitles=subtitles.ass",
            "-movflags",
            "+faststart",
            str(FINAL_MP4),
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Final assembly failed: {result.stderr}\n{result.stdout}")
    return FINAL_MP4


def polish_video(input_path: Path, output_path: Path) -> Path:
    """Post-process the final MP4 for a more cinematic look."""
    print("\nPost-processing final video (color, sharpen, vignette)...")
    result = run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            "eq=contrast=1.1:saturation=1.1:brightness=0.02,curves=all='0/0 0.5/0.52 1/1',unsharp=5:5:1.0:5:5:0.0,vignette=PI/5",
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            output_path,
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Polish failed: {result.stderr}\n{result.stdout}")
    return output_path


def run_qa(final: Path, contact_sheet_path: Path) -> dict[str, Any]:
    print("\nRunning automated QA...")
    report: dict[str, Any] = {}
    # duration
    report["duration"] = ffprobe_duration(final)
    # resolution, fps, codecs
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,codec_name,pix_fmt",
            "-of",
            "json",
            str(final),
        ]
    )
    if result.returncode == 0:
        report["video_stream"] = json.loads(result.stdout or "{}")
    # audio stream
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate",
            "-of",
            "json",
            str(final),
        ]
    )
    if result.returncode == 0:
        report["audio_stream"] = json.loads(result.stdout or "{}")
    # loudness
    result = run(
        ["ffmpeg", "-y", "-i", final, "-af", "ebur128=peak=true", "-f", "null", "-"]
    )
    report["loudness_log"] = result.stderr.splitlines()[-20:] if result.stderr else []

    # extract frames and build contact sheet (6x6 grid)
    dur = report.get("duration", 0.0) or 59.0
    if dur > 0:
        frames_dir = PROJECT / "qa" / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        count = 18
        times = [dur * i / (count - 1) for i in range(count)]
        for i, ts in enumerate(times):
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    final,
                    "-ss",
                    str(ts),
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    frames_dir / f"frame_{i:03d}.png",
                ]
            )
        montage_cmd = [
            "ffmpeg",
            "-y",
            "-pattern_type",
            "glob",
            "-i",
            str(frames_dir / "*.png"),
            "-filter_complex",
            "scale=320:-1,tile=3x6",
            contact_sheet_path,
        ]
        run(montage_cmd)
    report["contact_sheet"] = str(contact_sheet_path)
    return report


def main() -> None:
    print("=" * 60)
    print("Building Quantum Computing Short")
    print("=" * 60)

    print("\n1/8 Generating narration with edge-tts...")
    segments = generate_audio()

    print("\n2/8 Padding and writing config...")
    segments = pad_segments(segments, target=59.0)
    write_config(segments)

    print("\n3/8 Generating Vietnamese subtitles...")
    generate_ass(segments)

    print("\n4/8 Rendering Manim animation...")
    video_path = render_manim()
    print(f"    -> {video_path}")
    video_dur = ffprobe_duration(video_path)
    print(f"    video duration: {video_dur:.2f}s")

    print("\n5/8 Preparing audio (narration + SFX + ambient bed)...")
    narration_path = concatenate_audio(segments)
    sfx = generate_sfx_library()
    sfx_track = build_sfx_timeline(sfx, video_dur)
    music_bed = make_music_bed(video_dur)

    print("\n6/8 Assembling final video...")
    music_file: Path | None = None
    if len(sys.argv) > 2 and sys.argv[1] == "--with-music":
        music_file = Path(sys.argv[2])
    final = assemble_final(video_path, narration_path, sfx_track, music_bed, music_file=music_file)
    print(f"    -> {final}")

    print("\n7/8 Post-processing...")
    polished = polish_video(final, POLISHED_MP4)
    print(f"    -> {polished}")

    print("\n8/8 Running QA...")
    contact_sheet = PROJECT / "qa" / "contact_sheet_pass2.png"
    report = run_qa(polished, contact_sheet)

    print(f"\nDone. Final duration: {report['duration']:.2f}s")
    print(f"Contact sheet: {contact_sheet}")

    # write QA report
    with open(PROJECT / "qa" / "qa_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        segs = generate_audio()
        segs = pad_segments(segs, target=59.0)
        write_config(segs)
        generate_ass(segs)
        print(f"\nAudio+config prepared. Total narration: {sum(s['duration'] for s in segs):.2f}s")
    else:
        main()
