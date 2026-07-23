"""Generate YouTube Shorts/TikTok thumbnails using a free image API.

Defaults to Pollinations (no API key required). Set `THUMBNAIL_IMAGE_URL` to use
another image-generation endpoint that accepts `?prompt=...&width=...&height=...`.
"""

from __future__ import annotations

import os
import textwrap
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


DEFAULT_API = "https://image.pollinations.ai/prompt"


def _load_font(size: int, font_path: str = "") -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(font_path, size)
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/Arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def _draw_text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int] = (255, 255, 255, 255),
    stroke: tuple[int, int, int, int] = (0, 0, 0, 255),
    box: tuple[int, int, int, int] = (0, 0, 0, 220),
    radius: int = 20,
    stroke_width: int = 3,
) -> None:
    """Draw text with a rounded translucent background box and stroke."""
    x, y = xy
    # Shadow/stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke)
    # Background box
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 24
    box_coords = (
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        bbox[2] + pad,
        bbox[3] + pad,
    )
    draw.rounded_rectangle(box_coords, radius=radius, fill=box)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def _build_prompt(base_prompt: str, style: str = "math-ai") -> str:
    """Return a prompt tuned for high-retention Shorts thumbnails."""
    style_boosts = {
        "math-ai": ", neon electric blue and purple colors, deep black background, holographic 3D matrix grid, neural network light rays, cinematic lighting, ultra sharp, high contrast, no text",
        "minimal": ", clean minimalist, bold color blocks, flat design, no text",
    }
    return f"{base_prompt}{style_boosts.get(style, '')}".strip()


def generate_thumbnail(
    prompt: str,
    title: str,
    output_path: str | Path,
    width: int = 1080,
    height: int = 1920,
    seed: int | None = 42,
    font_size: int = 110,
    font_path: str = "",
    image_url: str = "",
    style: str = "math-ai",
    title_y_ratio: float = 0.82,
) -> Path:
    """Generate a polished vertical thumbnail image and overlay text."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    image_url = image_url or os.environ.get("THUMBNAIL_IMAGE_URL", DEFAULT_API)
    final_prompt = _build_prompt(prompt, style=style)
    encoded_prompt = urllib.parse.quote(final_prompt)
    url = f"{image_url}/{encoded_prompt}?width={width}&height={height}"
    if seed is not None:
        url += f"&seed={seed}"
    if "pollinations" in url:
        url += "&nologo=true"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "image/*",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        img = Image.open(BytesIO(resp.read()))

    img = img.convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    font = _load_font(font_size, font_path=font_path)

    wrapped = textwrap.fill(title, width=16)
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = int(height * title_y_ratio) - th // 2

    _draw_text_box(draw, (x, y), wrapped, font)

    img.save(output, "PNG")
    return output


def generate_thumbnail_variants(
    prompt: str,
    title: str,
    output_dir: str | Path,
    width: int = 1080,
    height: int = 1920,
    seeds: list[int] | None = None,
) -> list[Path]:
    """Generate several thumbnail options for the user to pick from."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = seeds or [42, 123, 2025]
    paths: list[Path] = []
    for i, seed in enumerate(seeds, start=1):
        path = output_dir / f"thumbnail_v{i}.png"
        generate_thumbnail(
            prompt=prompt,
            title=title,
            output_path=path,
            width=width,
            height=height,
            seed=seed,
        )
        paths.append(path)
    return paths


def main() -> None:
    """CLI entrypoint for quick thumbnail generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate a vertical video thumbnail")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--title", required=True, help="Text overlay")
    parser.add_argument("--output", default="thumbnail.png", help="Output file path")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--font-size", type=int, default=110)
    parser.add_argument("--variants", action="store_true", help="Generate 3 variants")
    args = parser.parse_args()

    if args.variants:
        paths = generate_thumbnail_variants(
            prompt=args.prompt,
            title=args.title,
            output_dir=Path(args.output).parent or Path("."),
            width=args.width,
            height=args.height,
        )
        for p in paths:
            print(f"Saved thumbnail variant: {p}")
    else:
        path = generate_thumbnail(
            prompt=args.prompt,
            title=args.title,
            output_path=args.output,
            width=args.width,
            height=args.height,
            seed=args.seed,
            font_size=args.font_size,
        )
        print(f"Saved thumbnail: {path}")


if __name__ == "__main__":
    main()
