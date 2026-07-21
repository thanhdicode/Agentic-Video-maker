"""High-end Manim Shorts: a neural network forward pass as matrix math.

1080x1920 vertical, 30 fps, dark background, LaTeX formulas, linear transformations
(ApplyMatrix), ReLU fold, and a final bar-chart prediction.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import *

# ---------------------------------------------------------------------------
# Canvas config — vertical 1080x1920 Shorts, dark background, 30 fps
# ---------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0a0a0a"
config.frame_rate = 30

# ---------------------------------------------------------------------------
# Concrete tiny network used for the forward pass
# ---------------------------------------------------------------------------
INPUT = np.array([1.2, -0.8, 0.0])
W1 = np.array([[1.5, -1.0], [0.5, 1.2]])
b1 = np.array([0.5, -0.5])
z1 = W1 @ INPUT[:2] + b1
h1 = np.maximum(z1, 0.0)

W2 = np.array([[1.0, -0.5], [-0.5, 1.0]])
b2 = np.array([-0.2, 0.3])
y = W2 @ h1 + b2


def relu_func(p):
    return np.array([max(p[0], 0), max(p[1], 0), 0])


def softmax(arr):
    e = np.exp(arr - np.max(arr))
    return e / e.sum()


class NeuralNetMatrixMath(MovingCameraScene):
    def construct(self):
        config_path = Path(__file__).resolve().parent / "config.json"
        CONFIG = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        self.segments = CONFIG.get("segments", [])

        self._make_axes()
        self._make_grid()
        self._make_vectors()
        self.active_vec = self.x_vec

        for seg in self.segments:
            stype = seg["type"]
            dur = float(seg.get("duration", 4.0))
            getattr(self, f"_seg_{stype}")(seg, dur)

    # -----------------------------------------------------------------------
    # Scene setup
    # -----------------------------------------------------------------------
    def _make_axes(self):
        self.axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=5,
            y_length=5,
            axis_config={
                "include_tip": False,
                "include_numbers": False,
                "stroke_color": "#333333",
                "stroke_width": 1.2,
            },
        )

    def _make_grid(self):
        dots = []
        for i in np.linspace(-2.5, 2.5, 6):
            for j in np.linspace(-2.5, 2.5, 6):
                color = BLUE if (i + j) > 0 else RED
                dots.append(Dot(self.axes.coords_to_point(i, j), radius=0.04, color=color))
        self.grid = VGroup(*dots)

    def _make_vectors(self):
        self.x_vec = Vector(self.axes.coords_to_point(*INPUT[:2]) - self.axes.coords_to_point(0, 0),
                            color=YELLOW, buff=0)
        self.x_vec.set_stroke(width=5)

    def _vec_label(self, text, color=WHITE, direction=UR, buff=0.15):
        label = MathTex(text, color=color, font_size=30)
        label.add_updater(lambda m: m.next_to(self.active_vec.get_end(), direction, buff=buff))
        return label

    def _matrix_tex(self, name, matrix, color=WHITE):
        a, b, c, d = matrix.flatten()
        return MathTex(
            rf"{name} = \begin{{bmatrix}} {a:.1f} & {b:.1f} \\ {c:.1f} & {d:.1f} \end{{bmatrix}}",
            color=color,
            font_size=30,
        )

    # -----------------------------------------------------------------------
    # Segments
    # -----------------------------------------------------------------------
    def _seg_hook(self, seg, dur):
        title = Text("Every neural network is", font_size=48, color=WHITE, weight=BOLD)
        title2 = Text("just matrix multiplication.", font_size=48, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=1.2)
        title2.next_to(title, DOWN, buff=0.25)

        subtitle = Text("(a forward pass in 90 seconds)", font_size=28, color=GRAY)
        subtitle.next_to(title2, DOWN, buff=0.4)

        self.play(FadeIn(title), FadeIn(title2), FadeIn(subtitle), run_time=0.8)
        self.wait(max(0.8, dur - 0.8))
        self.play(FadeOut(title), FadeOut(title2), FadeOut(subtitle), run_time=0.5)

    def _seg_input(self, seg, dur):
        self.play(FadeIn(self.axes), FadeIn(self.grid), run_time=0.8)

        self.x_label = self._vec_label("x", color=YELLOW)
        self.play(GrowArrow(self.x_vec), FadeIn(self.x_label), run_time=1.0)

        desc = MathTex(r"x = \begin{bmatrix} 1.2 \\ -0.8 \end{bmatrix}", color=WHITE, font_size=28)
        desc.to_edge(RIGHT, buff=0.8)
        desc.shift(UP * 2)
        self.play(FadeIn(desc), run_time=0.6)

        self.wait(max(0.6, dur - 0.8 - 1.0 - 0.6))
        self.play(FadeOut(desc), run_time=0.3)

    def _seg_matrix_intro(self, seg, dur):
        # Show W matrix and basis vectors
        self.w_tex = self._matrix_tex("W", W1, color=BLUE)
        self.w_tex.to_edge(RIGHT, buff=0.6)
        self.w_tex.shift(UP * 1.5)
        self.play(FadeIn(self.w_tex), run_time=0.5)

        e1 = Vector(self.axes.coords_to_point(1, 0) - self.axes.coords_to_point(0, 0), color=BLUE, buff=0)
        e2 = Vector(self.axes.coords_to_point(0, 1) - self.axes.coords_to_point(0, 0), color=RED, buff=0)
        e1_label = MathTex(r"\hat i", color=BLUE, font_size=24).add_updater(
            lambda m: m.next_to(e1.get_end(), UR, buff=0.1)
        )
        e2_label = MathTex(r"\hat j", color=RED, font_size=24).add_updater(
            lambda m: m.next_to(e2.get_end(), UL, buff=0.1)
        )

        self.play(GrowArrow(e1), GrowArrow(e2), FadeIn(e1_label), FadeIn(e2_label), run_time=0.8)

        # Apply W to basis vectors; they land on the columns of W
        self.play(
            ApplyMatrix(W1, e1, run_time=1.4),
            ApplyMatrix(W1, e2, run_time=1.4),
            run_time=1.4,
        )

        col_labels = VGroup(
            MathTex("w_1", color=BLUE, font_size=24).add_updater(lambda m: m.next_to(e1.get_end(), UR, buff=0.1)),
            MathTex("w_2", color=RED, font_size=24).add_updater(lambda m: m.next_to(e2.get_end(), UL, buff=0.1)),
        )
        self.play(FadeTransform(e1_label, col_labels[0]), FadeTransform(e2_label, col_labels[1]), run_time=0.4)

        self.wait(max(0.5, dur - 0.5 - 0.8 - 1.4 - 0.4))

        self.basis_group = VGroup(e1, e2, col_labels[0], col_labels[1])

    def _seg_layer1(self, seg, dur):
        # Move label aside for the transform
        self.play(FadeOut(self.x_label), run_time=0.3)

        # The whole grid + input vector warp under W
        self.play(
            ApplyMatrix(W1, self.grid, run_time=1.8),
            ApplyMatrix(W1, self.x_vec, run_time=1.8),
            run_time=1.8,
        )

        # Create the W x label at the new tip
        self.active_vec = self.x_vec
        self.z_pre_label = self._vec_label("W x", color=BLUE)
        self.play(FadeIn(self.z_pre_label), run_time=0.4)

        self.wait(max(0.5, dur - 0.3 - 1.8 - 0.4))

    def _seg_bias(self, seg, dur):
        # W x + b = z
        z_point = self.axes.coords_to_point(*z1) - self.axes.coords_to_point(0, 0)
        self.z_vec = Vector(z_point, color=ORANGE, buff=0)
        self.z_vec.set_stroke(width=5)

        self.play(
            ReplacementTransform(self.x_vec, self.z_vec),
            FadeOut(self.z_pre_label),
            run_time=1.0,
        )
        self.active_vec = self.z_vec

        self.b_tex = MathTex(
            r"b = \begin{bmatrix} 0.5 \\ -0.5 \end{bmatrix}",
            color=GRAY,
            font_size=28,
        )
        self.b_tex.to_edge(RIGHT, buff=0.8)
        self.b_tex.shift(UP * 0.5)
        self.play(FadeIn(self.b_tex), run_time=0.4)

        self.z_label = self._vec_label("z = W x + b", color=ORANGE)
        self.play(FadeIn(self.z_label), run_time=0.4)

        self.eq = MathTex("z = W x + b", color=WHITE, font_size=34)
        self.eq.to_edge(UP, buff=1.0)
        self.play(Write(self.eq), run_time=0.6)

        self.wait(max(0.5, dur - 1.0 - 0.4 - 0.4 - 0.6))

    def _seg_relu(self, seg, dur):
        # Show ReLU graph and fold the vector
        self.play(FadeOut(self.z_label), run_time=0.3)

        # A small ReLU graph on the right
        self.relu_axes = Axes(
            x_range=[-3, 4, 1],
            y_range=[-1, 4, 1],
            x_length=2.8,
            y_length=2.0,
            axis_config={"include_tip": False, "include_numbers": False, "stroke_color": "#555555"},
        )
        self.relu_axes.to_edge(RIGHT, buff=0.7)
        self.relu_axes.shift(DOWN * 1.5)
        self.relu_graph = self.relu_axes.plot(lambda x: max(0, x), x_range=[-3, 4, 0.1], color=GREEN)
        self.relu_label = MathTex(r"\text{ReLU}(z) = \max(0,z)", color=GREEN, font_size=24)
        self.relu_label.next_to(self.relu_axes, UP, buff=0.2)

        self.play(FadeIn(self.relu_axes), Create(self.relu_graph), FadeIn(self.relu_label), run_time=0.8)

        # Animate the vector tip dropping its negative coordinate to zero
        h_point = self.axes.coords_to_point(*h1) - self.axes.coords_to_point(0, 0)
        self.h_vec = Vector(h_point, color=GREEN, buff=0)
        self.h_vec.set_stroke(width=5)

        # Intermediate step: drop y to 0, then clip x if needed (x is positive, so no change)
        mid_point = self.axes.coords_to_point(z1[0], 0) - self.axes.coords_to_point(0, 0)
        z_to_axis = Vector(mid_point, color=ORANGE, buff=0)

        self.play(ReplacementTransform(self.z_vec, z_to_axis), run_time=0.7)
        self.play(ReplacementTransform(z_to_axis, self.h_vec), run_time=0.7)
        self.active_vec = self.h_vec

        self.h_label = self._vec_label("h = ReLU(z)", color=GREEN)
        self.play(FadeIn(self.h_label), run_time=0.4)

        self.wait(max(0.5, dur - 0.3 - 0.8 - 0.7 - 0.7 - 0.4))

    def _seg_layer2(self, seg, dur):
        self.play(FadeOut(self.h_label), run_time=0.3)

        # V matrix appears
        self.v_tex = self._matrix_tex("V", W2, color=PURPLE)
        self.v_tex.to_edge(RIGHT, buff=0.6)
        self.v_tex.shift(UP * 1.5)
        self.play(FadeIn(self.v_tex), run_time=0.5)

        # Apply V to h vector
        self.play(ApplyMatrix(W2, self.h_vec, run_time=1.6), run_time=1.6)

        # Add bias b2 -> y
        y_point = self.axes.coords_to_point(*y) - self.axes.coords_to_point(0, 0)
        self.y_vec = Vector(y_point, color=PURPLE, buff=0)
        self.y_vec.set_stroke(width=5)

        self.play(ReplacementTransform(self.h_vec, self.y_vec), run_time=0.8)
        self.active_vec = self.y_vec

        self.y_label = self._vec_label("y = V h + b_2", color=PURPLE)
        self.play(FadeIn(self.y_label), run_time=0.4)

        self.wait(max(0.5, dur - 0.3 - 0.5 - 1.6 - 0.8 - 0.4))

    def _seg_output(self, seg, dur):
        # Move to output space: a bar chart of scores
        to_fade = [
            self.grid,
            self.axes,
            self.basis_group,
            self.w_tex,
            self.b_tex,
            self.v_tex,
            self.y_label,
            self.y_vec,
            self.eq,
            self.relu_axes,
            self.relu_graph,
            self.relu_label,
            self.h_label,
        ]
        self.play(*[FadeOut(m) for m in to_fade], run_time=0.6)

        # Softmax probabilities for positive bars
        probs = softmax(y)
        chart = BarChart(
            values=[0, 0],
            y_range=[0, 1, 0.25],
            x_length=5,
            y_length=5,
            bar_names=["A", "B"],
            bar_colors=[GRAY, GRAY],
        )
        chart.move_to(ORIGIN)
        chart.get_y_axis().set_opacity(0)

        title = MathTex(r"\text{output scores } y", color=WHITE, font_size=34)
        title.to_edge(UP, buff=1.0)

        self.play(Create(chart), FadeIn(title), run_time=0.6)

        # Animate bars up to softmax probabilities
        self.play(chart.animate.change_bar_values(probs.tolist()), run_time=1.2)

        # Highlight the winning class
        winner = np.argmax(y)
        bars = chart.bars
        bars[winner].set_color(YELLOW)
        self.play(Indicate(bars[winner], scale_factor=1.2), run_time=0.6)

        pred = MathTex(r"\text{prediction} = \arg\max(y) = " + ("A" if winner == 0 else "B"), color=YELLOW, font_size=34)
        pred.next_to(chart, DOWN, buff=0.6)
        self.play(Write(pred), run_time=0.6)

        self.wait(max(0.5, dur - 0.6 - 0.6 - 1.2 - 0.6 - 0.6))

    def _seg_learning(self, seg, dur):
        # Pull back to full equations
        self.play(
            *[FadeOut(m) for m in self.mobjects if m is not None],
            run_time=0.5,
        )

        eq1 = MathTex(r"h = \text{ReLU}(W x + b)", color=WHITE, font_size=38)
        eq2 = MathTex(r"y = V h + b_2", color=WHITE, font_size=38)
        eq3 = MathTex(r"\text{prediction} = \arg\max(y)", color=WHITE, font_size=38)
        eqs = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.6)
        eqs.move_to(ORIGIN)

        self.play(Write(eq1), run_time=0.7)
        self.play(Write(eq2), run_time=0.7)
        self.play(Write(eq3), run_time=0.7)

        box = SurroundingRectangle(eqs, color=YELLOW, buff=0.3, corner_radius=0.1)
        note = Text("Adjust W, V, b during training to improve predictions.", font_size=30, color=GRAY)
        note.next_to(box, DOWN, buff=0.4)

        self.play(Create(box), FadeIn(note), run_time=0.6)
        self.wait(max(0.6, dur - 0.5 - 0.7 * 3 - 0.6))

    def _seg_cta(self, seg, dur):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.4)

        cta = Text("Follow for the math behind AI", font_size=48, color=WHITE, weight=BOLD)
        handle = Text("@MathInMotion", font_size=28, color=GRAY)
        cta.to_edge(UP, buff=1.5)
        handle.next_to(cta, DOWN, buff=0.3)
        self.play(FadeIn(cta), FadeIn(handle), run_time=0.6)
        self.wait(max(0.8, dur - 0.6))
        self.play(FadeOut(cta), FadeOut(handle), run_time=0.4)
