# AumSum Style Guide — AI Video Studio

Reference videos:
- https://www.youtube.com/watch?v=op4C2TypclE — "A Transparent Ocean: What If?"
- https://www.youtube.com/watch?v=K9e7dNdoyQo — "What if Social Networks Disappeared?"

## 1. Visual identity

- **Character**: AumSum — a friendly, round-headed figure with a turquoise/cyan body, peach skin face, simple black stick limbs, black eyes and a wide smile. Often shown waving, pointing, or with a curious expression.
- **Style**: 2D vector/flat cartoon with thick black outlines, bright saturated colors, simple shading.
- **Backgrounds**: Clean gradients (sky blue, ocean blue, green). Minimal detail; focus on the character and one or two props.
- **Props**: Simplified icons (submarine, fish, laptop, social media symbols, coral, treasure chest).
- **Text**: Large, bold, rounded sans-serif; yellow highlights for key words; white with dark outline or black shadow; placed at top-left or top-center.
- **Composition**: Character slightly off-center; main prop on the opposite side; title at top; caption at bottom in a rounded dark box.
- **Thumbnail style**: Character + oversized prop + bold question at top; bright palette.

## 2. Audio identity

- **Narrator**: Curious, energetic, kid-friendly English voice; moderate pace.
- **Music**: Upbeat background loop; louder during hook/outro, quieter during explanation.
- **SFX**: Light "pop" when objects appear, "ding" for fun facts, short transitions.

## 3. Pacing and structure

| Part | Duration | Purpose |
|------|----------|---------|
| Hook | 3–5 s | Ask an absurd "What if" question with character on screen |
| Fact 1 | 5–7 s | First consequence with a clear prop/label |
| Fact 2 | 5–7 s | Second consequence, contrasting visuals |
| Fact 3 | 5–7 s | Third consequence, often a twist or downside |
| Outro | 3–5 s | Reassuring/funny closer, character waves |

## 4. Agent rules for AumSum-style generation

1. Always open with the exact "What if" question as the title card.
2. Keep the AumSum character on screen for at least 80% of the video.
3. Use one key prop per fact; label the prop with large text.
4. Highlight the most important word in yellow.
5. Use a cheerful, inquisitive narration tone.
6. Add a short upbeat music loop and light SFX on prop appearances.
7. Keep total runtime under 60 seconds for compilations, under 90 seconds for standalone.

## 5. Sample project

See `projects/aumsum-transparent-ocean/`:
- `project.yaml` — production profile and style palette
- `script.md` — 5-scene "What if Oceans were Transparent?" script
- `output/final_aumsum.mp4` — CPU-rendered prototype

This sample can be used as a template for new AumSum-style videos.

## 6. Production notes

- The CPU prototype uses vector-style shapes from Pillow + MoviePy. It proves the pipeline but is not final quality.
- Final quality requires GPU generation of the character, props, and backgrounds (FLUX + ComfyUI + Wan/LTX) or a rigged 2D puppet in Blender/Motion Canvas.
- The character should be converted into a reusable asset (character sheet → LoRA/IP-Adapter → layered puppet) to maintain consistency across videos.
