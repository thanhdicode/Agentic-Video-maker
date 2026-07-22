# Viral Manim Math Shorts — Research & Pattern Library

Goal: build Shorts/TikToks that look as polished as 3Blue1Brown / Mathematical Visual Proofs and are engineered for retention + monetization.

## Top 10 reference examples

1. **Monge's Theorem** — 3Blue1Brown, ~2.4M views.
   - Pattern: geometry puzzle → surprising claim → 3D step-out → payoff.
   - Duration: ~59s. Strong hook: "here's a fun geometry puzzle with a very surprising solution".

2. **Six Trigs in 60 Seconds!** — Mathematical Visual Proofs, ~820K views.
   - Pattern: one static diagram, labels appear one by one, each trig function is a *length* on the unit circle.
   - Hook: "six trig functions in one picture". Clean color-coded lines + formula.

3. **Summing Powers of Three** — Mathematical Visual Proofs, visual proof of geometric series.
   - Pattern: build fractal/triangle tiling, show identity visually, no heavy algebra.

4. **"Perfection in imperfection" | 100K+ frames** — golden-ratio/geometry art.
   - Pattern: aesthetic/motion-heavy, no narration, relies on music + visual loop.

5. **Sine Wave Animation Using Unit Circle** — codematrixvishal, 26K views.
   - Pattern: unit circle → projection onto y-axis → sine graph, short and neon-styled.

6. **Limit Using Stirling's Approximation** — quick calculus derivation, hashtag-heavy.

7. **Pascal's triangle** — "each number equals the sum of the two above" — micro-lesson.

8. **Fourier Series — drawing with circles** — 3Blue1Brown main video.
   - The most iconic "complex concept made visual" example; the Shorts cut focuses on the epicycle reveal.

9. **"The essence of calculus"** — 3Blue1Brown long-form.
   - Shorts version: area of a circle by unwrapping rings → triangle.

10. **The Manim Experience / 3b1b workflow** — behind-the-scenes, 3.1M views.
    - Proves that polished programmatic animation itself is content.

## Why they work (retention & algorithm)

- **Hook in first 1.5s.** Viewer swipe-away on study Shorts peaks at 1-3s. Hook is either a question, a surprising visual, or a famous result.
- **One concept, one payoff.** 30-60s. No tangents. The payoff answers the hook.
- **Visual proof over algebra.** The audience sees *why*, not just *what*. Manim's power is animation, not slide text.
- **Color-coded, clean, high contrast.** Dark background, bright colored axes/functions, big labels.
- **LaTeX formulas as hero moments.** A big formula reveal with `Write` / `TransformMatchingTex`.
- **Pacing: fast cuts + pauses on the key frame.** Let the final result sit for 1-2s so the brain captures it.
- **Audio:** clear AI narration + low background music + burned English subs for sound-off viewing.
- **CTA / pattern interrupt at end.** "Follow for more math magic" or "The answer is X — don't let it fool you".

## Production checklist for a viral Manim Short

1. **Pick a surprising, visual, famous result.**
   - Visual proofs (Pythagorean, area of circle, sum of odd numbers = square)
   - Famous identities (Euler's identity, Fourier series, trig identities)
   - Counter-intuitive facts (Moser's circle, Banach-Tarski, Gabriel's horn)

2. **Script 60s max.**
   - 0-3s hook question
   - 3-10s setup/context
   - 10-45s step-by-step animation with narration synced to motion
   - 45-55s payoff + formula reveal
   - 55-60s CTA

3. **Manim techniques to maximize impact**
   - `MathTex` / `Tex` for clean formulas (LaTeX required).
   - `Axes`, `FunctionGraph`, `NumberPlane` for graphs.
   - `ValueTracker` + `always_redraw` for dynamic functions.
   - `TransformMatchingTex`, `ReplacementTransform`, `FadeTransform` for formula transitions.
   - `Write`, `Create`, `Indicate`, `Circumscribe`, `Flash` for emphasis.
   - `TracedPath`, `MoveAlongPath`, `ShowPassingFlash` for motion trails.
   - `ThreeDAxes`, `Dot3D`, `Surface` for 3D concepts.
   - Color palette: axes x=red, y=green, z=blue; highlight accent yellow.

4. **Audio**
   - `edge-tts` free voices: `en-US-AvaNeural` / `en-US-GuyNeural`.
   - Mix narration at 0 dB, background music at -18 to -22 dB.
   - Burn English ASS subtitles, bottom-center, white + black outline.

5. **Export**
   - 1080x1920 vertical, 30 fps, H.264 + AAC.
   - Title cards use `add_fixed_in_frame_mobjects` for 3D scenes; for 2D just `to_edge`.
