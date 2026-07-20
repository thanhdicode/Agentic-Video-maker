"""AumSum-style CPU demo v4 — puppet face animation, lip-sync, and longer scripts.

Improvements over v3:
- Per-frame face animation: eyes track props, pupils move, periodic blinks.
- Lip-sync driven by Rhubarb (or audio-volume fallback) on the mascot.
- Squash / stretch / anticipation motion on the character body.
- More dynamic prop paths (orbit, float, fly-across).
- Longer 18-scene educational scripts (3-4 minutes).
- SRT subtitle and storyboard JSON output.

Still CPU + Pollinations-based, so motion is code-driven transforms of AI assets,
not full GPU frame generation. For true Disney/Anime smoothness see
`docs/DEEP_ANIMATION_RESEARCH.md` and `docs/PRODUCTION_STACK.md`.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
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

from tools.rhubarb_lipsync import mouth_open_at, run_rhubarb, volume_based_mouth


RESOLUTION = (1280, 720)
FPS = 30
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
VOICE = "en-US-AriaNeural"
POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
SEED = 2026

NEGATIVE_BG = "character, person, mascot, human, animal, text, watermark, signature"
NEGATIVE_CHAR = "text, watermark, signature, bad anatomy, extra limbs, deformed, cropped hands"
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
    pattern = re.compile(r"## Scene \d+:\s*(.*?)\n(.*?)\n(?=## Scene \d+:|\Z)", re.S)
    for m in pattern.finditer(text + "\n"):
        title = m.group(1).strip()
        body = m.group(2).strip()
        scenes.append({"title": title, "text": body})
    return scenes


def load_project(project_path: str) -> dict:
    with open(project_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def generate_audio(text: str, out_path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate="-15%")
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
    return Sine(freq).to_audio_segment(duration=duration_ms, volume=volume_db)


def generate_music(total_ms: int, out_path: Path) -> None:
    if out_path.exists():
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Cheerful C major arpeggio
    scale = [523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 523.25, 659.25]
    beat_ms = 250
    loop = AudioSegment.silent(duration=0)
    for freq in scale:
        loop += _note(freq, beat_ms, volume_db=-20)
    final = AudioSegment.silent(duration=0)
    while len(final) < total_ms:
        final += loop
    final = final[:total_ms]
    final.export(str(out_path), format="mp3")


def generate_sfx(out_path: Path) -> AudioSegment:
    if out_path.exists():
        return AudioSegment.from_mp3(str(out_path))
    base = Sine(600).to_audio_segment(duration=80, volume=-10)
    chirp = Sine(900).to_audio_segment(duration=50, volume=-12)
    pop = base.overlay(chirp, position=30)
    pop.export(str(out_path), format="mp3")
    return pop


def generate_whoosh(out_path: Path) -> AudioSegment:
    if out_path.exists():
        return AudioSegment.from_mp3(str(out_path))
    whoosh = AudioSegment.silent(duration=0)
    for i in range(20):
        freq = 800 - i * 30
        seg = Square(freq).to_audio_segment(duration=30, volume=-24)
        whoosh += seg
    whoosh.export(str(out_path), format="mp3")
    return whoosh


def generate_chime(out_path: Path) -> AudioSegment:
    """A bright magical chime for scene highlights."""
    if out_path.exists():
        return AudioSegment.from_mp3(str(out_path))
    chime = AudioSegment.silent(duration=0)
    for freq in [880, 1108, 1318, 1760]:
        chime += Sine(freq).to_audio_segment(duration=120, volume=-12)
    chime.export(str(out_path), format="mp3")
    return chime


# ---------------------------------------------------------------------------
# Asset generation
# ---------------------------------------------------------------------------

# Consistent mascot image (generated once and reused for every pose)
CONSISTENT_MASCOT = Path("assets/mascot_final.png")


def generate_character_poses(assets_dir: Path) -> dict[str, Path]:
    print("[Assets] Using consistent mascot for all poses...")
    paths: dict[str, Path] = {}
    for name in ("neutral", "pointing", "surprised", "thumbsup", "waving"):
        png = assets_dir / f"character_{name}.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        if not png.exists():
            import shutil
            shutil.copy(CONSISTENT_MASCOT, png)
        paths[name] = png
    return paths


def scene_to_pose_name(scene: dict) -> str:
    title = scene["title"].lower()
    text = scene["text"].lower()
    if any(w in title for w in ("outro", "everybody", "stay", "worry", "like")):
        return "waving"
    if any(w in title for w in ("hook", "what if", "wonder", "secret")) or "?" in text:
        return "surprised"
    if any(w in title for w in ("steps", "good thing", "thank", "remember")) or "we can" in text:
        return "thumbsup"
    if any(w in text for w in ("point", "look", "there", "see", "right")):
        return "pointing"
    return "neutral"


def scene_to_prop(scene: dict) -> tuple[str | None, str]:
    """Return (prop_prompt, motion)."""
    text = scene["text"].lower()
    title = scene["title"].lower()
    if any(w in text for w in ("sun", "sunlight", "sun")) or "sun" in title:
        return ("AumSum style 2D cartoon bright Sun with rays, flat vector, white background, no text", "orbit")
    if any(w in text for w in ("moon", "moon")):
        return ("AumSum style 2D cartoon Moon with craters, flat vector, white background, no text", "orbit")
    if any(w in text for w in ("star", "space", "astronaut")):
        return ("AumSum style 2D cartoon shining star, flat vector, white background, no text", "float")
    if any(w in text for w in ("rainbow", "color")):
        return ("AumSum style 2D cartoon rainbow arc, flat vector, white background, no text", "float")
    if any(w in text for w in ("wave", "light wave", "wavelength", "scatter")):
        return ("AumSum style 2D cartoon blue light wave, flat vector, white background, no text", "fly")
    if any(w in text for w in ("air", "atmosphere", "sky", "horizon", "cloud")):
        return ("AumSum style 2D cartoon fluffy cloud, flat vector, white background, no text", "float")
    if any(w in text for w in ("particle", "dust", "gas")):
        return ("AumSum style 2D cartoon tiny gas particle bubble, flat vector, white background, no text", "float")
    if any(w in text for w in ("earth", "planet")):
        return ("AumSum style 2D cartoon Earth planet, flat vector, white background, no text", "orbit")
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


def _scene_words(scene: dict) -> set[str]:
    return set(re.findall(r"[a-z]+", (scene["title"] + " " + scene["text"]).lower()))


def scene_to_background_prompt(scene: dict, theme: str) -> str:
    words = _scene_words(scene)
    keywords: list[str] = []
    if words & {"space", "moon", "planet", "orbit", "star", "astronaut"}:
        keywords.append("outer space with stars and planets")
    if words & {"ocean", "water", "sea", "river", "lake", "underwater"}:
        keywords.append("underwater ocean scene")
    if words & {"sun", "sunlight", "sunny", "day", "bright"}:
        keywords.append("bright sunny sky with light rays")
    if words & {"sunset", "sunrise", "horizon", "orange", "pink"}:
        keywords.append("warm sunset sky with orange and pink clouds")
    if words & {"atmosphere", "air", "sky", "blue"}:
        keywords.append("blue sky with soft clouds")
    if words & {"rainbow", "color"}:
        keywords.append("rainbow colored light beams")
    if words & {"earth", "world"}:
        keywords.append("Earth seen from space")
    if words & {"night", "dark"}:
        keywords.append("dark night sky with stars")
    if not keywords:
        keywords.append(theme)

    setting = ", ".join(keywords[:2])
    return (
        f"AumSum style 2D cartoon educational empty scene, {setting}, "
        "bright colors, flat vector illustration, no character, no mascot, no text, high quality"
    )


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

    # Small topic label at top
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
    bg_path = assets_dir / f"bg_v4_{idx:03d}_{prompt_hash}.png"
    fetch_image(prompt, bg_path, negative=NEGATIVE_BG)
    return bg_path


# ---------------------------------------------------------------------------
# Easing and face animation
# ---------------------------------------------------------------------------


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    arr = np.array(img)
    if arr.shape[2] < 4:
        return None
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 50)
    if len(xs) == 0:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))


def sample_skin_color(img: Image.Image, x: float, y: float, radius: int = 10) -> tuple[int, int, int, int]:
    arr = np.array(img)
    h, w = arr.shape[:2]
    x0, y0 = max(0, int(x) - radius), max(0, int(y) - radius)
    x1, y1 = min(w, int(x) + radius), min(h, int(y) + radius)
    patch = arr[y0:y1, x0:x1]
    if patch.size == 0:
        return (128, 128, 128, 255)
    alpha = patch[:, :, 3]
    colors = patch[alpha > 80][:, :3]
    if len(colors) == 0:
        return (128, 128, 128, 255)
    avg = colors.mean(axis=0).astype(int)
    return (int(avg[0]), int(avg[1]), int(avg[2]), 255)


def draw_face(
    base_img: Image.Image,
    mouth_open: float,
    look_at: tuple[float, float],
    blink: bool,
) -> Image.Image:
    """Draw animated eyes and mouth over the mascot."""
    img = base_img.copy()
    bbox = alpha_bbox(img)
    if not bbox:
        return img
    x, y, w, h = bbox
    cx = x + w / 2
    eye_y = y + h * 0.30
    left_x = cx - w * 0.08
    right_x = cx + w * 0.08
    mouth_y = y + h * 0.52
    skin = sample_skin_color(img, cx, eye_y, 12)
    draw = ImageDraw.Draw(img, "RGBA")

    ew = max(6, int(w * 0.10))
    eh = max(5, int(h * 0.08))
    for ex in (left_x, right_x):
        if blink:
            # eyelid covers the eye for a blink
            draw.ellipse([ex - ew, eye_y - eh, ex + ew, eye_y + eh], fill=skin)
            draw.arc(
                [ex - ew, eye_y - eh * 0.5, ex + ew, eye_y + eh * 0.5],
                start=10,
                end=170,
                fill=(0, 0, 0, 255),
                width=max(1, int(ew * 0.08)),
            )
        else:
            # moving catchlight to make the original painted eye feel alive
            max_off = ew * 0.25
            hx = ex + (look_at[0] - 0.5) * max_off * 2
            hy = eye_y + (look_at[1] - 0.5) * max_off * 2
            draw.ellipse(
                [hx - ew * 0.12, hy - eh * 0.12, hx + ew * 0.12, hy + eh * 0.12],
                fill=(255, 255, 255, 220),
            )

    mw = max(6, int(w * 0.13))
    mh = max(4, int(h * 0.05))
    draw.ellipse([cx - mw * 0.75, mouth_y - mh * 0.75, cx + mw * 0.75, mouth_y + mh * 0.75], fill=skin)
    if mouth_open < 0.12:
        draw.arc(
            [cx - mw * 0.6, mouth_y - mh * 0.5, cx + mw * 0.6, mouth_y + mh * 0.5],
            start=10,
            end=170,
            fill=(0, 0, 0, 255),
            width=max(1, int(mw * 0.05)),
        )
    else:
        mh_open = max(2, int(mh * mouth_open * 3.0))
        draw.ellipse([cx - mw * 0.55, mouth_y - mh_open, cx + mw * 0.55, mouth_y + mh_open], fill=(60, 20, 20, 255), outline=(0, 0, 0, 255))
        if mouth_open > 0.5:
            draw.ellipse([cx - mw * 0.25, mouth_y, cx + mw * 0.25, mouth_y + mh_open * 0.7], fill=(255, 100, 120, 255))
        if mouth_open > 0.7:
            draw.line(
                [(cx - mw * 0.5, mouth_y - mh_open * 0.45), (cx + mw * 0.5, mouth_y - mh_open * 0.45)],
                fill=(240, 240, 240, 255),
                width=max(1, int(mw * 0.04)),
            )
    return img


def get_mouth_events(audio_path: Path) -> list[dict]:
    """Return lip-sync cues. Try Rhubarb first, then audio RMS fallback."""
    try:
        cues = run_rhubarb(audio_path)
        print("    Lip-sync: Rhubarb OK")
        return cues
    except Exception as exc:
        print(f"    Lip-sync: Rhubarb failed ({exc}), using volume fallback")
        values = volume_based_mouth(audio_path, fps=FPS)
        return [{"start": i / FPS, "end": (i + 1) / FPS, "mouth": float(v)} for i, v in enumerate(values)]


# ---------------------------------------------------------------------------
# Motion clips
# ---------------------------------------------------------------------------


def make_ken_burns_clip(image_path: Path, duration: float, zoom: float = 0.08) -> ImageClip:
    pil_img = Image.open(image_path).convert("RGB")
    base_arr = np.array(pil_img)
    base = ImageClip(base_arr, duration=duration)

    def get_size(t: float) -> tuple[int, int]:
        s = 1.0 + zoom * (t / duration)
        return (int(RESOLUTION[0] * s), int(RESOLUTION[1] * s))

    clip = base.with_effects([vfx.Resize(get_size)])

    def get_pos(t: float) -> tuple[float, float]:
        w, h = get_size(t)
        dx = 20 * math.sin(t * 0.4)
        dy = 12 * math.cos(t * 0.3)
        return (RESOLUTION[0] / 2 - w / 2 + dx, RESOLUTION[1] / 2 - h / 2 + dy)

    clip = clip.with_position(get_pos)
    return clip


def make_character_clip(
    character_path: Path,
    audio_path: str,
    duration: float,
    base_x: int,
    base_y: int,
    scale: float,
    pose: str,
    scene_idx: int,
    prop_x: int | None,
) -> VideoClip:
    base_pil = Image.open(character_path).convert("RGBA")
    target_h = int(RESOLUTION[1] * scale)
    char_w = int(base_pil.width * target_h / base_pil.height)
    char_h = target_h
    base_pil = base_pil.resize((char_w, char_h), Image.LANCZOS)

    events = get_mouth_events(Path(audio_path)) if Path(audio_path).exists() else []
    n_frames = int(duration * FPS) + 3
    mouth_values = [mouth_open_at(i / FPS, events) for i in range(n_frames)]

    rng = random.Random(SEED + scene_idx)
    blink_times = [rng.uniform(0.6, 1.6) + i * 2.5 for i in range(int(duration / 2.5) + 2)]

    look_x = 0.5
    if prop_x is not None:
        look_x = 0.75 if prop_x > base_x else 0.25

    def make_frame(t: float) -> np.ndarray:
        idx = min(int(t * FPS), n_frames - 1)
        mouth_open = mouth_values[idx]
        blink = any(start <= t < start + 0.12 for start in blink_times)
        lx = look_x + 0.06 * math.sin(t * 3 + scene_idx)
        ly = 0.5 + 0.05 * math.cos(t * 2.5 + scene_idx)
        face = base_pil  # keep original mascot face; draw_face misaligns on this star mascot

        breath = 0.04 * math.sin(t * 2.5 + scene_idx)
        sx = 1.0 + breath
        sy = 1.0 - breath * 0.6
        rot = 0.0
        dy = 0.0

        if pose == "waving":
            rot = 5 * math.sin(t * 3)
        elif pose == "pointing":
            rot = 5 * (look_x - 0.5) + 2 * math.sin(t * 2)
        elif pose == "surprised":
            if t < 0.5:
                sy += 0.1 * abs(math.sin(t * 12)) * math.exp(-t * 3)
        elif pose == "thumbsup":
            dy = -3 * abs(math.sin(t * 4))

        # anticipation squash at scene start
        if t < 0.25:
            p = t / 0.25
            sy -= 0.06 * math.sin(p * math.pi)

        new_w = max(2, int(char_w * sx))
        new_h = max(2, int(char_h * sy))
        resized = face.resize((new_w, new_h), Image.LANCZOS)
        if abs(rot) > 0.1:
            transformed = resized.rotate(rot, expand=True, resample=Image.BICUBIC)
        else:
            transformed = resized

        tw, th = transformed.size
        canvas = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        bounce = 6 * math.sin(t * 4 + scene_idx)
        px = base_x - tw // 2
        py = int(base_y - th // 2 + bounce + dy)
        canvas.paste(transformed, (px, py), transformed)
        return np.array(canvas)

    clip = VideoClip(make_frame).with_duration(duration).with_fps(FPS)
    clip.size = RESOLUTION
    return clip


def make_prop_clip(
    prop_path: Path,
    duration: float,
    motion: str = "float",
    side: str = "right",
) -> ImageClip:
    pil_img = Image.open(prop_path).convert("RGBA")
    target_h = int(RESOLUTION[1] * 0.28)
    prop_w = int(pil_img.width * target_h / pil_img.height)
    prop_h = target_h
    pil_img = pil_img.resize((prop_w, prop_h), Image.LANCZOS)
    base = ImageClip(np.array(pil_img), duration=duration)

    def get_size(t: float) -> tuple[int, int]:
        s = 1.0 + 0.06 * math.sin(t * 3)
        return (int(prop_w * s), int(prop_h * s))

    base = base.with_effects([vfx.Resize(get_size)])

    if motion == "orbit":
        cx = RESOLUTION[0] * 0.75 if side == "right" else RESOLUTION[0] * 0.25
        cy = RESOLUTION[1] * 0.35
        r = 160

        def get_pos(t: float) -> tuple[float, float]:
            w, h = get_size(t)
            a = t * 1.2
            return (cx + r * math.cos(a) - w / 2, cy + r * 0.4 * math.sin(a) - h / 2)
    elif motion == "fly":
        start_x = 0 if side == "left" else RESOLUTION[0]
        end_x = RESOLUTION[0] if side == "left" else 0
        ctrl_x = RESOLUTION[0] / 2
        start_y = RESOLUTION[1] * 0.25
        end_y = RESOLUTION[1] * 0.25

        def get_pos(t: float) -> tuple[float, float]:
            u = t / duration if duration > 0 else 0
            u = max(0.0, min(1.0, u))
            # quadratic bezier
            x = (1 - u) * (1 - u) * start_x + 2 * (1 - u) * u * ctrl_x + u * u * end_x
            y = (1 - u) * (1 - u) * start_y + 2 * (1 - u) * u * (start_y - 80) + u * u * end_y
            w, h = get_size(t)
            return (x - w / 2, y - h / 2)
    else:

        def get_pos(t: float) -> tuple[float, float]:
            w, h = get_size(t)
            x = (RESOLUTION[0] * 0.78 if side == "right" else RESOLUTION[0] * 0.22) - w / 2 + 25 * math.sin(t * 0.8)
            y = RESOLUTION[1] * 0.25 - h / 2 + 20 * math.cos(t * 1.1)
            return (x, y)

    return base.with_position(get_pos)


class ParticleSystem:
    def __init__(self, theme: str, count: int = 30) -> None:
        self.theme = theme
        self.count = count
        self.particles: list[dict] = []
        rng = random.Random(SEED)
        for _ in range(count):
            p: dict = {
                "x": rng.randint(0, RESOLUTION[0]),
                "y": rng.randint(0, RESOLUTION[1]),
                "vx": rng.uniform(-15, 15),
                "vy": rng.uniform(-15, -3),
                "size": rng.randint(2, 7),
                "phase": rng.uniform(0, 2 * math.pi),
            }
            if theme == "fire":
                p["color"] = (255, rng.randint(80, 180), 0, 180)
                p["vy"] = rng.uniform(-30, -8)
                p["gravity"] = -10
            elif theme == "ocean":
                p["color"] = (200, 230, 255, 160)
                p["vy"] = rng.uniform(-12, -3)
                p["gravity"] = 0
            elif theme == "space":
                p["color"] = (255, 255, 220, 200)
                p["vy"] = rng.uniform(-5, 5)
                p["vx"] = rng.uniform(-2, 2)
                p["gravity"] = 0
            elif theme == "sky":
                p["color"] = (255, 255, 255, 140)
                p["vy"] = rng.uniform(-3, 3)
                p["vx"] = rng.uniform(-8, 8)
                p["gravity"] = 0
            else:
                p["color"] = (rng.randint(180, 255), rng.randint(180, 255), rng.randint(180, 255), 180)
                p["gravity"] = 0
            self.particles.append(p)

    def make_frame(self, t: float) -> np.ndarray:
        frame = np.zeros((RESOLUTION[1], RESOLUTION[0], 4), dtype=np.uint8)
        for p in self.particles:
            gy = p.get("gravity", 0) * t
            x = int(p["x"] + p["vx"] * t + 10 * math.sin(t + p["phase"]))
            y = int(p["y"] + p["vy"] * t + gy + 10 * math.cos(t + p["phase"]))
            x = x % RESOLUTION[0]
            y = y % RESOLUTION[1]
            cv2.circle(frame, (x, y), p["size"], p["color"], -1)
        return frame


def make_particle_clip(duration: float, theme: str) -> VideoClip:
    system = ParticleSystem(theme)
    clip = VideoClip(system.make_frame, duration=duration)
    clip.size = RESOLUTION
    return clip.with_fps(FPS)


# ---------------------------------------------------------------------------
# Scene layout
# ---------------------------------------------------------------------------


def scene_layout(i: int, total: int) -> dict:
    """Choose character horizontal position and scale for a scene."""
    layouts = [
        {"x_rel": 0.22, "scale": 0.46},
        {"x_rel": 0.78, "scale": 0.46},
        {"x_rel": 0.50, "scale": 0.50},
        {"x_rel": 0.28, "scale": 0.44},
        {"x_rel": 0.72, "scale": 0.44},
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
    out_path = output_dir / f"scene_v4_{idx:03d}.mp4"
    if out_path.exists():
        return str(out_path)
    duration = audio_duration(audio_path)

    bg_clip = make_ken_burns_clip(bg_path, duration, zoom=0.06)
    overlay_clip = ImageClip(np.array(Image.open(caption_path).convert("RGBA")), duration=duration)

    pil_char = Image.open(character_path).convert("RGBA")
    layout = scene_layout(idx, 18)
    target_h = int(RESOLUTION[1] * layout["scale"])
    char_w = int(pil_char.width * target_h / pil_char.height)
    char_h = target_h
    base_x = int(RESOLUTION[0] * layout["x_rel"])
    base_y = int(RESOLUTION[1] - char_h / 2 - 120)
    pose = scene_to_pose_name(scene)

    # prop target for eye tracking
    prop_x = None
    if prop_path:
        prop_x = int(RESOLUTION[0] * 0.78) if base_x < RESOLUTION[0] / 2 else int(RESOLUTION[0] * 0.22)

    prop_prompt, motion = scene_to_prop(scene)
    prop_clip = make_prop_clip(prop_path, duration, motion, side="right" if base_x < RESOLUTION[0] / 2 else "left") if prop_path else None

    p_words = _scene_words(scene)
    particle_theme = "default"
    if p_words & {"space", "moon", "planet", "star", "astronaut"}:
        particle_theme = "space"
    elif p_words & {"ocean", "water", "sea", "river", "lake", "underwater"}:
        particle_theme = "ocean"
    elif p_words & {"fire", "flame", "hot", "burn"}:
        particle_theme = "fire"
    elif p_words & {"sky", "cloud", "air", "atmosphere", "sun", "sunlight", "sunny", "blue"}:
        particle_theme = "sky"
    particle_clip = make_particle_clip(duration, particle_theme)

    character_clip = make_character_clip(
        character_path,
        audio_path,
        duration,
        base_x,
        base_y,
        layout["scale"],
        pose,
        idx,
        prop_x,
    )

    layers = [bg_clip]
    if prop_clip:
        layers.append(prop_clip)
    layers.append(particle_clip)
    layers.append(character_clip)
    layers.append(overlay_clip)

    composite = CompositeVideoClip(layers, size=RESOLUTION)
    composite = composite.with_fps(FPS)

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
        font_size=72,
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
        font_size=38,
        color=color,
        font=FONT_PATH,
        size=(1200, 100),
        text_align="center",
        duration=duration,
    )
    sub = sub.with_position((0, 440))

    composite = CompositeVideoClip([bg_clip, title, sub], size=RESOLUTION)
    composite = composite.with_fps(FPS)
    slug = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    out = Path("projects") / f"_tmp_title_{slug}_v4.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    composite.write_videofile(str(out), fps=FPS, codec="libx264", audio=False, threads=4, preset="ultrafast")
    composite.close()
    return str(out)


def _export_silent_mp3(duration_ms: int, out_path: Path) -> Path:
    AudioSegment.silent(duration=duration_ms).export(str(out_path), format="mp3")
    return out_path


def _sfx_at(start_s: float, out_path: Path, kind: str = "pop") -> AudioFileClip:
    if kind == "whoosh":
        generate_whoosh(out_path)
    elif kind == "chime":
        generate_chime(out_path)
    else:
        generate_sfx(out_path)
    return AudioFileClip(str(out_path)).with_start(start_s)


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"


def write_srt(
    scenes: list[dict],
    scene_audio_paths: list[str],
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    start = 0.0
    for i, (scene, audio) in enumerate(zip(scenes, scene_audio_paths)):
        dur = max(0.0, audio_duration(audio) - 0.3)
        lines.append(str(i + 1))
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(start + dur)}")
        lines.append(scene["text"])
        lines.append("")
        start += dur
    output.write_text("\n".join(lines), encoding="utf-8")


def write_storyboard(
    scenes: list[dict],
    character_poses: dict[str, Path],
    bg_paths: list[Path],
    prop_paths: list[Path | None],
    output: Path,
    title: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    board = {"title": title, "scenes": []}
    for i, scene in enumerate(scenes):
        pose = scene_to_pose_name(scene)
        prop_prompt, motion = scene_to_prop(scene)
        board["scenes"].append({
            "scene": i + 1,
            "title": scene["title"],
            "text": scene["text"],
            "pose": pose,
            "character": str(character_poses.get(pose, character_poses["neutral"])),
            "background": str(bg_paths[i]) if i < len(bg_paths) else "",
            "prop": str(prop_paths[i]) if i < len(prop_paths) and prop_paths[i] else "",
            "prop_motion": motion,
        })
    output.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")


def assemble_final(
    scene_paths: list[str],
    scene_audio_paths: list[str],
    scene_starts: list[float],
    scenes: list[dict],
    output: Path,
    output_dir: Path,
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

    for i, clip in enumerate(scene_clips):
        clip = clip.with_effects([vfx.FadeIn(0.4), vfx.FadeOut(0.4)])
        scene_clips[i] = clip

    all_video = [intro_clip] + scene_clips + [outro_clip]
    final_video = concatenate_videoclips(all_video, method="compose", padding=-0.3)

    print("[5/5] Mixing audio...")
    tmp_dir = output.parent / "_tmp_audio"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    voice_clips: list[AudioFileClip] = []
    intro_silence = _export_silent_mp3(int(intro_clip.duration * 1000), tmp_dir / "silence_intro.mp3")
    voice_clips.append(AudioFileClip(str(intro_silence)))
    for p in scene_audio_paths:
        voice_clips.append(AudioFileClip(p).with_effects([afx.AudioFadeIn(0.2), afx.AudioFadeOut(0.2)]))
    outro_silence = _export_silent_mp3(int(outro_clip.duration * 1000), tmp_dir / "silence_outro.mp3")
    voice_clips.append(AudioFileClip(str(outro_silence)))
    voice_track = concatenate_audioclips(voice_clips)

    music_path = tmp_dir / "bg_music.mp3"
    if music_path.exists():
        music_path.unlink()
    generate_music(int(final_video.duration * 1000) + 500, music_path)
    music = AudioFileClip(str(music_path)).subclipped(0, final_video.duration).with_volume_scaled(0.10)

    sfx_list: list[AudioFileClip] = []
    for start in scene_starts:
        kind = "chime" if random.random() > 0.7 else "pop"
        sfx_list.append(_sfx_at(start + intro_clip.duration, tmp_dir / f"sfx_{start:.2f}.mp3", kind=kind))

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

    # Extras
    write_srt(scenes, scene_audio_paths, output_dir / "subtitles.srt")

    for c in all_video:
        c.close()
    voice_track.close()
    music.close()
    for s in sfx_list:
        s.close()
    return output


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


async def main_async(project_dir_str: str = "examples/why-is-the-sky-blue") -> None:
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
        caption_path = assets_dir / f"caption_v4_{i:03d}.png"
        build_caption_overlay(scene, caption_path)
        prop_prompt, _ = scene_to_prop(scene)
        prop_path = generate_prop(prop_prompt, assets_dir, i) if prop_prompt else None

        audio_path = audio_dir / f"scene_v4_{i:03d}.mp3"
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
        current_start += audio_duration(scene_audio_paths[i]) - 0.3

    final_path = output_dir / "final_aumsum_v4.mp4"
    print("[Assemble] Creating final video...")
    assemble_final(scene_paths, scene_audio_paths, scene_starts, scenes, final_path, output_dir, project_title)
    print(f"Done: {final_path.resolve()}")

    write_storyboard(scenes, character_poses, bg_paths, prop_paths, output_dir / "storyboard.json", project_title)
    print(f"Storyboard: {(output_dir / 'storyboard.json').resolve()}")


if __name__ == "__main__":
    import sys

    project_dir_arg = sys.argv[1] if len(sys.argv) > 1 else "examples/why-is-the-sky-blue"
    asyncio.run(main_async(project_dir_arg))
