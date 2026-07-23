# QA Report — Space Architecture Short

## Pipeline summary
- **Scene file**: `space_architecture.py`
- **Build file**: `build.py`
- **Final deliverable**: `space_architecture_voice_sfx.mp4`
- **Voice**: `edge-tts` `vi-VN-NamMinhNeural`
- **Music**: `assets/music/bensound-softvibes.mp3`
- **SFX**: generated with `aevalsrc`/`anoisesrc`/sine, aligned to cue sheet.

## Checks performed

### 1. Video container & resolution
```
ffprobe -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt
```
- **Width**: 1080
- **Height**: 1920
- **Frame rate**: 30/1
- **Codec**: h264
- **Pixel format**: yuv420p
- **Duration**: 85.87 s

### 2. Audio stream
```
ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,duration
```
- **Codec**: aac
- **Sample rate**: 48000 Hz
- **Duration**: 85.87 s (trimmed to video with `-shortest`)

### 3. Integrated loudness (EBU R128)
```
ffmpeg -i final.mp4 -af ebur128=peak=true -f null -
```
- **Integrated loudness**: -22.3 LUFS
- **True peak**: -2.4 dBTP
- **Status**: clear and audible on mobile devices.

### 4. Visual collision / subtitle check
- Rendered checkpoints at 2 s, 25 s, 40 s, 60 s, 80 s, 85 s.
- Title, math labels, and subtitles are readable and not cut off.
- Final CTA and summary chain fit within the frame.

### 5. Contact sheet
- `qa/contact_sheet_pass2.png` generated from evenly spaced frames.
- Visual style consistent: deep black background, cyan/violet/amber accents, fixed-frame labels.

### 6. Deliverables
- `space_architecture_voice_sfx.mp4` — final polished 1080×1920 vertical Short (85.87 s).
- `space_architecture_thumbnail.png` — 1280×720 thumbnail.
- `qa/contact_sheet_pass2.png` — visual contact sheet.
- `subtitles.ass` — Vietnamese subtitle source.

## Notes
- Post-processing applied: contrast +10 %, saturation +10 %, brightness +0.02, curves, sharpen, vignette, CRF 17.
- 3D camera uses `phi=55°, theta=-60°` start and per-segment orbits.
- All HUD text uses `add_fixed_in_frame_mobjects` / `add_fixed_orientation_mobjects` so it always faces the viewer.
- TTS outputs are normalized to real MP3 (24000 Hz, mono) before concatenation to avoid the WAV/MP3 concat bug.
