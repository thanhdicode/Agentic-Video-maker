"""AumSum-style CPU demo v3 — more engaging animation for kids.

Improvements over v2:
- Multiple mascot poses (neutral, pointing, surprised, thumbsup, waving).
- Per-scene prop overlays that float/animate.
- Ken Burns zoom/pan on backgrounds.
- Particle overlays (stars, bubbles, sparks, confetti) per scene theme.
- Background music + scene-start SFX generated with pydub.
- Animated intro and outro cards.
- Crossfade transitions.

Still CPU + Pollinations-based, so it is not full GPU frame generation, but it is
much more dynamic and kid-friendly than static image slideshows.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import random
import re
import textwrap
import urllib.parse
from io import BytesIO
from pathlib import Path

import cv2
import edge_tts
import numpy as np
import requests
import yaml
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoClip,
    afx,
    concatenate_audioclips,
    concatenate_videoclips,
    vfx,
)
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
from pydub.generators import Sine, Square


RESOLUTION = (1280, 720)
FPS = 30
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
VOICE = "en-US-AriaNeural"
POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
SEED = 2026

NEGATIVE_BG = "character, person, mascot, human, animal, text, watermark, signature"
NEGATIVE_CHAR = "text, watermark, signature, bad anatomy, extra limbs, deformed"
NEGATIVE_PROP = "text, watermark, signature, character, person, mascot"


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


def fetch_image(
    prompt: str,
    out_path: Path,
    width: int = 1280,
    height: int = 720,
    negative: str = "",
) -> None:
    if out_path.exists():
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = (
        f"{POLLINATIONS_BASE}/{urllib.parse.quote(prompt)}"
        f"?width={width}&height={height}&nologo=true&seed={SEED}"
    )
    if negative:
        url += f"&negative_prompt={urllib.parse.quote(negative)}"
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


# ---------------------------------------------------------------------------
# Music / SFX
# ---------------------------------------------------------------------------

def _note(freq: float, duration_ms: int, volume_db: float = -14) -> AudioSegment:
    """Create a simple sine-wave tone."""
    return Sine(freq).to_audio_segment(duration=duration_ms, volume=volume_db)


def generate_music(total_ms: int, out_path: Path) -> None:
    """Generate a simple cheerful looping background track."""
    if out_path.exists():
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # C major cheerful arpeggio
    scale = [523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 523.25, 659.25]
    beat_ms = 250
    loop = AudioSegment.silent(duration=0)
    for freq in scale:
        loop += _note(freq, beat_ms, volume_db=-18)
    # Loop to target duration
    final = AudioSegment.silent(duration=0)
    while len(final) < total_ms:
        final += loop
    final = final[:total_ms]
    final.export(str(out_path), format="mp3")


def generate_sfx(out_path: Path) -> AudioSegment:
    """Generate a generic 'pop' sound effect."""
    if out_path.exists():
        return AudioSegment.from_mp3(str(out_path))
    # Short upward chirp
    base = Sine(600).to_audio_segment(duration=80, volume=-8)
    chirp = Sine(900).to_audio_segment(duration=50, volume=-10)
    pop = base.overlay(chirp, position=30)
    pop.export(str(out_path), format="mp3")
    return pop


def generate_whoosh(out_path: Path) -> AudioSegment:
    """Generate a soft whoosh for transitions."""
    if out_path.exists():
        return AudioSegment.from_mp3(str(out_path))
    # White-ish noise sweep using square wave frequencies sliding down
    whoosh = AudioSegment.silent(duration=0)
    for i in range(20):
        freq = 800 - i * 30
        seg = Square(freq).to_audio_segment(duration=30, volume=-22)
        whoosh += seg
    whoosh.export(str(out_path), format="mp3")
    return whoosh


# ---------------------------------------------------------------------------
# Asset generation
# ---------------------------------------------------------------------------

CHARACTER_POSES = {
    "neutral": (
        "AumSum style cute turquoise cartoon mascot, big friendly eyes, "
        "wide smile, short dark hair, 2D flat vector, full body, neutral standing pose, "
        "hands on hips, white background, high quality, no text"
    ),
    "pointing": (
        "AumSum style cute turquoise cartoon mascot, big friendly eyes, "
        "smiling, short dark hair, 2D flat vector, full body, pointing to the right, "
        "white background, high quality, no text"
    ),
    "surprised": (
        "AumSum style cute turquoise cartoon mascot, big surprised eyes, "
        "open mouth, hands up, short dark hair, 2D flat vector, full body, "
        "white background, high quality, no text"
    ),
    "thumbsup": (
        "AumSum style cute turquoise cartoon mascot, big friendly eyes, "
        "wide smile, short dark hair, 2D flat vector, full body, thumbs up, "
        "white background, high quality, no text"
    ),
    "waving": (
        "AumSum style cute turquoise cartoon mascot, big friendly eyes, "
        "wide smile, short dark hair, 2D flat vector, full body, waving hand, "
        "white background, high quality, no text"
    ),
}


def generate_character_poses(assets_dir: Path) -> dict[str, Path]:
    print("[Assets] Generating mascot poses...")
    paths: dict[str, Path] = {}
    for name, prompt in CHARACTER_POSES.items():
        raw = assets_dir / f"character_{name}_raw.png"
        png = assets_dir / f"character_{name}.png"
        fetch_image(prompt, raw, width=1024, height=1024, negative=NEGATIVE_CHAR)
        remove_background(raw, png)
        paths[name] = png
    return paths


def scene_to_pose_name(scene: dict) -> str:
    title = scene["title"].lower()
    text = scene["text"].lower()
    if any(w in title for w in ("outro", "everybody", "stay", "worry")):
        return "waving"
    if any(w in title for w in ("hook", "what if")):
        return "surprised"
    if any(w in title for w in ("steps", "good thing", "thank")) or "we can" in text:
        return "thumbsup"
    if any(w in text for w in ("point", "look", "there", "see")):
        return "pointing"
    return "neutral"


def scene_to_prop(scene: dict) -> tuple[str | None, str]:
    """Return (prop_prompt, motion_type) or (None, '')."""
    title = scene["title"].lower()
    text = scene["text"].lower()
    if any(w in text for w in ("moon", "earth")):
        return ("AumSum style 2D cartoon moon with craters, flat vector, white background, no text", "float")
    if any(w in text for w in ("planet", "sun", "orbit")):
        return ("AumSum style 2D cartoon planet with rings, flat vector, white background, no text", "orbit")
    if any(w in text for w in ("ocean", "water", "river", "lake", "sea")):
        return ("AumSum style 2D cartoon water drop, flat vector, white background, no text", "float")
    if any(w in text for w in ("fire", "flame")):
        return ("AumSum style 2D cartoon flame, flat vector, white background, no text", "float")
    if any(w in text for w in ("build", "house", "tools", "hammer")):
        return ("AumSum style 2D cartoon floating toolbox, flat vector, white background, no text", "float")
    if any(w in text for w in ("chair", "table", "floating")):
        return ("AumSum style 2D cartoon floating chair, flat vector, white background, no text", "float")
    if any(w in text for w in ("atmosphere", "air", "breathe", "wind", "cloud")):
        return ("AumSum style 2D cartoon cloud, flat vector, white background, no text", "float")
    return (None, "")


def generate_prop(prop_prompt: str, assets_dir: Path, idx: int) -> Path | None:
    if not prop_prompt:
        return None
    raw = assets_dir / f"prop_{idx:03d}_raw.png"
    png = assets_dir / f"prop_{idx:03d}.png"
    fetch_image(prop_prompt, raw, width=512, height=512, negative=NEGATIVE_PROP)
    remove_background(raw, png)
    return png


# ---------------------------------------------------------------------------
# Backgrounds / captions
# ---------------------------------------------------------------------------

def scene_to_background_prompt(scene: dict, theme: str) -> str:
    title = scene["title"].lower()
    text = scene["text"].lower()
    keywords = []
    if any(w in title or w in text for w in ("space", "moon", "planet", "sun", "orbit", "star")):
        keywords.append("outer space with stars and planets")
    if any(w in title or w in text for w in ("ocean", "water", "sea", "river", "lake", "underwater")):
        keywords.append("underwater ocean scene")
    if any(w in title or w in text for w in ("float", "floating", "fly", "flying", "zero gravity")):
        keywords.append("objects floating in zero gravity")
    if any(w in title or w in text for w in ("fire", "flame", "burn", "hot")):
        keywords.append("floating round flames")
    if any(w in title or w in text for w in ("build", "house", "tools", "construction")):
        keywords.append("construction site with floating tools")
    if any(w in title or w in text for w in ("atmosphere", "air", "breathe", "cloud", "wind")):
        keywords.append("sky with clouds and wind")
    if any(w in title or w in text for w in ("home", "earth", "world", "save")):
        keywords.append("Earth from space with bright colors")
    if not keywords:
        keywords.append(theme)

    setting = ", ".join(keywords[:2])
    prompt = (
        f"AumSum style 2D cartoon educational empty scene, {setting}, "
        "bright colors, flat vector illustration, no character, no mascot, no text, high quality"
    )
    return prompt


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


def build_caption_overlay(scene: dict, output_path: Path) -> None:
    if output_path.exists():
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Optional tiny topic label at top (first 2 words) to avoid covering the character
    words = scene["text"].split()
    if len(words) > 1:
        topic = " ".join(words[:3])
        topic_font = safe_font(38)
        bbox = draw.textbbox((0, 0), topic, font=topic_font)
        tw = bbox[2] - bbox[0]
        x = (RESOLUTION[0] - tw) // 2
        y = 25
        draw.text((x + 2, y + 2), topic, font=topic_font, fill=(0, 0, 0))
        draw.text((x, y), topic, font=topic_font, fill=(255, 220, 80))

    # Caption box at bottom
    caption_font = safe_font(34)
    box_pad = 18
    max_box_w = RESOLUTION[0] - 120
    line_h = 40
    wrapped = textwrap.fill(scene["text"], width=50)
    line_count = wrapped.count("\n") + 1
    box_h = line_count * line_h + box_pad * 2
    box_w = max_box_w
    box_x = (RESOLUTION[0] - box_w) // 2
    box_y = RESOLUTION[1] - box_h - 25
    overlay = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=24,
        fill=(0, 0, 0, 170),
    )
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    draw_wrapped_text(
        draw,
        scene["text"],
        caption_font,
        RESOLUTION[0] // 2,
        box_y + box_pad,
        max_box_w - box_pad * 2,
        line_h,
    )

    img.save(output_path, "PNG")


def build_scene_background(
    scene: dict,
    theme: str,
    assets_dir: Path,
    idx: int,
) -> Path:
    prompt = scene_to_background_prompt(scene, theme)
    prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
    bg_path = assets_dir / f"bg_v3_{idx:03d}_{prompt_hash}.png"
    fetch_image(prompt, bg_path, negative=NEGATIVE_BG)
    return bg_path


# ---------------------------------------------------------------------------
# Motion clips
# ---------------------------------------------------------------------------

def make_ken_burns_clip(image_path: Path, duration: float, zoom: float = 0.08) -> ImageClip:
    """Slow zoom + gentle drift on a static image."""
    pil_img = Image.open(image_path).convert("RGB")
    base_arr = np.array(pil_img)
    base = ImageClip(base_arr, duration=duration)

    def get_size(t: float) -> tuple[int, int]:
        s = 1.0 + zoom * (t / duration)
        return (int(RESOLUTION[0] * s), int(RESOLUTION[1] * s))

    clip = base.with_effects([vfx.Resize(get_size)])

    def get_pos(t: float) -> tuple[float, float]:
        w, h = get_size(t)
        # slow circular drift
        dx = 20 * math.sin(t * 0.4)
        dy = 12 * math.cos(t * 0.3)
        return (RESOLUTION[0] / 2 - w / 2 + dx, RESOLUTION[1] / 2 - h / 2 + dy)

    clip = clip.with_position(get_pos)
    return clip


def make_character_clip(
    character_path: Path,
    duration: float,
    base_x: int,
    base_y: int,
    scale: float = 0.45,
) -> ImageClip:
    pil_img = Image.open(character_path).convert("RGBA")
    target_h = int(RESOLUTION[1] * scale)
    char_w = int(pil_img.width * target_h / pil_img.height)
    char_h = target_h
    pil_img = pil_img.resize((char_w, char_h), Image.LANCZOS)
    base = ImageClip(np.array(pil_img), duration=duration)

    breath = 0.03
    bounce = 8

    def get_size(t: float) -> tuple[int, int]:
        s = 1.0 + breath * math.sin(t * 3)
        return (int(char_w * s), int(char_h * s))

    clip = base.with_effects([
        vfx.Resize(get_size),
        vfx.Rotate(lambda t: 4 * math.sin(t * 2.5)),
    ])

    def get_pos(t: float) -> tuple[float, float]:
        w, h = get_size(t)
        y = base_y + bounce * math.sin(t * 5)
        return (base_x - w / 2, y - h / 2)

    clip = clip.with_position(get_pos)
    return clip


def make_prop_clip(
    prop_path: Path,
    duration: float,
    motion: str = "float",
) -> ImageClip | None:
    pil_img = Image.open(prop_path).convert("RGBA")
    target_h = int(RESOLUTION[1] * 0.28)
    prop_w = int(pil_img.width * target_h / pil_img.height)
    prop_h = target_h
    pil_img = pil_img.resize((prop_w, prop_h), Image.LANCZOS)
    base = ImageClip(np.array(pil_img), duration=duration)

    def get_size(t: float) -> tuple[int, int]:
        s = 1.0 + 0.05 * math.sin(t * 3)
        return (int(prop_w * s), int(prop_h * s))

    base = base.with_effects([vfx.Resize(get_size)])

    if motion == "orbit":
        def get_pos(t: float) -> tuple[float, float]:
            w, h = get_size(t)
            cx = RESOLUTION[0] * 0.75
            cy = RESOLUTION[1] * 0.35
            r = 180
            x = cx + r * math.cos(t * 0.8) - w / 2
            y = cy + r * 0.4 * math.sin(t * 0.8) - h / 2
            return (x, y)
    elif motion == "float":
        def get_pos(t: float) -> tuple[float, float]:
            w, h = get_size(t)
            x = RESOLUTION[0] * 0.78 - w / 2 + 30 * math.sin(t * 0.7)
            y = RESOLUTION[1] * 0.25 - h / 2 + 20 * math.cos(t * 1.2)
            return (x, y)
    else:
        def get_pos(t: float) -> tuple[float, float]:
            w, h = get_size(t)
            return (RESOLUTION[0] * 0.78 - w / 2, RESOLUTION[1] * 0.25 - h / 2)

    base = base.with_position(get_pos)
    return base


class ParticleSystem:
    def __init__(self, theme: str, count: int = 25) -> None:
        self.theme = theme
        self.count = count
        self.particles: list[dict] = []
        rng = random.Random(SEED)
        for _ in range(count):
            p = {
                "x": rng.randint(0, RESOLUTION[0]),
                "y": rng.randint(0, RESOLUTION[1]),
                "vx": rng.uniform(-20, 20),
                "vy": rng.uniform(-20, -5) if "float" in theme else rng.uniform(-10, 10),
                "size": rng.randint(3, 8),
                "phase": rng.uniform(0, 2 * math.pi),
            }
            if theme == "fire":
                p["color"] = (255, rng.randint(80, 180), 0, 180)
            elif theme == "ocean":
                p["color"] = (200, 230, 255, 160)
            elif theme == "space":
                p["color"] = (255, 255, 220, 200)
            else:
                p["color"] = (rng.randint(180, 255), rng.randint(180, 255), rng.randint(180, 255), 180)
            self.particles.append(p)

    def make_frame(self, t: float) -> np.ndarray:
        frame = np.zeros((RESOLUTION[1], RESOLUTION[0], 4), dtype=np.uint8)
        for p in self.particles:
            x = int(p["x"] + p["vx"] * t + 10 * math.sin(t + p["phase"]))
            y = int(p["y"] + p["vy"] * t + 10 * math.cos(t + p["phase"]))
            # wrap around
            x = x % RESOLUTION[0]
            y = y % RESOLUTION[1]
            cv2.circle(frame, (x, y), p["size"], p["color"], -1)
        return frame


def make_particle_clip(duration: float, theme: str) -> VideoClip:
    system = ParticleSystem(theme)
    return VideoClip(system.make_frame, duration=duration).with_fps(FPS)


# ---------------------------------------------------------------------------
# Scene layout
# ---------------------------------------------------------------------------

def scene_layout(i: int, total: int) -> dict:
    """Choose character horizontal position and scale for a scene."""
    layouts = [
        {"x_rel": 0.20, "scale": 0.45},
        {"x_rel": 0.80, "scale": 0.45},
        {"x_rel": 0.50, "scale": 0.50},
        {"x_rel": 0.28, "scale": 0.42},
        {"x_rel": 0.72, "scale": 0.42},
    ]
    return layouts[i % len(layouts)]


# ---------------------------------------------------------------------------
# Render / assemble
# ---------------------------------------------------------------------------

def render_scene(
    scene: dict,
    idx: int,
    audio_path: str,
    bg_path: Path,
    caption_path: Path,
    character_path: Path,
    prop_path: Path | None,
    output_dir: Path,
    theme: str,
) -> str:
    duration = audio_duration(audio_path)

    bg_clip = make_ken_burns_clip(bg_path, duration, zoom=0.06)
    overlay_clip = ImageClip(np.array(Image.open(caption_path).convert("RGBA")), duration=duration)

    # Character
    pil_char = Image.open(character_path).convert("RGBA")
    layout = scene_layout(idx, 10)
    target_h = int(RESOLUTION[1] * layout["scale"])
    char_w = int(pil_char.width * target_h / pil_char.height)
    char_h = target_h
    # keep feet above the caption box (caption box ~120px from bottom)
    base_x = int(RESOLUTION[0] * layout["x_rel"])
    base_y = int(RESOLUTION[1] - target_h / 2 - 120)
    char_clip = make_character_clip(character_path, duration, base_x, base_y, scale=layout["scale"])

    # Prop
    prop_clip = None
    if prop_path:
        prop_prompt, motion = scene_to_prop(scene)
        prop_clip = make_prop_clip(prop_path, duration, motion)

    # Particles
    particle_theme = "default"
    if any(w in scene["text"].lower() for w in ("space", "moon", "planet", "sun", "star")):
        particle_theme = "space"
    elif any(w in scene["text"].lower() for w in ("ocean", "water", "sea", "river", "lake", "underwater")):
        particle_theme = "ocean"
    elif any(w in scene["text"].lower() for w in ("fire", "flame")):
        particle_theme = "fire"
    particle_clip = make_particle_clip(duration, particle_theme)

    layers = [bg_clip]
    if prop_clip:
        layers.append(prop_clip)
    layers.append(char_clip)
    layers.append(particle_clip)
    layers.append(overlay_clip)

    composite = CompositeVideoClip(layers, size=RESOLUTION)
    composite = composite.with_fps(FPS)

    out_path = output_dir / f"scene_v3_{idx:03d}.mp4"
    composite.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio=False,
        threads=4,
        preset="ultrafast",
    )
    composite.close()
    return str(out_path)


def make_title_card(text: str, duration: float, color: tuple[int, int, int] = (255, 220, 80)) -> str:
    """Return a temporary mp4 path for an intro/outro title card."""
    # Create a gradient background image
    img = Image.new("RGB", RESOLUTION, (25, 50, 120))
    draw = ImageDraw.Draw(img)
    for y in range(RESOLUTION[1]):
        r = int(25 + (y / RESOLUTION[1]) * 40)
        g = int(50 + (y / RESOLUTION[1]) * 80)
        b = int(120 + (y / RESOLUTION[1]) * 60)
        draw.line([(0, y), (RESOLUTION[0], y)], fill=(r, g, b))

    bg_clip = ImageClip(np.array(img), duration=duration)

    title = TextClip(
        text=text,
        font_size=80,
        color="white",
        stroke_color="black",
        stroke_width=3,
        font=FONT_PATH,
        size=(1200, 300),
        text_align="center",
        duration=duration,
    )
    title = title.with_position("center")
    title = title.with_effects([vfx.Resize(lambda t: (int(min(1.0 + 0.1 * t, 1.1) * 1200), int(min(1.0 + 0.1 * t, 1.1) * 300)))])

    sub = TextClip(
        text="AumSum-style AI Studio",
        font_size=40,
        color=color,
        font=FONT_PATH,
        size=(1200, 100),
        text_align="center",
        duration=duration,
    )
    sub = sub.with_position((0, 450))

    composite = CompositeVideoClip([bg_clip, title, sub], size=RESOLUTION)
    composite = composite.with_fps(FPS)
    out = Path("projects") / "_tmp_title.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    composite.write_videofile(str(out), fps=FPS, codec="libx264", audio=False, threads=4, preset="ultrafast")
    composite.close()
    return str(out)


def _export_silent_mp3(duration_ms: int, out_path: Path) -> Path:
    AudioSegment.silent(duration=duration_ms).export(str(out_path), format="mp3")
    return out_path


def _sfx_at(start_s: float, out_path: Path) -> AudioFileClip:
    generate_sfx(out_path)
    return AudioFileClip(str(out_path)).with_start(start_s)


def assemble_final(
    scene_paths: list[str],
    scene_audio_paths: list[str],
    scene_starts: list[float],
    output: Path,
    project_title: str,
) -> Path:
    from moviepy import VideoFileClip

    print("[4/5] Building intro/outro and transitions...")
    intro_path = make_title_card(project_title, 3.0)
    outro_text = "Thanks for watching!\nLike & Subscribe for more!"
    outro_path = make_title_card(outro_text, 4.0, color=(80, 255, 120))

    scene_clips = [VideoFileClip(p) for p in scene_paths]
    intro_clip = VideoFileClip(intro_path)
    outro_clip = VideoFileClip(outro_path)

    # Apply fade in/out per scene
    for i, clip in enumerate(scene_clips):
        clip = clip.with_effects([vfx.FadeIn(0.4), vfx.FadeOut(0.4)])
        scene_clips[i] = clip

    all_video = [intro_clip] + scene_clips + [outro_clip]
    final_video = concatenate_videoclips(all_video, method="compose", padding=-0.3)

    # Build audio
    print("[5/5] Mixing audio...")
    tmp_dir = output.parent / "_tmp_audio"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Voice track
    voice_clips: list[AudioFileClip] = []
    intro_silence = _export_silent_mp3(int(intro_clip.duration * 1000), tmp_dir / "silence_intro.mp3")
    voice_clips.append(AudioFileClip(str(intro_silence)))
    for p in scene_audio_paths:
        voice_clips.append(AudioFileClip(p).with_effects([afx.AudioFadeIn(0.2), afx.AudioFadeOut(0.2)]))
    outro_silence = _export_silent_mp3(int(outro_clip.duration * 1000), tmp_dir / "silence_outro.mp3")
    voice_clips.append(AudioFileClip(str(outro_silence)))
    voice_track = concatenate_audioclips(voice_clips)

    # Music track
    music_path = tmp_dir / "bg_music.mp3"
    generate_music(int(final_video.duration * 1000) + 500, music_path)
    music = AudioFileClip(str(music_path)).subclipped(0, final_video.duration).with_volume_scaled(0.12)

    # SFX pops at scene starts
    sfx_list: list[AudioFileClip] = []
    for start in scene_starts:
        sfx_list.append(_sfx_at(start + intro_clip.duration, tmp_dir / f"sfx_{start:.2f}.mp3"))

    final_audio = CompositeAudioClip([voice_track, music] + sfx_list)
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        str(output),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
    )

    for c in all_video:
        c.close()
    voice_track.close()
    music.close()
    for s in sfx_list:
        s.close()
    return output


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
    project_title = project["project"]["title"]
    theme = project.get("style", {}).get("category", "educational-cartoon")

    print(f"[1/5] Generating mascot poses for {len(scenes)} scenes...")
    character_poses = generate_character_poses(assets_dir)

    print("[2/5] Generating backgrounds, props and captions...")
    bg_paths: list[Path] = []
    caption_paths: list[Path] = []
    prop_paths: list[Path | None] = []
    scene_audio_paths: list[str] = []
    for i, scene in enumerate(scenes):
        bg_path = build_scene_background(scene, theme, assets_dir, i)
        caption_path = assets_dir / f"caption_v3_{i:03d}.png"
        build_caption_overlay(scene, caption_path)
        prop_prompt, _ = scene_to_prop(scene)
        prop_path = generate_prop(prop_prompt, assets_dir, i) if prop_prompt else None

        audio_path = audio_dir / f"scene_v3_{i:03d}.mp3"
        if not audio_path.exists():
            print(f"  Generating audio for scene {i + 1}...")
            await generate_audio(scene["text"], str(audio_path))

        bg_paths.append(bg_path)
        caption_paths.append(caption_path)
        prop_paths.append(prop_path)
        scene_audio_paths.append(str(audio_path))

    print("[3/5] Rendering scenes...")
    scene_paths: list[str] = []
    scene_starts: list[float] = []
    current_start = 0.0
    for i, scene in enumerate(scenes):
        pose = scene_to_pose_name(scene)
        character_path = character_poses.get(pose, character_poses["neutral"])
        print(f"  Rendering scene {i + 1} with pose '{pose}'...")
        clip_path = render_scene(
            scene,
            i,
            scene_audio_paths[i],
            bg_paths[i],
            caption_paths[i],
            character_path,
            prop_paths[i],
            output_dir,
            theme,
        )
        scene_paths.append(clip_path)
        scene_starts.append(current_start)
        current_start += audio_duration(scene_audio_paths[i]) - 0.3  # account for padding

    final_path = output_dir / "final_aumsum_v3.mp4"
    print("[Assemble] Creating final video...")
    assemble_final(scene_paths, scene_audio_paths, scene_starts, final_path, project_title)
    print(f"Done: {final_path.resolve()}")


if __name__ == "__main__":
    import sys
    project_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "examples/what-if-gravity-disappeared"
    asyncio.run(main_async(project_dir_arg))
