"""AumSum-style CPU demo v2 using free AI image generation (Pollinations).

This version generates backgrounds and a character with Pollinations, removes the
character background with rembg, and composites everything with narration using
MoviePy.  It is still CPU-driven and does not train models, but the visual quality
is much closer to a professional 2D cartoon than the vector-only v1.
"""

from __future__ import annotations

import asyncio
import math
import os
import re
import time
import urllib.parse
from io import BytesIO
from pathlib import Path

import edge_tts
import numpy as np
import requests
import yaml
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFilter, ImageFont


RESOLUTION = (1280, 720)
FPS = 30
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
VOICE = "en-US-AriaNeural"
POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
SEED = 2026


def safe_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.Font:
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


def fetch_image(prompt: str, out_path: Path, width: int = 1280, height: int = 720) -> None:
    if out_path.exists():
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"{POLLINATIONS_BASE}/{urllib.parse.quote(prompt)}?width={width}&height={height}&nologo=true&seed={SEED}"
    print(f"  Generating image: {out_path.name} ...")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")
    # Pollinations may return a slightly different size; force target aspect and resize
    img = img.resize(RESOLUTION, Image.LANCZOS)
    img.save(out_path, "PNG")


def remove_background(input_path: Path, output_path: Path) -> None:
    if output_path.exists():
        return
    print(f"  Removing background: {output_path.name} ...")
    from rembg import remove
    img = Image.open(input_path)
    out = remove(img)
    out = out.resize((512, 512), Image.LANCZOS)
    out.save(output_path, "PNG")


