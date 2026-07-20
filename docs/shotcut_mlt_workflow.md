# Shotcut / MLT Headless Editing Workflow

Shotcut bundles `melt.exe`, the MLT command-line renderer. It can assemble
clips, add cross-fades, and mix audio without a GPU, making it a fast
CPU-only final-edit backend for the AI Video Studio pipeline.

## Install

1. Download the Shotcut portable zip for Windows:
   https://www.shotcut.org/download/
2. Extract to a known folder, e.g. `C:\shotcut\Shotcut`.
3. `melt.exe` is inside that folder.

On Linux/macOS install `melt` through the Shotcut or MLT package.

## Pipeline usage

```cmd
set SHOTCUT_MELT=C:\shotcut\Shotcut\melt.exe
set AI_VIDEO_USE_SHOTCUT=1
python -m agents.orchestrator --idea "Game launch trailer"
```

## Manual usage

```python
from tools.shotcut_edit import ShotcutEditor

editor = ShotcutEditor()
editor.assemble(
    video_paths=["clip1.mp4", "clip2.mp4", "clip3.mp4"],
    output="trailer.mp4",
    audio_clips=[
        {"path": "narration.mp3", "volume": 1.0, "fit_to_timeline": False},
        {"path": "music.mp3", "volume": 0.3, "fit_to_timeline": True},
    ],
    resolution=(1280, 720),
    fps=30,
    transition_frames=15,  # 0.5s cross-fade at 30fps
)
```

## Strengths and limits

- **Strengths:** fast, CPU-only, simple XML/CLI pipeline, easy cross-fades,
  multi-track audio mixing.
- **Limits:** text overlays and advanced grading require hand-written MLT XML
  or a GUI pass in Shotcut; for full text/color control use the Blender or
  FFmpeg backends.

## MLT references

- MLT command line: https://www.mltframework.org/docs/melt/
- MLT XML: https://www.mltframework.org/docs/mltxml/
