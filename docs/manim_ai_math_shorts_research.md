# Top Manim CS / AI / Matrix Shorts — Research & Pattern Library

Goal: make 1-2 minute vertical Shorts that explain the math inside computers / AI, using the strongest Manim features.

## Top 10 reference examples

1. **But what is a neural network?** — 3Blue1Brown (17M views).
   - Pattern: start with MNIST digit recognition, build intuition neuron-by-neuron, visual weight connections, activation squish, layers as computations.
   - Why it works: one concrete example (handwritten digits), each visual element answers a question before it is asked.

2. **Gradient descent, how neural networks learn** — 3Blue1Brown (9.4M views).
   - Pattern: cost function surface → rolling ball downhill → negative gradient step. Strong geometric metaphor.

3. **Backpropagation, intuitively** — 3Blue1Brown (6.1M views).
   - Pattern: nudges on weights, chain rule as influence propagation, color-coded paths.

4. **Attention in transformers, step-by-step** — 3Blue1Brown (4.3M views).
   - Pattern: embedding space, query-key-value as vectors, attention pattern as a heatmap, matrix products.
   - The Shorts cut: single attention head with clean matrix multiply visualization.

5. **Eigenvectors and eigenvalues | Essence of linear algebra** — 3Blue1Brown (5M+ views).
   - Pattern: matrix as space warp, special vectors that only stretch, equation `A v = λ v`, tied to real applications.

6. **Neural Networks Explained from Scratch using Python** — Bot Academy (389K views).
   - Pattern: matrix multiplication and bias terms animated, code synchronized with visuals.

7. **Cannon's & Fox's Matrix Multiplication Algorithms** — bhavik-goplani (YouTube Shorts).
   - Pattern: colored blocks moving between processors, distributed matrix multiply as a physical dance.

8. **2D Rotation Matrix Animation** — YouTube Shorts (C7SWSGRaPpU).
   - Pattern: fast, neon, single matrix transforms the whole plane, no voice, beat-driven.

9. **LLManim: Transformer / LLM visual components** — rishabhbhartiya GitHub.
   - Pattern: reusable Manim components for attention, feed-forward blocks, token flow.

10. **Linear Algebra for ML [Animated]** — Augusto Gonzalez-Bonorino / Medium.
    - Pattern: matrices as data, determinants, SVD/eigenvectors for compression/face recognition.

## Why they go viral

- **Concrete example first.** "How a neural network reads a digit" beats "Definition of a neural network".
- **One equation, one action.** Show a matrix, then immediately apply it to a point or a grid.
- **Space is a character.** Matrix = transformation of the plane. ReLU = fold. Attention = query-key dot products.
- **Pacing: show, don't pause.** Each segment is 3-10s; pauses only on the payoff frame.
- **Color semantics.** Red = negative/erased, green/blue = active/positive, yellow = result.
- **Burned subs + music.** Many Shorts are watched muted; clear bottom subtitles are essential.
- **CTA at the high point.** "Follow for the math behind AI" over the final clean result.

## Manim features to maximize for CS/AI Shorts

- `ApplyMatrix` / `ApplyPointwiseFunction` — animate the whole plane or a vector under a matrix.
- `Vector`, `NumberPlane`, `Axes` — geometry of linear algebra.
- `Matrix` / `DecimalMatrix` / `MathTex` — show the actual numbers and formulas.
- `ReplacementTransform` / `TransformMatchingTex` — morph equations step by step.
- `Indicate`, `Circumscribe`, `SurroundingRectangle`, `Flash` — draw the eye.
- `MovingCameraScene` — zoom in on a neuron/vector, then pull back to the full network.
- `FunctionGraph` — ReLU, sigmoid, cost function, softmax.
- `BarChart` / `Rectangle` — class probabilities, loss values.
- `ValueTracker` + `always_redraw` — dynamic graphs and counters.

## Production checklist for a 60-120s AI-math Short

1. **Pick one concrete AI task.** Digit recognition, spam detection, face compression, recommendation.
2. **Script 60-120s.**
   - 0-5s hook (surprising claim or question)
   - 5-20s setup (input data as vector)
   - 20-80s step-by-step math (matrix → bias → activation → matrix → output)
   - 80-95s payoff (the network decides)
   - 95-110s CTA
3. **Animate math, not slides.** Every matrix operation is shown acting on a vector or a grid.
4. **Voice + audio.** edge-tts `en-US-AvaNeural`/`en-US-GuyNeural`; background music at -18 to -22 dB; burned English subs.
5. **Export:** 1080×1920, 30fps, H.264/AAC.
