"""AumSum-style CPU demo v2 using free AI image generation (Pollinations).

This version generates a character and per-scene backgrounds with Pollinations,
removes the character background with rembg, and composites everything with
narration using MoviePy.  It is CPU-driven and does not train models, but the
visual quality is much closer to a professional 2D cartoon than the vector-only
v1.  The script now supports an arbitrary number of scenes.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
import textwrap
import urllib.parse
from io import BytesIO
from pathlib import Path

import edge_tts
import numpy as np
import requests
import yaml
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont


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
    print("[Assets] Generating mascot character via Pollinations...")
    character_prompt = (
        "AumSum style cute turquoise cartoon mascot character, big friendly eyes, "
        "wide smile, short dark hair, 2D flat vector educational illustration, "
        "full body, neutral standing pose, white background, high quality, no text"
    )
    character_raw = assets_dir / "character_raw.png"
    character_png = assets_dir / "character.png"
    fetch_image(character_prompt, character_raw, width=1024, height=1024)
    remove_background(character_raw, character_png)


def scene_to_background_prompt(scene: dict, theme: str) -> str:
    """Build a Pollinations prompt from the scene text + a project theme."""
    title = scene["title"].lower()
    text = scene["text"].lower()
    # Pull a few content keywords for the background
    keywords = []
    if any(w in title or w in text for w in ("space", "moon", "planet", "sun", "orbit")):
        keywords.append("outer space with stars and planets")
    if any(w in title or w in text for w in ("ocean", "water", "sea", "river", "lake")):
        keywords.append("underwater ocean scene")
    if any(w in title or w in text for w in ("float", "floating", "fly", "flying")):
        keywords.append("objects floating in zero gravity")
    if any(w in title or w in text for w in ("fire", "flame", "burn")):
        keywords.append("floating round flames")
    if any(w in title or w in text for w in ("build", "house", "write")):
        keywords.append("construction site with floating tools")
    if any(w in title or w in text for w in ("atmosphere", "air", "breathe")):
        keywords.append("sky with clouds and wind")
    if not keywords:
        keywords.append(theme)

    setting = ", ".join(keywords[:2])
    prompt = (
        f"AumSum style 2D cartoon educational scene, {setting}, "
        "bright colors, flat vector illustration, no character, no mascot, no text, high quality"
    )
    return prompt


def scene_to_position(i: int, total: int, char_w: int, char_h: int) -> dict:
    """Return character placement/animation parameters for scene index i."""
    layouts = [
        {"x_rel": 0.18, "scale": 0.45},
        {"x_rel": 0.78, "scale": 0.45},
        {"x_rel": 0.50, "scale": 0.55},
        {"x_rel": 0.28, "scale": 0.42},
        {"x_rel": 0.72, "scale": 0.42},
    ]
    layout = layouts[i % len(layouts)]
    scale = layout["scale"]
    x = int(RESOLUTION[0] * layout["x_rel"] - char_w * scale / 2)
    y = int(RESOLUTION[1] - char_h * scale - 60)
    return {
        "x": x,
        "y": y,
        "scale": scale,
        "bounce": 6 + (i % 3) * 2,
        "breath": 0.02,
    }


def draw_text_with_shadow(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    cx: int,
    cy: int,
    fill: tuple[int, int, int] = (255, 255, 255),
    shadow: tuple[int, int, int] = (0, 0, 0),
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = cx - tw // 2
    y = cy - th // 2
    for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((x + dx, y + dy), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def draw_wrapped_text(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    cx: int,
    top_y: int,
    max_width: int,
    line_height: int,
    fill: tuple[int, int, int] = (255, 255, 255),
    shadow: tuple[int, int, int] = (0, 0, 0),
) -> None:
    """Draw wrapped text centered horizontally, starting at top_y."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = cx - tw // 2
        y = top_y
        for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            draw.text((x + dx, y + dy), line, font=font, fill=shadow)
        draw.text((x, y), line, font=font, fill=fill)
        top_y += line_height


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

    # Title at top: highlight first word
    words = title.split()
    if words:
        first = words[0]
        rest = " " + " ".join(words[1:]) if len(words) > 1 else ""
        bbox = draw.textbbox((0, 0), first, font=title_font)
        fw = bbox[2] - bbox[0]
        bbox2 = draw.textbbox((0, 0), rest, font=title_font)
        rw = bbox2[2] - bbox2[0]
        total_w = fw + rw
        start_x = (RESOLUTION[0] - total_w) // 2
        y = 40
        draw.text((start_x + 2, y + 2), first, font=title_font, fill=(0, 0, 0))
        draw.text((start_x, y), first, font=title_font, fill=(255, 220, 80))
        if rest:
            draw.text((start_x + 2 + rw, y + 2), rest, font=title_font, fill=(0, 0, 0))
            draw.text((start_x + fw, y), rest, font=title_font, fill=(255, 255, 255))
    else:
        draw_text_with_shadow(draw, title, title_font, RESOLUTION[0] // 2, 50)

    # Caption box at bottom, wrapped
    if caption:
        box_pad = 18
        max_box_w = RESOLUTION[0] - 120
        wrapped = textwrap.fill(caption, width=50)
        line_count = wrapped.count("\n") + 1
        line_h = 36
        box_h = line_count * line_h + box_pad * 2
        box_w = max_box_w
        box_x = (RESOLUTION[0] - box_w) // 2
        box_y = RESOLUTION[1] - box_h - 25
        overlay = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=20,
            fill=(0, 0, 0, 160),
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw_wrapped_text(
            draw,
            caption,
            caption_font,
            RESOLUTION[0] // 2,
            box_y + box_pad,
            max_box_w - box_pad * 2,
            line_h,
        )

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

    char_clip = char_clip.resized(
        lambda t: (
            char_w * (1 + breath * math.sin(t * 3)),
            char_h * (1 + breath * math.sin(t * 3)),
        )
    )
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


def build_scene_images(assets_dir: Path, scenes: list[dict], theme: str) -> list[Path]:
    scene_images: list[Path] = []
    for i, scene in enumerate(scenes):
        prompt = scene_to_background_prompt(scene, theme)
        # Use a short hash of the prompt for caching to avoid redownloading
        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
        bg_path = assets_dir / f"bg_{i:03d}_{prompt_hash}.png"
        fetch_image(prompt, bg_path)
        out = assets_dir / f"scene_{i:03d}_composite.png"
        build_scene_image(bg_path, scene["text"], scene["text"], out)
        scene_images.append(out)
    return scene_images


def compute_positions(scenes: list[dict]) -> list[dict]:
    # Use a dummy character size for layout; actual resized size is computed later.
    dummy_w, dummy_h = 512, 512
    return [scene_to_position(i, len(scenes), dummy_w, dummy_h) for i in range(len(scenes))]


async def main_async(project_dir_str: str = "examples/what-if-gravity-disappeared") -> None:
    project_dir = Path(project_dir_str)
    assets_dir = project_dir / "assets"
    output_dir = project_dir / "output"
    audio_dir = project_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    project = load_project(str(project_dir / "project.yaml"))
    scenes = parse_script(str(project_dir / "script.md"))
    theme = project.get("style", {}).get("category", "educational-cartoon")

    print(f"[1/4] Generating character for {len(scenes)} scenes...")
    generate_assets(assets_dir)

    print("[2/4] Building scene images with AI backgrounds...")
    scene_images = build_scene_images(assets_dir, scenes, theme)

    print("[3/4] Rendering scenes with narration...")
    positions = compute_positions(scenes)
    clip_paths: list[str] = []
    for i, scene in enumerate(scenes):
        audio_path = audio_dir / f"scene_v2_{i:03d}.mp3"
        if not audio_path.exists():
            print(f"  Generating audio for scene {i + 1}...")
            await generate_audio(scene["text"], str(audio_path))
        print(f"  Rendering scene {i + 1}...")
        clip_path = render_scene(
            i, scene["text"], str(audio_path), scene_images[i],
            assets_dir / "character.png", output_dir, positions[i],
        )
        clip_paths.append(clip_path)

    final_path = output_dir / "final_aumsum_v2.mp4"
    print("[4/4] Assembling final video...")
    assemble(clip_paths, final_path)
    print(f"Done: {final_path.resolve()}")


if __name__ == "__main__":
    import sys
    project_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "examples/what-if-gravity-disappeared"
    asyncio.run(main_async(project_dir_arg))
