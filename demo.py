"""CPU-only demo of the AI Video Studio pipeline.

This script uses online Microsoft Edge TTS for narration and Pillow/MoviePy
to generate slides, producing a real MP4 on a machine without a GPU.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFont

import edge_tts


@dataclass
class Segment:
    text: str
    duration: float = 5.0
    slide_text: str = ""
    audio_path: str = ""
    video_path: str = ""


SCRIPT = [
    Segment(
        text="Welcome to the AI Video Studio. Today we build videos locally with AI.",
        duration=5.0,
        slide_text="AI Video Studio\nLocal. Open. Agentic.",
    ),
    Segment(
        text="First, an idea becomes a script through a local language model.",
        duration=5.0,
        slide_text="Step 1\nIdea to Script",
    ),
    Segment(
        text="Then, image and video models generate visuals for every scene.",
        duration=5.0,
        slide_text="Step 2\nGenerate Visuals",
    ),
    Segment(
        text="Finally, voice, music and subtitles are mixed into the final render.",
        duration=5.0,
        slide_text="Step 3\nRender & Deliver",
    ),
]


VOICE = "en-GB-SoniaNeural"
OUTPUT_DIR = Path("projects/demo_output")


def create_slide(text: str, width: int = 1280, height: int = 720) -> Image.Image:
    """Render a simple gradient text slide."""
    img = Image.new("RGB", (width, height), color=(20, 20, 40))
    draw = ImageDraw.Draw(img)

    # Simple vertical gradient
    for y in range(height):
        r = int(20 + (y / height) * 40)
        g = int(20 + (y / height) * 30)
        b = int(40 + (y / height) * 60)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_sub = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = font_title

    lines = text.split("\n")
    title = lines[0]
    subtitle = "\n".join(lines[1:]) if len(lines) > 1 else ""

    # Draw title centered
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((width - tw) // 2, height // 2 - th - 20),
        title,
        fill=(255, 255, 255),
        font=font_title,
    )

    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((width - tw) // 2, height // 2 + 40),
            subtitle,
            fill=(200, 220, 255),
            font=font_sub,
        )

    return img


async def generate_audio(segment: Segment, index: int, output_dir: Path) -> str:
    """Generate narration audio with Edge TTS."""
    path = output_dir / f"audio_{index:03d}.mp3"
    communicate = edge_tts.Communicate(segment.text, VOICE)
    await communicate.save(str(path))
    return str(path)


def render_segment(segment: Segment, index: int, output_dir: Path) -> str:
    """Render one video clip: slide + audio + subtitle text overlay."""
    slide_img = create_slide(segment.slide_text or segment.text)
    slide_path = output_dir / f"slide_{index:03d}.png"
    slide_img.save(slide_path)

    audio = AudioFileClip(segment.audio_path)
    duration = audio.duration or segment.duration

    # Slide with subtle zoom/pan effect (static for CPU demo)
    img_clip = ImageClip(str(slide_path), duration=duration)

    # Subtitle overlay at bottom
    txt_clip = (
        TextClip(
            text=segment.text,
            font="C:\\Windows\\Fonts\\arial.ttf",
            font_size=28,
            color="white",
            bg_color="black",
            size=(1200, None),
            method="caption",
            text_align="center",
            horizontal_align="center",
            vertical_align="bottom",
            duration=duration,
        )
        .with_position(("center", "bottom"))
    )

    clip = CompositeVideoClip([img_clip, txt_clip], size=(1280, 720))
    clip = clip.with_audio(audio)

    out_path = output_dir / f"clip_{index:03d}.mp4"
    clip.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )
    return str(out_path)


def assemble_final(clips: list[str], output: Path) -> Path:
    """Concatenate rendered clips into the final video."""
    loaded = [VideoFileClip(p) for p in clips]
    final = concatenate_videoclips(loaded, method="compose")
    final.write_videofile(
        str(output),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )
    for c in loaded:
        c.close()
    return output


async def main_async() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating audio for", len(SCRIPT), "segments...")
    for i, seg in enumerate(SCRIPT):
        seg.audio_path = await generate_audio(seg, i, OUTPUT_DIR)

    print("Rendering video clips...")
    clip_paths = []
    for i, seg in enumerate(SCRIPT):
        path = render_segment(seg, i, OUTPUT_DIR)
        clip_paths.append(path)
        print(f"  clip {i + 1}/{len(SCRIPT)}: {path}")

    final_path = OUTPUT_DIR / "final_demo.mp4"
    print("Assembling final video:", final_path)
    assemble_final(clip_paths, final_path)
    print("Done:", final_path.resolve())


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
