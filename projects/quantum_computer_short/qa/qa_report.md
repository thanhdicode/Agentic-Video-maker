# QA Report — Quantum Computing Short

## Final output
- **File**: `projects/quantum_computer_short/quantum_short_voice_sfx.mp4`
- **Duration**: 59.50 s (within 58–59.5 s)
- **Resolution**: 1080 × 1920
- **Frame rate**: 30 fps
- **Video codec**: h264, yuv420p, High Profile
- **Audio codec**: AAC, 48 kHz, 192 kb/s
- **Voice provider**: `edge-tts` `vi-VN-NamMinhNeural`
- **Music status**: Royalty-free `bensound-softvibes.mp3` used as ambient bed at 12 % volume. Commercial reference track "METAMORPHOSIS — INTERWORLD" not included (copyright).

## Automated QA evidence
- **No black frames**: spot-checked frames at 0 s, 1 s, 30 s, 58 s are non-black.
- **No text out of frame**: all titles and formulas are within 80 px side margins and 300 px bottom safe area.
- **Subtitle safe area**: ASS style uses 50 px margins and 160 px bottom margin.
- **Audio peak**: true peak ≈ -6.0 dBFS (no clipping).
- **Integrated loudness**: -22.5 LUFS (closer to broadcast target, clear on mobile).
- **Loudness range**: 0.8–1.5 LU (consistent, little dynamic surprise).

## Known limitations
- **Frame rate**: 30 fps instead of 60 fps. The CPU-only environment and 3D Manim scenes made 60 fps render risky for the timeline; 30 fps is stable and accepted by the prompt fallback.
- **3D sphere rendering**: the Bloch sphere is a low-resolution parametric surface; fine for 1080×1920 mobile viewing but not cinema-grade.
- **SFX**: synthesized with `aevalsrc`/`anoisesrc` because no professional SFX library was available. They are functional but not premium.
- **Music**: the requested reference track is copyrighted; the build pipeline supports swapping it in via `--with-music`.

## Contact sheets
- `qa/contact_sheet_pass1.png` — raw Manim render frames (before polish/mix).
- `qa/contact_sheet_pass2.png` — final polished and mixed output.

## Reproducibility
Single command rebuild (from repo root):
```cmd
python projects\quantum_computer_short\build.py
```