def generate_assets(assets_dir: Path) -> None:
    print("[Assets] Generating AI images via Pollinations...")

    character_prompt = (
        "AumSum style cute turquoise cartoon mascot character, big friendly eyes, "
        "wide smile, short dark hair, 2D flat vector educational illustration, "
        "full body, neutral standing pose, white background, high quality, no text"
    )
    character_raw = assets_dir / "character_raw.png"
    character_png = assets_dir / "character.png"
    fetch_image(character_prompt, character_raw, width=1024, height=1024)
    remove_background(character_raw, character_png)

    background_prompts = {
        "bg_hook.png": (
            "AumSum style 2D cartoon educational scene, bright sunny ocean with crystal "
            "clear transparent water, fish and coral visible underwater, blue sky with clouds, "
            "no character, no mascot, no text, high quality"
        ),
        "bg_submarine.png": (
            "AumSum style 2D cartoon educational scene, deep blue ocean with a grey submarine, "
            "light rays, bubbles, coral reef, no character, no mascot, no text, high quality"
        ),
        "bg_fish.png": (
            "AumSum style 2D cartoon educational scene, underwater with colorful tropical fish, "
            "bubbles, light rays, coral, no character, no mascot, no text, high quality"
        ),
        "bg_coral.png": (
            "AumSum style 2D cartoon educational scene, underwater coral reef with a treasure chest, "
            "light rays, bubbles, no character, no mascot, no text, high quality"
        ),
        "bg_outro.png": (
            "AumSum style 2D cartoon educational scene, sunny beach with palm trees, "
            "turquoise ocean, bright sky, no character, no mascot, no text, high quality"
        ),
    }
    for filename, prompt in background_prompts.items():
        fetch_image(prompt, assets_dir / filename, width=1280, height=720)


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
    # Shadow/glow
    for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((x + dx, y + dy), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def build_scene_image(
    background_path: Path,
    title: str,
    caption: str,
    output_path: Path,
) -> None:
    if output_path.exists():
        return
    img = Image.open(background_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    title_font = safe_font(44)
    caption_font = safe_font(30)

    # Title at top with highlighted keyword
    # Highlight the first noun-ish word if possible; here highlight the first word
    words = title.split()
    if words:
        # Simple heuristic: highlight the first word
        first = words[0]
        rest = " " + " ".join(words[1:]) if len(words) > 1 else ""
        bbox = draw.textbbox((0, 0), first, font=title_font)
        fw = bbox[2] - bbox[0]
        bbox2 = draw.textbbox((0, 0), rest, font=title_font)
        rw = bbox2[2] - bbox2[0]
        total_w = fw + rw
        start_x = (RESOLUTION[0] - total_w) // 2
        y = 40
        # shadow
        draw.text((start_x + 2, y + 2), first, font=title_font, fill=(0, 0, 0))
        draw.text((start_x, y), first, font=title_font, fill=(255, 220, 80))
        if rest:
            draw.text((start_x + 2 + rw, y + 2), rest, font=title_font, fill=(0, 0, 0))
            draw.text((start_x + fw, y), rest, font=title_font, fill=(255, 255, 255))
    else:
        draw_text_with_shadow(draw, title, title_font, RESOLUTION[0] // 2, 50)

    # Caption box at bottom
    if caption:
        box_pad = 20
        bbox = draw.textbbox((0, 0), caption, font=caption_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        box_w = min(tw + box_pad * 2, RESOLUTION[0] - 80)
        box_h = th + box_pad * 2
        box_x = (RESOLUTION[0] - box_w) // 2
        box_y = RESOLUTION[1] - box_h - 30
        overlay = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=20,
            fill=(0, 0, 0, 160),
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw_text_with_shadow(draw, caption, caption_font, RESOLUTION[0] // 2, box_y + box_h // 2)

    img.save(output_path, "PNG")


def render_scene(
    scene_idx: int,
    scene_text: str,
    audio_path: str,
    scene_image_path: Path,
    character_path: Path,
    output_dir: Path,
    positions: dict,
) -> str:
    duration = audio_duration(audio_path)

    base_clip = ImageClip(str(scene_image_path), duration=duration)

    char_img = Image.open(character_path).convert("RGBA")
    # Base size for character
    target_h = int(RESOLUTION[1] * positions.get("scale", 0.5))
    char_w = int(char_img.width * target_h / char_img.height)
    char_h = target_h
    char_clip = ImageClip(np.array(char_img.resize((char_w, char_h), Image.LANCZOS)), duration=duration)

    base_x = positions.get("x", RESOLUTION[0] // 2 - char_w // 2)
    base_y = positions.get("y", RESOLUTION[1] - char_h - 30)
    bounce_amp = positions.get("bounce", 8)
    breath = positions.get("breath", 0.03)

    def get_pos(t: float) -> tuple[float, float]:
        x = base_x
        y = base_y + bounce_amp * math.sin(t * 5)
        return x, y

    # MoviePy resized needs the clip to be VideoClip; ImageClip is fine.
    char_clip = char_clip.resized(lambda t: (char_w * (1 + breath * math.sin(t * 3)), char_h * (1 + breath * math.sin(t * 3))))
    char_clip = char_clip.with_position(get_pos)

    audio = AudioFileClip(audio_path)
    composite = CompositeVideoClip([base_clip, char_clip], size=RESOLUTION)
    composite = composite.with_audio(audio).with_fps(FPS)

    out_path = output_dir / f"scene_v2_{scene_idx:03d}.mp4"
    composite.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )
    composite.close()
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


SCENE_POSITIONS = [
    {"x": 500, "y": 280, "scale": 0.55, "bounce": 10, "breath": 0.02},
    {"x": 100, "y": 300, "scale": 0.45, "bounce": 6, "breath": 0.02},
    {"x": 480, "y": 300, "scale": 0.48, "bounce": 8, "breath": 0.02},
    {"x": 120, "y": 320, "scale": 0.45, "bounce": 6, "breath": 0.02},
    {"x": 500, "y": 260, "scale": 0.55, "bounce": 10, "breath": 0.02},
]


def build_scene_images(assets_dir: Path, scenes: list[dict]) -> list[Path]:
    bg_files = ["bg_hook.png", "bg_submarine.png", "bg_fish.png", "bg_coral.png", "bg_outro.png"]
    scene_images: list[Path] = []
    for i, scene in enumerate(scenes):
        bg = assets_dir / bg_files[min(i, len(bg_files) - 1)]
        out = assets_dir / f"scene_{i:03d}_composite.png"
        build_scene_image(bg, scene["text"], scene["text"], out)
        scene_images.append(out)
    return scene_images


async def main_async(project_dir_str: str = "examples/aumsum-transparent-ocean") -> None:
    project_dir = Path(project_dir_str)
    assets_dir = project_dir / "assets"
    output_dir = project_dir / "output"
    audio_dir = project_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    project = load_project(str(project_dir / "project.yaml"))
    scenes = parse_script(str(project_dir / "script.md"))

    print("[1/4] Generating assets (character + backgrounds) ...")
    generate_assets(assets_dir)

    print("[2/4] Building scene images ...")
    scene_images = build_scene_images(assets_dir, scenes)

    print("[3/4] Rendering scenes with narration ...")
    clip_paths: list[str] = []
    for i, scene in enumerate(scenes):
        audio_path = audio_dir / f"scene_v2_{i:03d}.mp3"
        if not audio_path.exists():
            print(f"  Generating audio for scene {i + 1}...")
            await generate_audio(scene["text"], str(audio_path))
        print(f"  Rendering scene {i + 1}...")
        pos = SCENE_POSITIONS[min(i, len(SCENE_POSITIONS) - 1)]
        clip_path = render_scene(
            i, scene["text"], str(audio_path), scene_images[i],
            assets_dir / "character.png", output_dir, pos,
        )
        clip_paths.append(clip_path)

    final_path = output_dir / "final_aumsum_v2.mp4"
    print("[4/4] Assembling final video...")
    assemble(clip_paths, final_path)
    print(f"Done: {final_path.resolve()}")


if __name__ == "__main__":
    import sys
    project_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "examples/aumsum-transparent-ocean"
    asyncio.run(main_async(project_dir_arg))
