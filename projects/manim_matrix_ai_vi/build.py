"""Build a Vietnamese 3D Manim Shorts: matrix multiplication is the heart of AI.

Pipeline:
1. Generate edge-tts narration per segment and measure exact durations.
2. Write config.json with timings for the Manim scene.
3. Render the Manim vertical 1080x1920 3D animation.
4. Loop background music and mix it with narration.
5. Burn Vietnamese subtitles into the final MP4.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT / "audio"
SCENE_FILE = PROJECT / "matrix_ai_vi.py"
CONFIG_FILE = PROJECT / "config.json"
ASS_FILE = PROJECT / "subtitles.ass"
FINAL_MP4 = PROJECT / "matrix_ai_vi.mp4"
POLISHED_MP4 = PROJECT / "matrix_ai_vi_polished.mp4"

MANIM_ENV = Path("C:/Users/Administrator/manim_env")
PYTHON = MANIM_ENV / "Scripts" / "python.exe"
MANIM = MANIM_ENV / "Scripts" / "manim.exe"

VOICE = "vi-VN-HoaiMyNeural"
BG_MUSIC = REPO / "assets" / "music" / "bensound-softvibes.mp3"

os.environ["PATH"] = str(Path.home() / "AppData" / "Roaming" / "TinyTeX" / "bin" / "windows") + os.pathsep + os.environ.get("PATH", "")


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
        "narration": "Mỗi khi AI nhận diện khuôn mặt hay dịch một câu, nó chỉ làm một việc: nhân ma trận.",
    },
    {
        "id": "02_matrix_transform",
        "type": "matrix_transform",
        "narration": "Ma trận không phải bảng số khô khan. Nó là phép biến hình không gian: xoay, kéo, nghiêng, phóng to.",
    },
    {
        "id": "03_cube_3d",
        "type": "cube_3d",
        "narration": "Hãy tưởng tượng một khối lập phương trong không gian ba chiều. Mỗi điểm có ba tọa độ: x, y, z.",
    },
    {
        "id": "04_basis",
        "type": "basis",
        "narration": "Ba trục i, j, k là bộ cơ sở. Một ma trận ba ba nói cho ta biết mỗi trục sẽ đi đâu sau phép biến hình.",
    },
    {
        "id": "05_W1",
        "type": "W1",
        "narration": "Áp dụng ma trận W1: khối lập phương xoay và kéo. Các trục cơ sở cũng dịch chuyển theo đúng ba cột của W1.",
    },
    {
        "id": "06_W2",
        "type": "W2",
        "narration": "Tiếp theo, áp dụng W2. Không gian lại biến hình một lần nữa, tạo thành tích hợp mới.",
    },
    {
        "id": "07_composition",
        "type": "composition",
        "narration": "Nhân W2 với W1 nghĩa là thực hiện cả hai trong một bước. Ma trận tích M cho kết quả y hệt.",
    },
    {
        "id": "08_why",
        "type": "why",
        "narration": "Mỗi cột của M chính là W2 tác động lên cột tương ứng của W1. Đó là lý do người ta định nghĩa phép nhân ma trận như vậy.",
    },
    {
        "id": "09_neural_net",
        "type": "neural_net",
        "narration": "Mạng nơ-ron cũng chỉ làm điều này. Mỗi lớp là một ma trận. Dữ liệu đi qua chuỗi các phép biến hình để ra dự đoán.",
    },
    {
        "id": "10_forward_pass",
        "type": "forward_pass",
        "narration": "Đầu vào x, nhân W1, cộng bias, qua hàm kích hoạt ReLU, rồi W2, W3, cho đến khi ra kết quả.",
    },
    {
        "id": "11_recap_cta",
        "type": "recap_cta",
        "narration": "Vậy AI không hề ma thuật. Nó là hàng triệu phép nhân ma trận ghép lại. Theo dõi để xem thêm toán học đằng sau AI.",
    },
]


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


def ffprobe_duration(path: Path) -> float:
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


TARGET_TOTAL = 120.0


def generate_audio() -> list[dict[str, Any]]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    raw_paths: list[tuple[dict[str, Any], Path]] = []
    for seg in SEGMENTS:
        mp3_path = AUDIO_DIR / f"{seg['id']}.mp3"
        if not mp3_path.exists():
            print(f"  TTS -> {mp3_path.name}")
            tts_tools.text_to_speech(seg["narration"], mp3_path, voice=VOICE)
        raw_paths.append((seg, mp3_path))

    raw_durs = [ffprobe_duration(p) for _, p in raw_paths]
    total_raw = sum(raw_durs)
    pad_each = max(0.0, (TARGET_TOTAL - total_raw) / len(SEGMENTS)) if total_raw < TARGET_TOTAL else 0.0
    print(f"  total raw narration: {total_raw:.2f}s; adding {pad_each:.2f}s silence per segment")

    for seg, raw_path in raw_paths:
        raw_dur = ffprobe_duration(raw_path)
        seg["raw_duration"] = raw_dur
        target_dur = raw_dur + pad_each
        padded_path = AUDIO_DIR / f"{seg['id']}_pad.mp3"
        result = run(
            [
                "ffmpeg",
                "-y",
                "-i",
                raw_path,
                "-af",
                f"apad=pad_dur={target_dur},atrim=0:{target_dur}",
                "-c:a",
                "libmp3lame",
                "-q:a",
                "4",
                padded_path,
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(f"Audio padding failed: {result.stderr}\n{result.stdout}")
        seg["duration"] = ffprobe_duration(padded_path)
        seg["audio"] = str(padded_path)
        print(f"    {seg['id']}: {raw_dur:.3f}s -> {seg['duration']:.3f}s")
    return SEGMENTS


def write_config(segments: list[dict[str, Any]]) -> None:
    config = {
        "background_color": "#0A0A0A",
        "voice": VOICE,
        "segments": [{"type": seg["type"], "duration": seg["duration"]} for seg in segments],
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def split_caption(text: str, max_chars: int = 24) -> list[str]:
    """Split narration into readable subtitle phrases at natural boundaries."""
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


def format_ass_time(seconds: float) -> str:
    cs = int(round(seconds * 100))
    s = cs // 100
    cs -= s * 100
    m = s // 60
    s -= m * 60
    h = m // 60
    m -= h * 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_ass(segments: list[dict[str, Any]]) -> None:
    entries = []
    cursor = 0.0
    for seg in segments:
        seg_dur = seg["duration"]
        # Subtitle timing follows the actual voice, not the padded animation hold.
        voice_dur = seg.get("raw_duration", seg_dur)
        text = seg["narration"]
        phrases = split_caption(text)

        word_count = len(text.split())
        for phrase in phrases:
            phrase_words = len(phrase.split())
            phrase_dur = voice_dur * (phrase_words / max(word_count, 1))
            start = cursor
            end = cursor + phrase_dur
            clean = phrase.replace("\n", "\\N")
            entries.append((format_ass_time(start), format_ass_time(end), clean))
            cursor += phrase_dur
        # Advance cursor to the start of the next segment (padded boundary).
        cursor += seg_dur - voice_dur

    ass_lines = [
        "[Script Info]",
        "Title: Matrix AI Vietnamese Shorts",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV,Encoding",
        "Style: Default,Arial,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,50,50,140,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for start, end, text in entries:
        ass_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    ASS_FILE.write_text("\n".join(ass_lines), encoding="utf-8")


def concatenate_audio(segments: list[dict[str, Any]]) -> Path:
    concat_txt = AUDIO_DIR / "concat.txt"
    concat_txt.write_text(
        "\n".join(f"file '{Path(seg['audio']).resolve()}'" for seg in segments),
        encoding="utf-8",
    )
    full_mp3 = AUDIO_DIR / "narration_full.mp3"
    result = run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", full_mp3]
    )
    if result.returncode != 0:
        raise RuntimeError(f"Audio concat failed: {result.stderr}")
    return full_mp3


def make_music_bed(target_duration: float) -> Path:
    bed_path = AUDIO_DIR / "music_bed.mp3"
    music_dur = ffprobe_duration(BG_MUSIC)

    if music_dur <= 0:
        raise RuntimeError("Background music file is empty or unreadable")

    # If the music is already long enough, just trim and fade out.
    if music_dur >= target_duration:
        result = run(
            [
                "ffmpeg",
                "-y",
                "-i",
                BG_MUSIC,
                "-af",
                f"afade=t=in:ss=0:d=0.5,afade=t=out:st={target_duration - 3}:d=3,atrim=0:{target_duration}",
                "-c:a",
                "libmp3lame",
                "-q:a",
                "4",
                bed_path,
            ]
        )
    else:
        # Loop with crossfade. Trim the last few seconds of each copy to avoid
        # re-introducing the original fade-out at every loop point.
        crossfade_dur = 8
        fadeout_trim = 4
        body_dur = max(music_dur - fadeout_trim, crossfade_dur + 2)

        # Number of copies so that the crossfaded output is at least target_duration.
        n_copies = max(2, int((target_duration - body_dur) / (body_dur - crossfade_dur)) + 2)

        inputs = []
        for i in range(n_copies):
            inputs.extend(["-i", BG_MUSIC])

        trim_filters = []
        cross_inputs = []
        for i in range(n_copies):
            trim_filters.append(f"[{i}:a]atrim=0:{body_dur}[a{i}]")
            cross_inputs.append(f"[a{i}]")

        fade_start = max(0.0, target_duration - 3.0)
        filter_complex = (
            ";".join(trim_filters)
            + ";"
            + "".join(cross_inputs)
            + f"acrossfade=n={n_copies}:d={crossfade_dur}[loop];"
            + f"[loop]atrim=0:{target_duration},afade=t=in:ss=0:d=0.5,afade=t=out:st={fade_start}:d=3[out]"
        )

        result = run(
            [
                "ffmpeg",
                "-y",
                *inputs,
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                "-c:a",
                "libmp3lame",
                "-q:a",
                "4",
                bed_path,
            ]
        )

    if result.returncode != 0:
        raise RuntimeError(f"Music bed creation failed: {result.stderr}\n{result.stdout}")
    return bed_path


def render_manim() -> Path:
    print("Rendering Manim 3D scene...")
    result = run(
        [
            str(MANIM),
            "-q",
            "l",
            "--disable_caching",
            "-o",
            "MatrixAIVietnamese",
            str(SCENE_FILE),
            "MatrixAIVietnamese",
        ],
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr}\n{result.stdout}")
    out = PROJECT / "media" / "videos" / "matrix_ai_vi" / "1920p30" / "MatrixAIVietnamese.mp4"
    if not out.exists():
        matches = list((PROJECT / "media" / "videos" / "matrix_ai_vi").rglob("MatrixAIVietnamese.mp4"))
        if matches:
            out = matches[0]
        else:
            raise RuntimeError("Manim did not produce MatrixAIVietnamese.mp4")
    return out


def assemble_final(video: Path, audio: Path, music: Path) -> Path:
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
            "[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.14'[aout]",
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
        raise RuntimeError(f"Final assembly failed: {result.stderr}\n{result.stdout}")
    return FINAL_MP4


def polish_video(input_path: Path, output_path: Path) -> Path:
    """Post-process the final MP4 for a more cinematic look."""
    print("\n7/6 Polishing final video (color, sharpen, vignette)...")
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
            "18",
            "-preset",
            "medium",
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


def main() -> None:
    print("=" * 60)
    print("Building 'Ma trận là trái tim của AI' — Vietnamese 3D Shorts")
    print("=" * 60)

    print("\n1/6 Generating narration with edge-tts...")
    segments = generate_audio()

    print("\n2/6 Writing config.json for Manim...")
    write_config(segments)

    print("\n3/6 Generating Vietnamese subtitles...")
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

    print("\n7/6 Polishing final video...")
    polished = polish_video(final, POLISHED_MP4)
    print(f"    -> {polished}")

    dur = ffprobe_duration(final)
    print(f"\nDone. Final duration: {dur:.2f}s")
    print(f"Polished output: {polished}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        segs = generate_audio()
        write_config(segs)
        generate_ass(segs)
        print(f"\nAudio+config prepared. Total narration: {sum(s['duration'] for s in segs):.2f}s")
    else:
        main()
