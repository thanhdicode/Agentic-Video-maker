"""Manim rendering helpers for automated educational videos.

Writes a Python scene file from a sequence of segments and renders it with the
``manim`` CLI. Each segment is shown as a text slide, optionally paired with a
generic colored shape, for the length of its narration.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


class ManimError(Exception):
    """Raised when Manim cannot be found or render a scene."""

    pass


def _find_manim() -> str:
    env = os.environ.get("MANIM_EXECUTABLE")
    if env and Path(env).exists():
        return env

    found = shutil.which("manim")
    if found:
        return found

    raise ManimError(
        "manim executable not found. Install manim: https://docs.manim.community"
    )


TEMPLATE = '''\
from manim import *

class {class_name}(Scene):
    def construct(self):
        background = FullScreenRectangle(color=BLACK)
        self.add(background)

        # Palette of cheerful colors for shapes/accents
        colors = [BLUE, GREEN, YELLOW, ORANGE, PURPLE, TEAL]

        {segments_code}

        # Hold final frame briefly
        self.wait(0.5)
'''


def _build_segments(segments: list[dict[str, Any]]) -> str:
    """Generate Manim Python code that shows one slide per segment."""
    lines: list[str] = []

    for i, seg in enumerate(segments):
        text = seg.get("visual_text", seg.get("narration", "")).replace('"', '\\"')
        duration = max(float(seg.get("duration", 3.0)), 1.0)
        color = f"colors[{i % 6}]"

        # A small colored shape in the center, with text below it.
        lines.append(f"""
        # Segment {i + 1}
        shape = Circle(radius=1.2, color={color}, fill_opacity=0.3)
        label = Text(\"{text}\", font_size=44, color=WHITE)
        label.next_to(shape, DOWN, buff=0.6)
        group = VGroup(shape, label)
        self.play(FadeIn(group, shift=UP*0.3), run_time=0.6)
        self.wait({duration - 0.9:.2f})
        self.play(FadeOut(group, shift=DOWN*0.3), run_time=0.3)
""")

    return "\n".join(lines)


def write_scene_file(
    segments: list[dict[str, Any]],
    output: str | Path,
    class_name: str = "AutoEduScene",
) -> Path:
    """Write a ``.py`` Manim scene file from a slide list.

    Args:
        segments: Each item must contain at least ``narration``; ``visual_text``,
                  ``duration`` and ``duration`` are optional.
        output: Destination ``.py`` path.
        class_name: Name of the scene class.
    """
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    segments_code = _build_segments(segments)
    source = TEMPLATE.format(class_name=class_name, segments_code=segments_code)
    out_path.write_text(source, encoding="utf-8")
    return out_path


def predict_output_path(scene_file: str | Path, class_name: str, quality_flag: str) -> Path:
    """Return the MP4 path Manim will create for a given scene/quality flag."""
    scene_file = Path(scene_file)
    # Map common flags to the directory names Manim uses for fps.
    dir_map = {"l": "480p15", "m": "720p30", "h": "1080p60", "p": "1440p60", "k": "2160p60"}
    quality_dir = dir_map.get(quality_flag, "480p15")
    # Manim output structure: <scene_dir>/media/videos/<stem>/<quality>/<ClassName>.mp4
    return (
        scene_file.parent
        / "media"
        / "videos"
        / scene_file.stem
        / quality_dir
        / f"{class_name}.mp4"
    )


def render_scene(
    scene_file: str | Path,
    class_name: str,
    quality: str = "l",
) -> Path:
    """Render a Manim scene file and return the produced MP4 path.

    ``quality`` is passed to ``manim -q`` and should be one of ``l/m/h/p/k``.
    """
    scene_file = Path(scene_file)
    exe = _find_manim()
    cmd = [
        exe,
        "-q",
        quality,
        "--disable_caching",
        "-o",
        class_name,
        str(scene_file),
        class_name,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(scene_file.parent))
    if result.returncode != 0:
        raise ManimError(
            f"manim render failed: {result.stderr}\n{result.stdout}"
        )

    expected = predict_output_path(scene_file, class_name, quality)
    if not expected.exists():
        # Some versions put output under the file directory; search for it.
        candidates = list(scene_file.parent.rglob(f"{class_name}.mp4"))
        if not candidates:
            raise ManimError("Manim did not produce an output MP4")
        return candidates[0].resolve()

    return expected.resolve()


def render_from_script(
    segments: list[dict[str, Any]],
    scene_file: str | Path,
    class_name: str = "AutoEduScene",
    quality: str = "l",
) -> Path:
    """Convenience: write a scene file from ``segments`` and render it."""
    write_scene_file(segments, scene_file, class_name=class_name)
    return render_scene(scene_file, class_name, quality=quality)
