"""Blender VSE (Video Sequence Editor) automation wrapper.

This module drives Blender as an external process in headless mode. It does
**not** import `bpy` directly; instead it generates a temporary Blender Python
script + JSON config and invokes `blender -b -P script.py -- config.json`.

This makes the wrapper importable on machines that do not yet have Blender
installed and avoids needing a display/GPU.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


class BlenderNotFoundError(Exception):
    """Raised when the Blender executable cannot be located."""

    pass


class BlenderRenderError(Exception):
    """Raised when Blender exits with an error or the output is missing."""

    pass


class BlenderVideoEditor:
    """High-level controller for assembling and rendering video with Blender VSE."""

    def __init__(self, executable: Optional[str] = None, verbose: bool = False) -> None:
        self.executable = executable or self._find_executable()
        self.verbose = verbose

    @staticmethod
    def _find_executable() -> str:
        """Locate the Blender binary from env, PATH, or common install paths."""
        env = os.environ.get("BLENDER_EXECUTABLE")
        if env and Path(env).exists():
            return env

        names = ["blender", "blender.exe"]
        for name in names:
            path = shutil.which(name)
            if path:
                return path

        # Common Windows install paths; keep the list short and ordered.
        common = [
            r"C:\Users\Administrator\blender\blender-4.2.9-windows-x64\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/opt/blender/blender",
        ]
        for p in common:
            if Path(p).exists():
                return p

        raise BlenderNotFoundError(
            "Blender executable not found. Install Blender or set BLENDER_EXECUTABLE."
        )

    def _build_script(self) -> str:
        """Return the Blender Python script template that reads a JSON config."""
        return r'''import json
import os
import sys

import bpy


def main() -> None:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    if not argv:
        raise SystemExit("Usage: blender -b -P script.py -- config.json")

    with open(argv[0], "r", encoding="utf-8") as f:
        config = json.load(f)

    # Reset to a clean, empty scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # ------------------------------------------------------------------ #
    # Render settings
    # ------------------------------------------------------------------ #
    width, height = config.get("resolution", [1920, 1080])
    fps = config.get("fps", 30)
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.filepath = config["output"]
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = config.get("format", "MPEG4")
    scene.render.ffmpeg.codec = config.get("codec", "H264")
    scene.render.ffmpeg.audio_codec = config.get("audio_codec", "AAC")
    scene.render.ffmpeg.audio_bitrate = config.get("audio_bitrate", 192)

    scene.view_settings.view_transform = config.get("view_transform", "Standard")
    scene.view_settings.look = config.get("look", "None")

    # ------------------------------------------------------------------ #
    # Sequence editor setup
    # ------------------------------------------------------------------ #
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    sequences = scene.sequence_editor.sequences

    # ------------------------------------------------------------------ #
    # Video clips
    # ------------------------------------------------------------------ #
    clips = config.get("video_clips", [])
    transition_frames = max(0, int(config.get("transition_frames", 0)))
    current_frame = 1
    prev_strip = None
    channel = 1
    max_end = 1

    for i, clip in enumerate(clips):
        path = clip["path"]
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        start = current_frame - transition_frames if (prev_strip and transition_frames) else current_frame
        fit_method = clip.get("fit_method", "ORIGINAL")
        strip = sequences.new_movie(
            name=clip.get("name", f"Clip_{i}"),
            filepath=path,
            channel=channel,
            frame_start=start,
            fit_method=fit_method,
        )
        strip.frame_offset_start = int(clip.get("frame_offset_start", 0))
        strip.frame_offset_end = int(clip.get("frame_offset_end", 0))

        # Color correction modifier
        bright = float(clip.get("brightness", 0.0))
        contrast = float(clip.get("contrast", 0.0))
        if bright != 0.0 or contrast != 0.0:
            bc = strip.modifiers.new(name="BrightContrast", type="BRIGHT_CONTRAST")
            bc.bright = bright
            bc.contrast = contrast

        # Crossfade transition
        if prev_strip and transition_frames:
            sequences.new_effect(
                name=f"Cross_{i}",
                type="GAMMA_CROSS",
                channel=8,
                frame_start=start,
                frame_end=start + transition_frames,
                seq1=prev_strip,
                seq2=strip,
            )

        current_frame = start + (strip.frame_final_duration or 1)
        max_end = max(max_end, strip.frame_final_end)
        prev_strip = strip
        channel = 2 if channel == 1 else 1

    # ------------------------------------------------------------------ #
    # Audio clips (music, narration, sfx)
    # ------------------------------------------------------------------ #
    audio_tracks = [5, 6, 7]
    for idx, audio in enumerate(config.get("audio_clips", [])):
        path = audio["path"]
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        start_frame = int(audio.get("start_frame", 1))
        strip = sequences.new_sound(
            name=audio.get("name", f"Audio_{idx}"),
            filepath=path,
            channel=audio_tracks[idx % len(audio_tracks)],
            frame_start=start_frame,
        )

        if audio.get("fit_to_timeline") and max_end > 1:
            excess = int(strip.frame_final_end - max_end)
            if excess > 0:
                strip.frame_offset_end = excess

        volume = float(audio.get("volume", 1.0))
        if volume != 1.0:
            strip.volume = volume
            strip.keyframe_insert(data_path="volume", frame=start_frame)

    # ------------------------------------------------------------------ #
    # Text overlays
    # ------------------------------------------------------------------ #
    for overlay in config.get("text_overlays", []):
        text_content = overlay["text"]
        start = int(overlay.get("start_sec", 0) * fps) + 1
        end = start + int(overlay.get("duration_sec", 2) * fps)
        text = sequences.new_effect(
            name=text_content[:20],
            type="TEXT",
            channel=3,
            frame_start=start,
            frame_end=end,
        )
        text.text = text_content
        text.font_size = overlay.get("font_size", 80)
        r, g, b, a = overlay.get("color", [1.0, 1.0, 1.0, 1.0])
        text.color = (r, g, b, a)
        text.location = tuple(overlay.get("location", [0.5, 0.85]))
        text.align_x = overlay.get("align_x", "CENTER")
        text.align_y = overlay.get("align_y", "CENTER")
        text.use_shadow = overlay.get("use_shadow", True)

    # ------------------------------------------------------------------ #
    # Frame range and render
    # ------------------------------------------------------------------ #
    if sequences:
        scene.frame_start = 1
        scene.frame_end = max(s.frame_final_end for s in sequences)
    else:
        scene.frame_start = 1
        scene.frame_end = 1

    print(f"Rendering frames {scene.frame_start}..{scene.frame_end} to {scene.render.filepath}")
    bpy.ops.render.render(animation=True)
    print("Render complete")


if __name__ == "__main__":
    main()
'''

    def render(self, config: dict[str, Any], work_dir: Optional[str | Path] = None) -> Path:
        """Write a temporary script/config and run Blender headlessly.

        Returns the absolute output path. Raises BlenderRenderError on failure.
        """
        work_dir = Path(work_dir or tempfile.mkdtemp(prefix="blender_vse_"))
        work_dir.mkdir(parents=True, exist_ok=True)

        config_path = work_dir / "config.json"
        script_path = work_dir / "render.py"
        config["output"] = str(Path(config["output"]).resolve().as_posix())
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        script_path.write_text(self._build_script(), encoding="utf-8")

        cmd = [
            self.executable,
            "-b",
            "-P",
            str(script_path),
            "--",
            str(config_path),
        ]
        if self.verbose:
            print("Running:", " ".join(cmd), file=sys.stderr)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if self.verbose:
            print(result.stdout, file=sys.stderr)
            if result.returncode != 0:
                print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            raise BlenderRenderError(
                f"Blender failed with code {result.returncode}.\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        output = Path(config["output"])
        if not output.exists():
            # Blender may append frame numbers in some modes; check common variants.
            candidate = output.with_stem(f"{output.stem}0001-0001")
            if candidate.exists():
                output = candidate
            else:
                raise BlenderRenderError(
                    f"Output not found: {config['output']}\nSTDOUT:\n{result.stdout}"
                )

        return output.resolve()

    def assemble(
        self,
        video_paths: list[str | Path],
        output: str | Path,
        audio_clips: Optional[list[dict[str, Any]]] = None,
        text_overlays: Optional[list[dict[str, Any]]] = None,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30,
        transition_frames: int = 0,
    ) -> Path:
        """Convenience method: assemble videos + optional audio/text and render."""
        config: dict[str, Any] = {
            "resolution": list(resolution),
            "fps": fps,
            "transition_frames": transition_frames,
            "video_clips": [
                {"path": str(Path(p).resolve().as_posix()), "name": Path(p).stem}
                for p in video_paths
            ],
            "audio_clips": audio_clips or [],
            "text_overlays": text_overlays or [],
            "output": str(Path(output).resolve().as_posix()),
        }
        return self.render(config)
