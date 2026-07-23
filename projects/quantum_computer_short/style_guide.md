# Quantum Computing Short — Style Guide

## Color palette
- **Background**: `#05070A` (near-black).
- **Primary energy**: `#00E5FF` (cyan).
- **Secondary / phase**: `#9D4EDD` (violet).
- **Misconception / wrong path**: `#FF3B3B` (red), used sparingly.
- **Classical / bit**: `#FFFFFF` (white).
- **Text backing box**: `#000000` at 70 % opacity.
- **Grid/nebula layer**: `#00E5FF` / `#9D4EDD` at 3–6 % opacity.

## Typography
- **Vietnamese text**: `Arial` bold, size 32–110 depending on role.
- **Titles**: 90–110 px, white, with black backing box.
- **Subtitles (burn-in)**: 28 px Arial, white with black outline/stroke.
- **Math notation**: `MathTex` with `font_size=40–48`, color white.
- **Safe area**: keep text within 80 px sides, 120 px top, 300 px bottom.

## Motion language
- **Easing**: default `rate_func=smooth` for camera, `rate_func=exponential` for impacts.
- **Transitions**: object-driven; a shared particle or wire must bridge scenes.
- **Camera moves**: every move has a purpose: reveal, focus, scale, follow, transition.
- **No idle orbit**: orbit only to explain an axis or rotation.
- **Meaningful visual change**: at least one every 1.5–2.5 seconds.

## 3D objects
- **Bloch sphere**: wireframe latitude/longitude, translucent surface, state vector as bright arrow.
- **Bit cube**: solid white/cyan cube with a visible switch.
- **Quantum circuit wire**: horizontal cyan line, gates as labeled boxes or icons.
- **Amplitude bars**: flat colored bars with labels, no 3D unnecessary depth.
- **Interference waves**: `ParametricFunction` with `ValueTracker` for phase and amplitude.

## Glow and particles
- Glow is a `VGroup` of slightly larger, low-opacity copies behind a bright object.
- Particles encode data: bit digits (0/1), amplitude paths, photon trail.
- No random decoration particles; every particle is a state, path, or label.

## Sound hierarchy
1. Voice (always loudest, never clipped).
2. Key SFX (gate pulses, measurement snaps, interference hit).
3. Background ambience/risers.
4. Music (ducked under voice).

## Scientific accuracy rules
- Qubit is a vector in a 2D complex space, not a coin that is both heads and tails.
- Measurement yields only `0` or `1`; the wave components are not two separate answers.
- Entanglement is correlation of measurement outcomes, not faster-than-light messaging.
- Interference changes amplitudes via phase, not probability directly.
- The final output is always classical.

## Deliverable naming
- `quantum_short_voice_sfx.mp4` — narration + SFX + ambient bed.
- `quantum_short_reference_music_mix.mp4` — if a commercial track is provided and licensed.
- `quantum_short_thumbnail_frame.png` — final frame or chosen thumbnail.
- `qa/contact_sheet_pass1.png` and `qa/contact_sheet_pass2.png` — frame contact sheets.
