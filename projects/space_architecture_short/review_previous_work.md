# Review of Previous Manim Work

## What worked in earlier shorts
1. **Vertical 9:16 canvas** at 1080×1920 is correct for Shorts/TikTok.
2. **Dark cinematic palette** (deep black + cyan/violet) keeps focus on the math.
3. **Edge-tts Vietnamese voice** with burned-in ASS subtitles is usable and fast.
4. **Post-processing** (contrast +10 %, saturation +10 %, sharpen, vignette, CRF 17) makes the flat Manim render feel more premium.
5. **Segment-based `build.py`** pipeline (TTS → config → Manim → SFX → mix) is reproducible.

## Common issues found in earlier shorts
1. **Audio concatenation bug**: `synth:silence` is not valid for FFmpeg concat; must generate real silence mp3 files.
2. **Audio loudness**: first mixes were too quiet (-26 LUFS); final mix now boosted to -22 LUFS with `volume=1.5`.
3. **Text overlapping**: math labels and subtitles occasionally collided with 3D objects; now use `_add_fixed` for HUD text and safe margins.
4. **Camera moves too timid**: earlier shorts were mostly static; this short adds slow orbits and push-ins.
5. **SFX timing drift**: timeline must align with actual narration durations, not hard-coded 60s.
6. **30 fps is acceptable** on CPU but every frame must be visually rich to avoid choppiness.
7. **Narration too long**: previous 2m+ scripts caused bloated videos; this script is tighter, aiming for ~1m45s–2m.

## 10 fixes applied in this short
1. Hook in first 2 seconds: question + title + first arrow.
2. Each scene has one clear visual verb (fade in, grow, transform, orbit).
3. Continuity motif: cyan axes/basis vectors appear in every scene.
4. Sound design: bass impact, switch clicks, sweeps, risers mapped to storyboard beats.
5. No decoration-only motion; every animation carries meaning.
6. 3D camera orbits and zooms for spatial concepts.
7. Post-processing preserved and baked into the build pipeline.
8. Subtitle safe area enforced (160 px bottom margin, 2–4 word chunks).
9. Math labels are fixed in frame and backed with dark rectangles.
10. Single surprising claim: "AI data lives in 100+ dimensions" bridges math to modern tech.
