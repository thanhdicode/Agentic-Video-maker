# Manim Math / AI Shorts — Viral Pattern Research (v2)

Goal: understand why top math + AI Shorts keep viewers, then copy the most powerful patterns into our 1–2 min vertical Shorts.

## 1. Top reference videos (Manim / 3Blue1Brown style)

| # | Video / Source | Why it works |
|---|----------------|--------------|
| 1 | 3Blue1Brown — *But what is a neural network?* (23.7M) | Clean 3D-ish layered network, weights as edges light up, one concept per shot |
| 2 | 3Blue1Brown — *Large Language Models explained briefly* (6.9M) | Tokens turn into vectors, arrows show information flow, voice is calm but precise |
| 3 | 3Blue1Brown — *Attention in transformers, visually explained* | Softmax heatmap, Q/K/V geometry, camera rotates around attention grid |
| 4 | 3Blue1Brown TikTok/Shorts — *Newton's fractal*, *Fourier series*, *Where matrix multiplication comes from* | Strong first-frame hook, fast payoff, text-on-screen |
| 5 | CodeMatrixVishal — *Sine Wave Animation Using Unit Circle* (26K) | Neon color, unit-circle-to-sine morph, 14s pure visual loop |
| 6 | STEM in Motion — *The Most Beautiful Equation of Mathematics* (435K) | 3Blue1Brown-style pacing, dramatic reveal (Euler's identity) |
| 7 | Pascal's triangle Short (N0aTOcHaZd8) | Grid builds itself, rule appears visually, no clutter |
| 8 | Pravnsh — *The Animated Transformer* (article) | Step-by-step Q/K/V with code & diagrams, good 90s Shorts structure |
| 9 | LLManim examples (attention, embeddings, full forward pass) | Pre-built components (TokenBox, VectorBar, SoftmaxCurve) for fast professional scenes |
| 10 | Transformer_explorer (GitHub) | 3D multi-head attention, residual/FFN/SwiGLU animations, storyboard-driven |

## 2. Common viral patterns (Shorts/TikTok, 1–2 min)

### A. Hook in the first 1–3 seconds
- Start with a surprising claim / question / number. Example: "Every neural network is just multiplying matrices."
- No intro, no "hi", no logo. Visual + voice start immediately.
- Education Shorts average 35–45% swipe-away by second 3; top creators get it below 20%.

### B. One idea per 5–10 second beat
- Each beat = one sentence of narration + one visual action.
- Avoid paragraphs of text. One formula, one vector, one matrix per shot.

### C. Visual continuity with motion
- Use `Transform`, `ApplyMatrix`, `MoveAlongPath`, `ReplacementTransform`, not fade-in/fade-out slideshows.
- Show the *same* object morphing: vector x → W x → z → ReLU(z) → h. This makes the math feel alive.

### D. Camera moves (2.5D / 3D)
- `ThreeDScene` + `set_camera_orientation` + `move_camera` + `begin_ambient_camera_rotation`.
- For 2D, `MovingCameraScene` `camera.frame.animate.scale/move` adds depth without full 3D.
- Rotate around the object, dolly in/out, reveal the next step from a new angle.

### E. Color as meaning
- Each matrix/variable has a single color and stays consistent: W=blue, b=gray, z=orange, h=green, V=purple, y=purple.
- Use dark background (`#0a0a0a`) so glowing vectors pop.

### F. Sound design
- Voice: `edge-tts` `en-US-AvaNeural` or `en-US-GuyNeural` at 1.05–1.15x speed for energy.
- Music: quiet lo-fi/ambient bed, 15–20% volume, no lyrics.
- Sync every narration word to the animation; use per-segment timing (`config.json` + ffprobe).

### G. Text and subtitles
- Burn in ASS subtitles with clear white font + black outline.
- Keep formulas large, no overlapping, use `BackgroundRectangle` behind floating labels.
- Don't show more than 2 text objects in the same screen zone.

### H. End with payoff
- Close with a clear takeaway or "aha" moment: "That's all a forward pass is."
- Add a subtle CTA ("follow for more") in the last 2 seconds.

## 3. Technical best-practice checklist

- Resolution: 1080×1920, 30 fps, H.264 + AAC.
- Render engine: `ThreeDScene` or `MovingCameraScene` for camera moves.
- Use `add_fixed_in_frame_mobjects` / `add_fixed_orientation_mobjects` for labels in 3D.
- Math: `MathTex` with TinyTeX; keep font size ≥24, use `add_background_rectangle`.
- Build pipeline: `script.md` → `edge-tts` → `config.json` timings → Manim → `ffmpeg` mix + subtitle burn.
- Avoid `ReplacementTransform` between objects with different structures; prefer `.animate.put_start_and_end_on` for vectors.
- Test each segment in `-pqh` 1080×1920 at least once; use `-pql` for rapid iteration.

## 4. 3D Shorts formula (1–2 min)

1. **0–3s**: one-liner hook + 3D object appears.
2. **3–20s**: show the data/vectors entering the operation (e.g. tokens → embeddings).
3. **20–50s**: run the core math visually (matrix × vector, attention softmax, ReLU).
4. **50–80s**: reveal the result and why it matters.
5. **80–100s**: recap + final line + subscribe/follow CTA.

## 5. Tools to use / install

- `manim==0.20.1` (already installed).
- `edge-tts` for free AI voice.
- `TinyTeX` for LaTeX / `MathTex`.
- `ffmpeg` with libass for subtitle burn.
- Optional: `llmanim` for reusable Transformer components.
- Optional: `kokoro` or `f5-tts` for higher-quality voice (free, local).
