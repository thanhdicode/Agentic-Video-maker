# Space Architecture Short — Style Guide

## Color palette
- Background: `#05070A` (deep void black)
- Primary accent: `#00E5FF` (cyan — vectors, axes, span)
- Secondary: `#9D4EDD` (violet — j-hat, alternative concepts)
- Warm highlight: `#FFB800` (amber — target vectors, dimension numbers)
- Alert/wrong path: `#FF3B3B` (red — alternative basis contrast)
- Text: `#FFFFFF` (white) on dark backing

## Typography
- Vietnamese UI: **Arial Bold** at 30–72 pt
- Math formulas: `MathTex` default, 36–46 pt, white/cyan/amber
- Subtitle: Arial 30 pt, cyan, 2–4 words per line

## 3D conventions
- `ThreeDAxes` with low opacity gray axes.
- Basis vectors as `Arrow3D` with `thickness=0.03–0.05`.
- Important vectors: amber, 0.05 thickness.
- Planes / span: translucent `Polygon` fill (`fill_opacity=0.06`).
- Dots: `Dot3D` radius 0.04–0.08, cyan/white.

## Motion rules
- Camera moves are slow and purposeful (orbits, push-ins).
- Object-driven transitions: keep one anchor object (origin dot / basis vectors) across cuts.
- Avoid decoration-only motion; every animation explains a concept.
- Use `FadeIn`/`Create`/`GrowArrow`/`Transform`.

## Sound hierarchy
- Voice is primary, mixed at -22 LUFS.
- SFX accent key visual events (switch click, sweep snap, riser, pulse).
- Background music `bensound-softvibes.mp3` at ~12 % volume, ducked under voice.

## Scientific accuracy
- Coordinates represent scalars multiplying basis vectors.
- Span is the set of all linear combinations.
- Basis is a linearly independent spanning set.
- Dimension is the number of vectors in any basis.
