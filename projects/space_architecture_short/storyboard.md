# Space Architecture Short — Storyboard

## Global rules
- Canvas: 1080 × 1920, 30 fps (CPU fallback), H.264 yuv420p.
- Background: near-black `#05070A` with a faint cyan grid at z = -6 (very low opacity).
- Continuity motif: cyan basis vectors / arrows recur in every scene.
- Typography: `Arial` for Vietnamese, `MathTex` for `\hat{\imath}`, `\hat{\jmath}`, `\hat{k}`, `\vec{v}`, `R^n`.
- Safe area: 80 px sides, 120 px top, 300 px bottom reserved for Shorts UI.

---

## SCENE 1 — Hook (0.00–~12.3 s)
### Voice
"Mỗi con số sống trong một không gian. Không gian đó xây từ đâu?"

### Visuals
- 0.00–1.5: 2D axes fade in; a white dot appears at origin.
- 1.5–3.5: Title `KIẾN TRÚC\nTOÁN HỌC\nKHÔNG GIAN` scales in with dark backing.
- 3.5–7.0: Subtitle slides up from bottom.
- 7.0–12.3: A cyan arrow grows from origin, hinting at the vector theme.

### Camera
Slow push-in toward the origin dot, then settle.

### Sound
- 0.0: Bass impact.
- 1.0: Digital snap on title.
- 6.0: Math pulse as arrow appears.

---

## SCENE 2 — Origin and vector (~12.3–~22.7 s)
### Voice
"Đầu tiên là một điểm gốc. Từ đó, một vector bước ra."

### Visuals
- Dot `O` at origin with label.
- Cyan arrow `\vec{v}` grows from origin to (2.2, 1.2, 0).
- Label `\vec{v}` appears at tip.

### Camera
Gentle zoom focusing on the arrow tip.

### Sound
- 12.3: Whoosh snap.
- 17.0: Math pulse.

---

## SCENE 3 — Basis and coordinates (~22.7–~37.1 s)
### Voice
"x, y không phải vị trí. Chúng là cách kéo giãn i-hát và j-hát."

### Visuals
- Unit arrows `\hat{\imath}` (cyan, x) and `\hat{\jmath}` (violet, y).
- Scale `\hat{\imath}` by 3, `\hat{\jmath}` by 2.
- Show parallelogram and final vector `\vec{v} = 3\hat{\imath} + 2\hat{\jmath}`.

### Camera
Slight orbit to keep the parallelogram readable.

### Sound
- 23.0: Switch click on basis reveal.
- 28.0: Math pulse on vector equation.

---

## SCENE 4 — Linear combination / span (~37.1–~54.4 s)
### Voice
"Cộng hai vector đã scale: tổ hợp tuyến tính. Mọi điểm đạt được gọi là span."

### Visuals
- Grid of dots fades in, representing all reachable linear combinations.
- Translucent cyan plane overlay fills the 2D space.
- Big `SPAN` title with subtitle.

### Camera
Pull back slightly to show the infinite plane.

### Sound
- 37.0: Riser / ambient lift.
- 41.0: Sweep snap as plane reveals.

---

## SCENE 5 — Alternative basis (~54.4–~72.2 s)
### Voice
"i-hát, j-hát là một bộ cơ sở. Cặp vector khác vẫn xây được cùng mặt phẳng."

### Visuals
- Standard basis i, j and target vector `\vec{v}`.
- Transform to alternative basis `\vec{u}` and `\vec{w}` (red).
- Show new parallelogram reaching the same `\vec{v}`.
- Equation `\vec{v} = 2.5\vec{u} - 0.5\vec{w}`.

### Camera
Orbit 15 degrees to expose the new basis.

### Sound
- 55.0: Switch click.
- 62.0: Math pulse on alternative equation.

---

## SCENE 6 — Dimension (~72.2–~86.6 s)
### Voice
"Số vector tối thiểu cần thiết là số chiều. Thêm k-hát, không gian thành 3D."

### Visuals
- 3D axes with `\hat{\imath}`, `\hat{\jmath}`, `\hat{k}`.
- A white vector built from the three basis arrows.
- Counter animates `1 → 2 → 3` as dimensions expand.

### Camera
Swing to `phi=60°, theta=-45°` to reveal 3D depth.

### Sound
- 73.0: Riser.
- 78.0: Sweep snap as k-hat appears.

---

## SCENE 7 — Higher dimensions / AI data (~86.6–~98.1 s)
### Voice
"Không dừng ở 3D. Dữ liệu AI sống trong hàng trăm chiều."

### Visuals
- Abstract radial axes (8 directions).
- Bar chart of 12 feature values (feature vector).
- Text `R^n` and `100+ chiều`.
- A red data dot moves through the space.

### Camera
Pull back to a flat, dashboard-style 2.5D view.

### Sound
- 87.0: Math pulse.
- 92.0: Tone hit as `R^n` appears.

---

## SCENE 8 — Outro (~98.1–~113.2 s)
### Voice
"Đó là kiến trúc không gian. Hiểu nó, bạn thấy toán học ở khắp nơi."

### Visuals
- Chain `ĐIỂM → VECTOR → CƠ SỞ → SỐ CHIỀU`.
- Central title `KIẾN TRÚC\nKHÔNG GIAN`.
- Subtitle / CTA at bottom.
- Background 3D axes rotate slowly.

### Camera
Slow continuous orbit for loop feel.

### Sound
- 99.0: Riser.
- 108.0: Digital snap on CTA.
