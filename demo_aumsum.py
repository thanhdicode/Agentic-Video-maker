"""AumSum-style CPU demo for the AI Video Studio.

This script reads a project YAML + script, generates narration with Edge TTS,
and renders a 2D cartoon scene per segment using Pillow/MoviePy. It is a
prototype to show the end-to-end agent pipeline on a CPU-only machine.
"""

from __future__ import annotations

import asyncio
import math
import os
import re
from pathlib import Path

import edge_tts
import numpy as np
import yaml
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont


RESOLUTION = (1280, 720)
FPS = 30
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
VOICE = "en-US-AriaNeural"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.Font:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def parse_script(script_path: str) -> list[dict]:
    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read()
    scenes = []
    pattern = re.compile(r"## Scene \d+:\s*(.*?)\n(.*?)(?=\n## Scene|\Z)", re.S)
    for m in pattern.finditer(text):
        title = m.group(1).strip()
        body = m.group(2).strip()
        scenes.append({"title": title, "text": body})
    return scenes


def load_project(project_path: str) -> dict:
    with open(project_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def generate_audio(text: str, out_path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(out_path)


def audio_duration(path: str) -> float:
    with AudioFileClip(path) as clip:
        return float(clip.duration)


def draw_rounded_rect(
    draw: ImageDraw.Draw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    width: int = 0,
) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)


def draw_character(
    draw: ImageDraw.Draw,
    cx: int,
    cy: int,
    scale: float,
    pose: str,
    t: float,
) -> None:
    """Draw a simple AumSum-inspired character."""
    s = scale
    # Body (turquoise blob)
    body_w, body_h = int(90 * s), int(110 * s)
    body_color = (0, 188, 212)
    draw.ellipse(
        [cx - body_w // 2, cy - body_h // 2, cx + body_w // 2, cy + body_h // 2],
        fill=body_color,
        outline=(0, 120, 140),
        width=3,
    )

    # Head
    head_r = int(50 * s)
    head_y = cy - int(85 * s)
    draw.ellipse(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        fill=(255, 230, 200),
        outline=(0, 0, 0),
        width=3,
    )

    # Hair
    hair_points = [
        (cx - int(30 * s), head_y - head_r + int(10 * s)),
        (cx, head_y - head_r - int(25 * s)),
        (cx + int(30 * s), head_y - head_r + int(10 * s)),
    ]
    draw.line(hair_points, fill=(0, 0, 0), width=int(6 * s), joint="curve")

    # Eyes
    eye_y = head_y - int(10 * s)
    eye_offset = int(18 * s)
    eye_r = int(8 * s)
    # Blink every ~2.5s
    if (t % 2.5) < 0.15:
        for dx in (-eye_offset, eye_offset):
            draw.line(
                [(cx + dx - eye_r, eye_y), (cx + dx + eye_r, eye_y)],
                fill=(0, 0, 0),
                width=int(3 * s),
            )
    else:
        for dx in (-eye_offset, eye_offset):
            draw.ellipse(
                [cx + dx - eye_r, eye_y - eye_r, cx + dx + eye_r, eye_y + eye_r],
                fill=(255, 255, 255),
                outline=(0, 0, 0),
                width=2,
            )
            draw.ellipse(
                [cx + dx - eye_r // 3, eye_y - eye_r // 3, cx + dx + eye_r // 3, eye_y + eye_r // 3],
                fill=(0, 0, 0),
            )

    # Mouth (talk animation)
    mouth_y = head_y + int(20 * s)
    talk_open = (math.sin(t * 15) > 0) and (t % 1.0 < 0.8)
    if talk_open:
        draw.ellipse(
            [cx - int(10 * s), mouth_y - int(8 * s), cx + int(10 * s), mouth_y + int(8 * s)],
            fill=(120, 30, 30),
        )
    else:
        draw.arc(
            [cx - int(15 * s), mouth_y - int(12 * s), cx + int(15 * s), mouth_y + int(12 * s)],
            start=0,
            end=180,
            fill=(120, 30, 30),
            width=int(4 * s),
        )

    # Arms
    arm_y = cy - int(20 * s)
    arm_len = int(50 * s)
    if pose == "wave":
        left_angle = math.sin(t * 6) * 0.5 - 0.3
        right_angle = 0.3
    elif pose == "point_right":
        left_angle = -0.2
        right_angle = -0.8
    elif pose == "think":
        left_angle = 0.6
        right_angle = -0.6
    else:
        left_angle = 0.2
        right_angle = -0.2

    def draw_arm(angle: float, side: int) -> None:
        end_x = cx + side * (int(45 * s) + int(arm_len * math.cos(angle) * side))
        end_y = arm_y + int(arm_len * math.sin(angle))
        draw.line([(cx + side * int(35 * s), arm_y), (end_x, end_y)], fill=(0, 0, 0), width=int(6 * s))
        # Hand
        draw.ellipse([end_x - 8, end_y - 8, end_x + 8, end_y + 8], fill=(255, 230, 200), outline=(0, 0, 0), width=2)

    draw_arm(left_angle, -1)
    draw_arm(right_angle, 1)

    # Legs
    leg_y = cy + int(45 * s)
    leg_len = int(45 * s)
    for side in (-1, 1):
        end_x = cx + side * int(25 * s)
        end_y = leg_y + leg_len
        draw.line([(cx + side * int(15 * s), leg_y), (end_x, end_y)], fill=(0, 0, 0), width=int(6 * s))
        draw.ellipse([end_x - 10, end_y - 5, end_x + 10, end_y + 10], fill=(0, 0, 0))


def draw_background(draw: ImageDraw.Draw, scene_type: str, width: int, height: int, t: float) -> None:
    if scene_type == "ocean_surface":
        for y in range(height):
            ratio = y / height
            r = int(135 + ratio * 60)
            g = int(206 + ratio * 20)
            b = int(235 + ratio * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        # Sun
        draw.ellipse([width - 140, 40, width - 40, 140], fill=(255, 220, 80), outline=(255, 180, 0), width=3)
        # Clouds
        for cx, cy in [(180, 90), (450, 70), (900, 100)]:
            draw.ellipse([cx - 50, cy - 20, cx + 50, cy + 20], fill=(255, 255, 255))
            draw.ellipse([cx - 25, cy - 35, cx + 25, cy + 5], fill=(255, 255, 255))
    elif scene_type == "ocean_deep":
        for y in range(height):
            ratio = y / height
            r = int(20 + ratio * 40)
            g = int(60 + ratio * 50)
            b = int(120 + ratio * 80)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        # Bubbles
        for i in range(8):
            bx = int((i * 150 + t * 50) % width)
            by = height - int((i * 70 + t * 80) % height)
            draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(255, 255, 255, 100), outline=(255, 255, 255))
    elif scene_type == "sky":
        for y in range(height):
            ratio = y / height
            r = int(135 - ratio * 40)
            g = int(206 - ratio * 30)
            b = int(235 - ratio * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        draw.ellipse([width - 140, 40, width - 40, 140], fill=(255, 220, 80), outline=(255, 180, 0), width=3)


def draw_submarine(draw: ImageDraw.Draw, x: int, y: int, t: float) -> None:
    body_color = (80, 80, 80)
    draw.ellipse([x - 100, y - 40, x + 100, y + 40], fill=body_color, outline=(40, 40, 40), width=3)
    draw.rectangle([x - 30, y - 70, x + 10, y - 40], fill=body_color, outline=(40, 40, 40), width=3)
    draw.ellipse([x - 120, y - 50, x - 80, y - 10], fill=(200, 200, 200), outline=(40, 40, 40), width=2)
    # Periscope
    periscope_h = int(20 + 10 * math.sin(t * 2))
    draw.rectangle([x + 50, y - 60 - periscope_h, x + 70, y - 60], fill=body_color)
    draw.ellipse([x + 45, y - 65 - periscope_h, x + 75, y - 55 - periscope_h], fill=body_color)


def draw_fish(draw: ImageDraw.Draw, x: int, y: int, color: tuple[int, int, int], t: float) -> None:
    body_w = 40
    offset = int(10 * math.sin(t * 5))
    draw.ellipse([x - body_w, y - 20 + offset, x + body_w, y + 20 + offset], fill=color, outline=(0, 0, 0), width=2)
    # Tail
    tail_x = x - body_w - 15
    draw.polygon([(tail_x, y + offset), (tail_x - 20, y - 15 + offset), (tail_x - 20, y + 15 + offset)], fill=color, outline=(0, 0, 0))


def draw_coral_treasure(draw: ImageDraw.Draw, x: int, y: int, t: float) -> None:
    # Coral
    for i, color in enumerate([(255, 100, 100), (255, 150, 80), (255, 80, 150)]):
        cx = x + (i - 1) * 60
        h = int(80 + 20 * math.sin(t * 2 + i))
        draw.ellipse([cx - 15, y - h, cx + 15, y + 10], fill=color, outline=(150, 50, 50), width=2)
    # Treasure chest
    draw.rounded_rectangle([x + 80, y - 30, x + 150, y + 10], radius=5, fill=(139, 90, 43), outline=(80, 50, 20), width=2)
    draw.arc([x + 80, y - 60, x + 150, y], start=0, end=180, fill=(139, 90, 43), width=20)


def draw_text_with_shadow(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    cx: int,
    cy: int,
    fill: tuple[int, int, int] = (255, 255, 255),
    shadow: tuple[int, int, int] = (0, 0, 0),
    align: str = "center",
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if align == "center":
        x = cx - tw // 2
    elif align == "left":
        x = cx
    else:
        x = cx - tw
    y = cy - th // 2
    draw.text((x + 2, y + 2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def make_scene_frame(
    scene_idx: int,
    scene_text: str,
    scene_type: str,
    pose: str,
    props: list[str],
) -> callable:
    title_font = load_font(48)
    text_font = load_font(32)

    def make_frame(t: float) -> np.ndarray:
        img = Image.new("RGB", RESOLUTION, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        width, height = RESOLUTION

        draw_background(draw, scene_type, width, height, t)

        # Props
        if "submarine" in props:
            draw_submarine(draw, width - 250, height // 2 + 50, t)
        if "fish" in props:
            draw_fish(draw, width - 200, height // 2 + 80, (255, 200, 50), t + 0)
            draw_fish(draw, width - 300, height // 2 + 120, (255, 120, 120), t + 1)
        if "coral" in props:
            draw_coral_treasure(draw, width // 2 + 150, height - 80, t)

        # Character bounce
        bounce = int(15 * abs(math.sin(t * 4)))
        char_x = width // 2 - 250 if "submarine" in props else width // 2
        char_y = height // 2 + 80 - bounce
        draw_character(draw, char_x, char_y, 1.0, pose, t)

        # Title card at top
        draw_text_with_shadow(draw, scene_text, title_font, width // 2, 60, fill=(255, 255, 255))

        # Caption box at bottom
        caption_font = load_font(28)
        caption = scene_text
        bbox = draw.textbbox((0, 0), caption, font=caption_font)
        tw = bbox[2] - bbox[0]
        box_w = min(tw + 60, width - 80)
        box_h = 80
        box_x = (width - box_w) // 2
        box_y = height - box_h - 30
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=20, fill=(0, 0, 0, 160))
        draw_text_with_shadow(draw, caption, caption_font, width // 2, box_y + box_h // 2)

        return np.array(img)

    return make_frame


SCENE_CONFIG = [
    {"type": "ocean_surface", "pose": "wave", "props": [], "text": "What if our oceans were completely transparent?"},
    {"type": "ocean_deep", "pose": "think", "props": ["submarine"], "text": "Submarines would lose their biggest advantage: stealth."},
    {"type": "ocean_deep", "pose": "point_right", "props": ["fish"], "text": "Sea animals using camouflage would be super easy to spot."},
    {"type": "ocean_deep", "pose": "wave", "props": ["coral"], "text": "Underwater archaeology would be easier, but coral might suffer."},
    {"type": "sky", "pose": "wave", "props": [], "text": "Don't worry, oceans are beautiful just the way they are!"},
]


def render_scene(
    scene_idx: int,
    scene_text: str,
    audio_path: str,
    output_dir: Path,
) -> str:
    cfg = SCENE_CONFIG[min(scene_idx, len(SCENE_CONFIG) - 1)]
    duration = audio_duration(audio_path)

    make_frame = make_scene_frame(scene_idx, cfg["text"], cfg["type"], cfg["pose"], cfg["props"])
    video = VideoClip(make_frame, duration=duration)
    audio = AudioFileClip(audio_path)
    video = video.with_audio(audio).with_fps(FPS)

    out_path = output_dir / f"scene_{scene_idx:03d}.mp4"
    video.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )
    video.close()
    audio.close()
    return str(out_path)


def assemble(clips: list[str], output: Path) -> Path:
    from moviepy import VideoFileClip
    loaded = [VideoFileClip(p) for p in clips]
    final = concatenate_videoclips(loaded, method="compose")
    final.write_videofile(
        str(output),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )
    for c in loaded:
        c.close()
    return output


async def main_async() -> None:
    project_dir = Path("projects/aumsum-transparent-ocean")
    output_dir = project_dir / "output"
    audio_dir = project_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    project = load_project(str(project_dir / "project.yaml"))
    scenes = parse_script(str(project_dir / "script.md"))

    print(f"Rendering {len(scenes)} scenes...")
    clip_paths: list[str] = []
    for i, scene in enumerate(scenes):
        audio_path = audio_dir / f"scene_{i:03d}.mp3"
        if not audio_path.exists():
            print(f"  Generating audio for scene {i + 1}: {scene['text'][:50]}...")
            await generate_audio(scene["text"], str(audio_path))
        print(f"  Rendering scene {i + 1}...")
        clip_path = render_scene(i, scene["text"], str(audio_path), output_dir)
        clip_paths.append(clip_path)

    final_path = output_dir / "final_aumsum.mp4"
    print(f"Assembling final video: {final_path}")
    assemble(clip_paths, final_path)
    print(f"Done: {final_path.resolve()}")


if __name__ == "__main__":
    asyncio.run(main_async())
