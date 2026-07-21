# Neural Networks are Matrix Multiplication — 1-2 min Manim Shorts

Target: 1080x1920 vertical, 30 fps, ~66s (final render with edge-tts).
Topic: a single forward pass of a tiny neural network, visualized as matrix warps + ReLU fold + output scores.

## Segments

1. **hook** (≈8.6s)
   - Visual: title "Every neural network is just matrix multiplication."
   - Audio: "Every neural network, from ChatGPT to your photo app, is just matrix multiplication hidden behind a few simple tricks."

2. **input** (≈8.0s)
   - Visual: axes + one input vector `x` in 2D, with `x = [1.2, -0.8]^T` on the right.
   - Audio: "An input is a vector of numbers. It could be pixels from an image, words turned into embeddings, or sensor readings."

3. **matrix_intro** (≈6.7s)
   - Visual: `W` matrix and basis vectors `i-hat`, `j-hat` moving to columns of `W`.
   - Audio: "A matrix is a transformation of space. Each column tells you where a basis vector lands after the warp."

4. **layer1** (≈6.8s)
   - Visual: `ApplyMatrix` on the grid and on `x`; the whole plane stretches and rotates.
   - Audio: "Multiplying the input by W warps it into a new space where patterns become easier to separate."

5. **bias** (≈5.3s)
   - Visual: shift the resulting vector by bias `b`; show `z = W x + b`.
   - Audio: "A bias vector shifts that space so the network does not have to pass through the origin."

6. **relu** (≈8.5s)
   - Visual: ReLU graph; the vector folds so negative coordinates become zero. Show `h = ReLU(z)`.
   - Audio: "Then ReLU clips negative values to zero. This simple fold is the nonlinearity that lets the network bend straight lines."

7. **layer2** (≈6.2s)
   - Visual: matrix `V` transforms the hidden vector into output scores. Show `y = V h + b_2`.
   - Audio: "Another matrix maps the hidden state into output scores, one number for each possible class."

8. **output** (≈5.4s)
   - Visual: bar chart of two scores, highlight the larger one, show predicted class A.
   - Audio: "The biggest score wins. The network picks the class it is most confident about."

9. **learning** (≈6.7s)
   - Visual: full equations `h = ReLU(W x + b)` and `y = V h + b_2` boxed; text about training.
   - Audio: "During training, small nudges to every weight and bias make the predictions better, layer after layer."

10. **cta** (≈2.4s)
    - Visual: "Follow for the math behind AI".
    - Audio: "Follow for the math behind AI."
