"""3D Manim scene: matrix multiplication is composing linear transformations.

Vertical 1080x1920 Shorts, dark background, camera moves, and clear
fixed-in-frame labels. Each segment duration is read from config.json.
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
config.background_color = "#111111"
config.frame_rate = 30


# Two example 3x3 matrices whose composition looks interesting in 3D.
W1 = np.array(
    [
        [1.0, 0.5, -0.3],
        [0.2, 1.2, 0.4],
        [-0.1, 0.3, 0.9],
    ]
)
W2 = np.array(
    [
        [0.8, -0.2, 0.3],
        [0.4, 1.1, -0.2],
        [-0.2, 0.1, 1.0],
    ]
)
M = W2 @ W1

AXIS_X = RED
AXIS_Y = GREEN
AXIS_Z = BLUE
CUBE_COLOR = BLUE
BASIS_I = RED
BASIS_J = GREEN
BASIS_K = GOLD


def _matrix_tex(name: str, mat: np.ndarray, color: str = WHITE) -> VGroup:
    """Return a fixed-in-frame matrix group with a background."""
    entries = [[f"{v:.1f}" for v in row] for row in mat]
    matrix_mob = Matrix(entries, h_buff=1.1, v_buff=0.75).scale(0.58)
    # Slightly tint each column to match basis colors
    for i, col_color in enumerate([BASIS_I, BASIS_J, BASIS_K]):
        for entry in matrix_mob.get_entries()[i::3]:
            entry.set_color(col_color)
    name_tex = MathTex(name, color=color, font_size=26)
    name_tex.next_to(matrix_mob, LEFT, buff=0.25)
    group = VGroup(name_tex, matrix_mob)
    bg = BackgroundRectangle(group, color=BLACK, fill_opacity=0.85, buff=0.15)
    return VGroup(bg, group)


class Matrix3DComposition(ThreeDScene):
    def construct(self):
        config_path = Path(__file__).resolve().parent / "config.json"
        CONFIG = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        self.segments = CONFIG.get("segments", [])

        self._build_axes()
        self._build_cube()
        self._build_basis()

        for seg in self.segments:
            stype = seg["type"]
            dur = float(seg.get("duration", 3.0))
            getattr(self, f"_seg_{stype}")(seg, dur)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _build_axes(self):
        self.axes = ThreeDAxes(
            x_range=(-4, 4, 1),
            y_range=(-4, 4, 1),
            z_range=(-4, 4, 1),
            x_length=6,
            y_length=6,
            z_length=6,
            axis_config={
                "include_tip": True,
                "tip_width": 0.2,
                "tip_height": 0.2,
                "include_numbers": False,
                "color": GRAY,
            },
        )
        x_label = MathTex("x", color=AXIS_X, font_size=30)
        y_label = MathTex("y", color=AXIS_Y, font_size=30)
        z_label = MathTex("z", color=AXIS_Z, font_size=30)
        self.axis_labels = self.axes.get_axis_labels(x_label, y_label, z_label)

    def _build_cube(self):
        self.cube = Cube(
            side_length=1.5,
            fill_color=CUBE_COLOR,
            fill_opacity=0.18,
            stroke_color=CUBE_COLOR,
            stroke_width=2,
        )

    def _build_basis(self):
        # Vectors from the origin
        self.i_vec = Vector(np.array([2, 0, 0]), color=BASIS_I, buff=0)
        self.j_vec = Vector(np.array([0, 2, 0]), color=BASIS_J, buff=0)
        self.k_vec = Vector(np.array([0, 0, 2]), color=BASIS_K, buff=0)
        self.i_vec.set_stroke(width=4)
        self.j_vec.set_stroke(width=4)
        self.k_vec.set_stroke(width=4)

        # Labels that always face the camera and follow the vector tips
        self.i_label = MathTex(r"\hat i", color=BASIS_I, font_size=26)
        self.j_label = MathTex(r"\hat j", color=BASIS_J, font_size=26)
        self.k_label = MathTex(r"\hat k", color=BASIS_K, font_size=26)
        for lab in (self.i_label, self.j_label, self.k_label):
            lab.add_background_rectangle(color=BLACK, opacity=0.75)
            self.add_fixed_orientation_mobjects(lab)

        def _label_pos(tip, extra=UP * 0.7):
            norm = np.linalg.norm(tip)
            if norm > 0.01:
                return tip + extra + (tip / norm) * 1.7
            return tip + extra

        self.i_label.add_updater(lambda m: m.move_to(_label_pos(self.i_vec.get_end())))
        self.j_label.add_updater(lambda m: m.move_to(_label_pos(self.j_vec.get_end())))
        self.k_label.add_updater(lambda m: m.move_to(_label_pos(self.k_vec.get_end())))

    def _add_matrix_label(self, name: str, mat: np.ndarray, color: str = WHITE):
        tex = _matrix_tex(name, mat, color)
        tex.to_edge(RIGHT, buff=0.35)
        tex.shift(UP * 2.8)
        self.add_fixed_in_frame_mobjects(tex)
        return tex

    def _matrix_title(self, name: str, color: str = WHITE) -> VGroup:
        title = Text(f"{name} = transformation of space", font_size=32, color=color, weight=BOLD)
        title.to_edge(UP, buff=0.9)
        title.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(title)
        return title

    # -----------------------------------------------------------------------
    # Segments
    # -----------------------------------------------------------------------
    def _seg_hook(self, seg, dur):
        title = Text("What is matrix\nmultiplication?", font_size=44, color=WHITE, weight=BOLD, line_spacing=0.4)
        subtitle = Text("Composing 3D transformations", font_size=34, color=YELLOW)
        title.to_edge(UP, buff=1.0)
        subtitle.next_to(title, DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.9)

        # A small rotating cube in the center
        preview = self.cube.copy()
        preview.scale(0.6)
        self.add(preview)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=0.8)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(max(0.5, dur - 0.8 - 0.4))
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(preview), run_time=0.4)

    def _seg_input(self, seg, dur):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-70 * DEGREES, zoom=0.9)

        # Bring in axes, grid, cube and basis vectors
        self.play(
            Create(self.axes),
            FadeIn(self.axis_labels),
            FadeIn(self.cube),
            GrowArrow(self.i_vec),
            GrowArrow(self.j_vec),
            GrowArrow(self.k_vec),
            run_time=1.2,
        )

        # Smooth camera move to reveal the 3D setup
        self.move_camera(phi=65 * DEGREES, theta=-50 * DEGREES, run_time=1.5, rate_func=smooth)

        wait = max(0.2, dur - 1.2 - 1.5)
        if wait > 0:
            self.wait(wait)

    def _seg_matrix_intro(self, seg, dur):
        title = self._matrix_title("matrix", WHITE)
        self.play(FadeIn(title), run_time=0.6)

        # Generic W matrix placeholder
        w_tex = _matrix_tex("W", W1, BLUE)
        w_tex.to_edge(RIGHT, buff=0.35)
        w_tex.shift(UP * 2.8)
        self.add_fixed_in_frame_mobjects(w_tex)
        self.play(FadeIn(w_tex), run_time=0.6)

        wait = max(0.3, dur - 0.6 - 0.6)
        if wait > 0:
            self.wait(wait)

        self.play(FadeOut(title), FadeOut(w_tex), run_time=0.3)

    def _seg_W1(self, seg, dur):
        self.w1_tex = self._add_matrix_label("W_1", W1, BLUE)
        self.play(FadeIn(self.w1_tex), run_time=0.5)

        # Apply W1 to cube and basis vectors
        self.play(
            ApplyMatrix(W1, self.cube, run_time=1.8),
            ApplyMatrix(W1, self.i_vec, run_time=1.8),
            ApplyMatrix(W1, self.j_vec, run_time=1.8),
            ApplyMatrix(W1, self.k_vec, run_time=1.8),
            run_time=1.8,
        )

        # Camera follows the action
        self.move_camera(phi=60 * DEGREES, theta=-30 * DEGREES, run_time=1.0, rate_func=smooth)

        wait = max(0.3, dur - 0.5 - 1.8 - 1.0)
        if wait > 0:
            self.wait(wait)

    def _seg_W2(self, seg, dur):
        self.w2_tex = self._add_matrix_label("W_2", W2, PURPLE)
        # Shift W2 below W1
        self.w2_tex.to_edge(RIGHT, buff=0.35)
        self.w2_tex.shift(UP * 1.1)
        self.play(FadeIn(self.w2_tex), run_time=0.5)

        # Apply W2 to already transformed cube and basis vectors
        self.play(
            ApplyMatrix(W2, self.cube, run_time=1.8),
            ApplyMatrix(W2, self.i_vec, run_time=1.8),
            ApplyMatrix(W2, self.j_vec, run_time=1.8),
            ApplyMatrix(W2, self.k_vec, run_time=1.8),
            run_time=1.8,
        )

        self.move_camera(phi=55 * DEGREES, theta=-20 * DEGREES, run_time=1.0, rate_func=smooth)

        wait = max(0.3, dur - 0.5 - 1.8 - 1.0)
        if wait > 0:
            self.wait(wait)

    def _seg_composition(self, seg, dur):
        # Reset cube and basis to identity, then apply the product M = W2 W1
        self.play(FadeOut(self.w1_tex), FadeOut(self.w2_tex), run_time=0.3)

        # Re-create untransformed copies for a clean one-shot animation
        new_cube = Cube(
            side_length=1.5,
            fill_color=CUBE_COLOR,
            fill_opacity=0.18,
            stroke_color=CUBE_COLOR,
            stroke_width=2,
        )
        new_i = Vector(np.array([2, 0, 0]), color=BASIS_I, buff=0)
        new_j = Vector(np.array([0, 2, 0]), color=BASIS_J, buff=0)
        new_k = Vector(np.array([0, 0, 2]), color=BASIS_K, buff=0)
        for v in (new_i, new_j, new_k):
            v.set_stroke(width=4)

        # Replace the transformed objects so the one-shot is obvious
        self.play(
            ReplacementTransform(self.cube, new_cube),
            ReplacementTransform(self.i_vec, new_i),
            ReplacementTransform(self.j_vec, new_j),
            ReplacementTransform(self.k_vec, new_k),
            run_time=0.6,
        )
        self.cube = new_cube
        self.i_vec = new_i
        self.j_vec = new_j
        self.k_vec = new_k

        # Re-wire label updaters to the new vectors
        self.i_label.clear_updaters()
        self.j_label.clear_updaters()
        self.k_label.clear_updaters()
        self.i_label.add_updater(lambda m: m.move_to(self.i_vec.get_end() + UP * 0.25 + RIGHT * 0.25))
        self.j_label.add_updater(lambda m: m.move_to(self.j_vec.get_end() + UP * 0.25 + LEFT * 0.25))
        self.k_label.add_updater(lambda m: m.move_to(self.k_vec.get_end() + UP * 0.35))

        self.m_tex = self._add_matrix_label("M = W_2 W_1", M, YELLOW)
        self.play(
            ApplyMatrix(M, self.cube, run_time=2.0),
            ApplyMatrix(M, self.i_vec, run_time=2.0),
            ApplyMatrix(M, self.j_vec, run_time=2.0),
            ApplyMatrix(M, self.k_vec, run_time=2.0),
            run_time=2.0,
        )

        # Show side-by-side equivalence by overlaying the sequential result as a wireframe
        seq_cube = Cube(
            side_length=1.5,
            fill_color=GREEN,
            fill_opacity=0.0,
            stroke_color=GREEN,
            stroke_width=2,
        )
        seq_cube.apply_matrix(W2 @ W1)  # already at target; used as wireframe overlay
        self.play(FadeIn(seq_cube), run_time=0.6)
        self.play(FadeOut(seq_cube), run_time=0.4)

        wait = max(0.3, dur - 0.3 - 0.6 - 2.0 - 1.0)
        if wait > 0:
            self.wait(wait)

    def _seg_basis_columns(self, seg, dur):
        # Highlight each column of M as the image of a basis vector
        self.play(FadeOut(self.m_tex), run_time=0.3)

        col1 = M[:, 0]
        col2 = M[:, 1]
        col3 = M[:, 2]
        col1_vec = Vector(col1 * 1.5, color=BASIS_I, buff=0)
        col2_vec = Vector(col2 * 1.5, color=BASIS_J, buff=0)
        col3_vec = Vector(col3 * 1.5, color=BASIS_K, buff=0)

        self.play(
            Transform(self.i_vec, col1_vec),
            Transform(self.j_vec, col2_vec),
            Transform(self.k_vec, col3_vec),
            run_time=1.2,
        )

        # Spin around the result for a cinematic reveal
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(max(0.3, dur - 0.3 - 1.2))
        self.stop_ambient_camera_rotation()

    def _seg_neural_net(self, seg, dur):
        # Clean scene: replace 3D objects with a layered network diagram
        self.play(
            *[FadeOut(m) for m in self.mobjects if m is not None],
            run_time=0.6,
        )

        # Re-add the camera frame default
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES, zoom=0.9)

        blocks = VGroup()
        labels = VGroup()
        names = ["W_1", "W_2", r"\cdots", "W_n"]
        colors = [BLUE, PURPLE, GRAY, ORANGE]
        for i, (name, color) in enumerate(zip(names, colors)):
            rect = Rectangle(width=2.2, height=1.1, color=color, fill_color=color, fill_opacity=0.2, stroke_width=3)
            rect.shift(UP * (2.5 - i * 2.2))
            lab = MathTex(name, color=color, font_size=36)
            lab.move_to(rect.get_center())
            blocks.add(rect)
            labels.add(lab)

        arrows = VGroup()
        for i in range(len(blocks) - 1):
            a = Arrow(blocks[i].get_bottom(), blocks[i + 1].get_top(), color=WHITE, buff=0.2)
            arrows.add(a)

        x_label = MathTex("x", color=WHITE, font_size=34).next_to(blocks[0].get_top(), UP, buff=0.4)
        y_label = MathTex("y", color=WHITE, font_size=34).next_to(blocks[-1].get_bottom(), DOWN, buff=0.4)

        group = VGroup(blocks, labels, arrows, x_label, y_label)
        self.add_fixed_in_frame_mobjects(group)
        self.play(FadeIn(blocks), FadeIn(labels), FadeIn(arrows), FadeIn(x_label), FadeIn(y_label), run_time=0.8)

        # Animate a pulse traveling down the arrows
        self.play(*[a.animate.set_color(YELLOW) for a in arrows], run_time=0.5)
        self.play(*[a.animate.set_color(WHITE) for a in arrows], run_time=0.5)

        wait = max(0.3, dur - 0.8 - 1.0)
        if wait > 0:
            self.wait(wait)

        self.play(FadeOut(group), run_time=0.3)

    def _seg_recap(self, seg, dur):
        title = Text("Matrix multiplication", font_size=44, color=WHITE, weight=BOLD)
        subtitle = Text("= composing simple steps into deep learning", font_size=34, color=YELLOW)
        title.to_edge(UP, buff=0.9)
        subtitle.next_to(title, DOWN, buff=0.3)

        eq = MathTex(r"y = W_n \cdots W_2 W_1 x", font_size=40, color=WHITE)
        eq.next_to(subtitle, DOWN, buff=0.6)
        eq.add_background_rectangle(color=BLACK, opacity=0.8)

        self.add_fixed_in_frame_mobjects(title, subtitle, eq)
        self.play(FadeIn(title), FadeIn(subtitle), FadeIn(eq), run_time=0.8)
        self.wait(max(0.3, dur - 0.8))
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(eq), run_time=0.3)

    def _seg_cta(self, seg, dur):
        cta = Text("Follow for more visual math", font_size=40, color=WHITE, weight=BOLD)
        handle = Text("@learningverse123", font_size=26, color=GRAY)
        cta.to_edge(UP, buff=1.5)
        handle.next_to(cta, DOWN, buff=0.4)
        self.add_fixed_in_frame_mobjects(cta, handle)
        self.play(FadeIn(cta), FadeIn(handle), run_time=0.6)
        self.wait(max(0.3, dur - 0.6))
        self.play(FadeOut(cta), FadeOut(handle), run_time=0.3)
