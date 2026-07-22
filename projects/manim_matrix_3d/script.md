# Matrix Multiplication in 3D — Manim Shorts script

## Goal
Show that matrix multiplication is just composing 3D linear transformations, which is the core math behind neural networks. Vertical 1080×1920, 30 fps, ~75 s.

## Segments

### 01_hook (0:00-0:07)
**Narration:** "What is matrix multiplication? It is composing transformations in three dimensions."
**Visual:** Title text + a small 3D cube rotating in the center.

### 02_input (0:07-0:15)
**Narration:** "Start with a vector, or a whole cube. Every point has three coordinates: x, y, and z."
**Visual:** Fade to 3D axes, unit cube, and basis vectors i-hat, j-hat, k-hat.

### 03_matrix_intro (0:15-0:25)
**Narration:** "A three by three matrix is a transformation of space. Each column tells you where one of the basis vectors lands."
**Visual:** Show matrix W on the right; highlight the three columns and the matching basis vectors.

### 04_W1 (0:25-0:32)
**Narration:** "First matrix W1 rotates and stretches the cube."
**Visual:** Apply W1 to cube and basis vectors. W1 formula stays on the right.

### 05_W2 (0:32-0:39)
**Narration:** "Second matrix W2 performs another rotation."
**Visual:** Apply W2 to the already transformed cube.

### 06_composition (0:39-0:50)
**Narration:** "Multiplying W2 by W1 means applying both in one shot. One new matrix M gives the same final result."
**Visual:** Reset to the original cube, then apply M = W2 W1. Show the product matrix.

### 07_basis_columns (0:50-0:59)
**Narration:** "Each column of the product is W2 acting on a column of W1. That is why matrix multiplication is defined the way it is."
**Visual:** Zoom around the transformed cube and show the columns of M as arrows.

### 08_neural_net (0:59-1:07)
**Narration:** "A neural network does exactly this: every layer is a matrix, and the output is one big composition."
**Visual:** Replace the cube with a layered network of matrix blocks W1, W2, Wn and arrows.

### 09_recap (1:07-1:14)
**Narration:** "So matrix multiplication is the math that turns simple steps into deep learning."
**Visual:** Final equation y equals W_n dot dot dot W_2 W_1 x.

### 10_cta (1:14-1:17)
**Narration:** "Follow for more visual math."
**Visual:** CTA text.
