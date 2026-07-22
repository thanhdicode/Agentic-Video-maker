"""3D Manim scene: "Ma trận là trái tim của AI" — Vietnamese vertical Shorts.

Vertical 1080x1920, 30fps, dark background, 3D camera moves, clear labels,
background music, and Vietnamese subtitles.
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
config.background_color = "#0A0A0A"
config.frame_rate = 30


# Two 3x3 matrices whose composition looks interesting in 3D.
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
CUBE_COLOR = "#2DD4BF"
BASIS_I = RED
BASIS_J = GREEN
BASIS_K = GOLD


def _matrix_tex(name: str, mat: np.ndarray, color: str = WHITE) -> VGroup:
    """Return a fixed-in-frame matrix group with a dark background."""
    entries = [[f"{v:.2f}" for v in row] for row in mat]
    matrix_mob = Matrix(entries, h_buff=1.0, v_buff=0.7).scale(0.5)
    for i, col_color in enumerate([BASIS_I, BASIS_J, BASIS_K]):
        for entry in matrix_mob.get_entries()[i::3]:
            entry.set_color(col_color)
    name_tex = MathTex(name, color=color, font_size=26)
    name_tex.next_to(matrix_mob, LEFT, buff=0.25)
    group = VGroup(name_tex, matrix_mob)
    bg = BackgroundRectangle(group, color=BLACK, fill_opacity=0.85, buff=0.12)
    return VGroup(bg, group)


class MatrixAIVietnamese(ThreeDScene):
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
                "tip_width": 0.18,
                "tip_height": 0.18,
                "include_numbers": False,
                "color": GRAY_B,
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
            fill_opacity=0.15,
            stroke_color=CUBE_COLOR,
            stroke_width=2,
        )

    def _build_basis(self):
        self.i_vec = Vector(np.array([2, 0, 0]), color=BASIS_I, buff=0)
        self.j_vec = Vector(np.array([0, 2, 0]), color=BASIS_J, buff=0)
        self.k_vec = Vector(np.array([0, 0, 2]), color=BASIS_K, buff=0)
        for v in (self.i_vec, self.j_vec, self.k_vec):
            v.set_stroke(width=4)

        self.i_label = MathTex(r"\hat i", color=BASIS_I, font_size=26)
        self.j_label = MathTex(r"\hat j", color=BASIS_J, font_size=26)
        self.k_label = MathTex(r"\hat k", color=BASIS_K, font_size=26)
        for lab in (self.i_label, self.j_label, self.k_label):
            lab.add_background_rectangle(color=BLACK, opacity=0.75)
            self.add_fixed_orientation_mobjects(lab)

        def _label_pos(tip, extra=UP * 0.6):
            norm = np.linalg.norm(tip)
            if norm > 0.01:
                return tip + extra + (tip / norm) * 1.5
            return tip + extra

        self.i_label.add_updater(lambda m: m.move_to(_label_pos(self.i_vec.get_end())))
        self.j_label.add_updater(lambda m: m.move_to(_label_pos(self.j_vec.get_end())))
        self.k_label.add_updater(lambda m: m.move_to(_label_pos(self.k_vec.get_end())))

    def _add_matrix_label(self, name: str, mat: np.ndarray, color: str = WHITE, shift: np.ndarray = UP * 2.8):
        tex = _matrix_tex(name, mat, color)
        tex.to_edge(RIGHT, buff=0.35)
        tex.shift(shift)
        self.add_fixed_in_frame_mobjects(tex)
        return tex

    def _text_block(self, text: str, size: int, color: str, weight: str) -> Mobject:
        lines = text.split("\n")
        if len(lines) == 1:
            return Text(text, font_size=size, color=color, weight=weight, font="Arial")
        block = VGroup(*[
            Text(line, font_size=size, color=color, weight=weight, font="Arial")
            for line in lines
        ])
        block.arrange(DOWN, buff=0.12, center=False)
        return block

    def _viet_title(self, text: str, color: str = WHITE, size: int = 38, weight: str = BOLD) -> Mobject:
        title = self._text_block(text, size, color, weight)
        title.to_edge(UP, buff=0.9)
        title.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(title)
        return title

    def _viet_subtitle(self, text: str, ref: Mobject, color: str = YELLOW, size: int = 32) -> Mobject:
        sub = self._text_block(text, size, color, BOLD)
        sub.next_to(ref, DOWN, buff=0.35)
        sub.add_background_rectangle(color=BLACK, opacity=0.75)
        self.add_fixed_in_frame_mobjects(sub)
        return sub

    # -----------------------------------------------------------------------
    # Segments
    # -----------------------------------------------------------------------
    def _seg_hook(self, seg, dur):
        title = self._viet_title("Ma trận là trái tim của AI", size=44)
        sub = self._viet_subtitle("Mỗi lần AI hoạt động,\nnó chỉ làm một việc:", title, size=30)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.9)
        preview = self.cube.copy().scale(0.6)
        self.add(preview)

        self.play(FadeIn(title), FadeIn(sub), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.12)
        # Leave time for the Flash/FadeIn tag and final FadeOut.
        self.wait(max(0.3, dur - 0.6 - 0.5 - 0.4))
        self.stop_ambient_camera_rotation()

        # Flash around the cube and reveal the tagline
        tag = Text("nhân ma trận", font_size=42, color=CUBE_COLOR, weight=BOLD, font="Arial")
        tag.move_to(ORIGIN)
        tag.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(tag)
        self.play(Flash(preview, color=CUBE_COLOR, line_length=0.35, flash_radius=1.2), FadeIn(tag), run_time=0.5)
        self.play(FadeOut(title), FadeOut(sub), FadeOut(tag), FadeOut(preview), run_time=0.4)

    def _seg_matrix_transform(self, seg, dur):
        title = self._viet_title("Ma trận = phép\nbiến hình không gian", size=30)

        # 2x2 matrix example to keep it readable on vertical screen
        mat = Matrix([["a", "b"], ["c", "d"]], h_buff=1.1, v_buff=0.8).scale(0.65)
        mat.move_to(ORIGIN)
        mat.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(mat)

        words = VGroup()
        for label, color, direction in [
            ("xoay", YELLOW, UP * 2.0 + LEFT * 1.8),
            ("kéo", GREEN, UP * 2.0 + RIGHT * 1.8),
            ("nghiêng", ORANGE, DOWN * 2.0 + LEFT * 1.8),
            ("phóng to", RED, DOWN * 2.0 + RIGHT * 1.8),
        ]:
            t = Text(label, font_size=30, color=color, weight=BOLD, font="Arial")
            t.move_to(direction)
            t.add_background_rectangle(color=BLACK, opacity=0.7)
            words.add(t)

        self.add_fixed_in_frame_mobjects(words)

        arrows = VGroup()
        for w, sign in zip(words, [1, 1, -1, -1]):
            if w.get_center()[1] > 0:
                start = w.get_bottom()
                end = mat.get_top() + UP * 0.1
            else:
                start = w.get_top()
                end = mat.get_bottom() + DOWN * 0.1
            arr = Arrow(start, end, color=w.get_color(), buff=0.15, stroke_width=2)
            arrows.add(arr)
        self.add_fixed_in_frame_mobjects(arrows)

        self.play(FadeIn(title), FadeIn(mat), run_time=0.5)
        self.play(*[FadeIn(w, shift=UP * 0.2) for w in words], run_time=0.8)
        self.play(*[Create(a) for a in arrows], run_time=0.7)

        self.play(Indicate(mat.get_entries(), color=CUBE_COLOR, scale_factor=1.05), run_time=0.5)

        wait = max(0.3, dur - 0.5 - 0.8 - 0.7 - 0.5 - 0.4)
        self.wait(wait)
        self.play(FadeOut(title), FadeOut(mat), FadeOut(words), FadeOut(arrows), run_time=0.4)

    def _seg_cube_3d(self, seg, dur):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-65 * DEGREES, zoom=0.85)

        coords = MathTex(r"(x, y, z)", color=WHITE, font_size=34)
        coords.to_corner(UL, buff=0.6)
        coords.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(coords)

        self.play(
            Create(self.axes),
            FadeIn(self.axis_labels),
            FadeIn(self.cube),
            run_time=1.2,
        )

        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(max(0.3, dur - 1.2 - 0.3))
        self.stop_ambient_camera_rotation()

        self.play(FadeOut(coords), run_time=0.3)

    def _seg_basis(self, seg, dur):
        title = self._viet_title("Bộ cơ sở i, j, k", size=38)

        w_tex = self._add_matrix_label("W", W1, BLUE)

        self.play(
            GrowArrow(self.i_vec),
            GrowArrow(self.j_vec),
            GrowArrow(self.k_vec),
            run_time=0.9,
        )

        # Highlight matrix columns one by one, synced with basis vectors
        entries = w_tex[1][1].get_entries()
        for col_idx, vec, label in zip([0, 1, 2], [self.i_vec, self.j_vec, self.k_vec], [self.i_label, self.j_label, self.k_label]):
            col = entries[col_idx::3]
            self.play(
                Indicate(VGroup(*col), color=col[0].get_color(), scale_factor=1.2),
                Indicate(vec, color=vec.get_color(), scale_factor=1.2),
                run_time=0.5,
            )

        wait = max(0.3, dur - 0.9 - 1.5 - 0.3)
        self.wait(wait)
        self.play(FadeOut(title), FadeOut(w_tex), run_time=0.3)

    def _seg_W1(self, seg, dur):
        self.w1_tex = self._add_matrix_label("W_1", W1, BLUE)

        trace_group = VGroup()
        for v, col in zip([self.i_vec, self.j_vec, self.k_vec], [BASIS_I, BASIS_J, BASIS_K]):
            trace = TracedPath(v.get_end, stroke_color=col, stroke_width=2, dissipating_time=0.3)
            trace_group.add(trace)
            self.add(trace)

        self.play(
            ApplyMatrix(W1, self.cube, run_time=1.8),
            ApplyMatrix(W1, self.i_vec, run_time=1.8),
            ApplyMatrix(W1, self.j_vec, run_time=1.8),
            ApplyMatrix(W1, self.k_vec, run_time=1.8),
            run_time=1.8,
        )

        self.move_camera(phi=60 * DEGREES, theta=-40 * DEGREES, run_time=1.0, rate_func=smooth)

        # Highlight W1 columns vs transformed basis vectors
        entries = self.w1_tex[1][1].get_entries()
        for col_idx, vec in zip([0, 1, 2], [self.i_vec, self.j_vec, self.k_vec]):
            col = VGroup(*entries[col_idx::3])
            self.play(
                Indicate(col, color=col[0].get_color(), scale_factor=1.15),
                Indicate(vec, color=vec.get_color(), scale_factor=1.15),
                run_time=0.35,
            )

        self.remove(trace_group)

        wait = max(0.3, dur - 1.8 - 1.0 - 1.05)
        self.wait(wait)

    def _seg_W2(self, seg, dur):
        self.w2_tex = self._add_matrix_label("W_2", W2, PURPLE, shift=UP * 1.0)
        # Chain arrow W1 -> W2
        chain = MathTex(r"\rightarrow", color=WHITE, font_size=36)
        chain.next_to(self.w1_tex, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(chain)

        self.play(FadeIn(self.w2_tex), FadeIn(chain), run_time=0.4)

        self.play(
            ApplyMatrix(W2, self.cube, run_time=1.7),
            ApplyMatrix(W2, self.i_vec, run_time=1.7),
            ApplyMatrix(W2, self.j_vec, run_time=1.7),
            ApplyMatrix(W2, self.k_vec, run_time=1.7),
            run_time=1.7,
        )

        self.move_camera(phi=55 * DEGREES, theta=-25 * DEGREES, run_time=1.0, rate_func=smooth)

        wait = max(0.3, dur - 0.4 - 1.7 - 1.0 - 0.3)
        self.wait(wait)
        self.play(FadeOut(self.w1_tex), FadeOut(self.w2_tex), FadeOut(chain), run_time=0.3)

    def _seg_composition(self, seg, dur):
        # Reset cube and basis to identity for a clean one-shot product
        new_cube = Cube(
            side_length=1.5,
            fill_color=CUBE_COLOR,
            fill_opacity=0.15,
            stroke_color=CUBE_COLOR,
            stroke_width=2,
        )
        new_i = Vector(np.array([2, 0, 0]), color=BASIS_I, buff=0)
        new_j = Vector(np.array([0, 2, 0]), color=BASIS_J, buff=0)
        new_k = Vector(np.array([0, 0, 2]), color=BASIS_K, buff=0)
        for v in (new_i, new_j, new_k):
            v.set_stroke(width=4)

        self.play(
            ReplacementTransform(self.cube, new_cube),
            ReplacementTransform(self.i_vec, new_i),
            ReplacementTransform(self.j_vec, new_j),
            ReplacementTransform(self.k_vec, new_k),
            run_time=0.5,
        )
        self.cube = new_cube
        self.i_vec = new_i
        self.j_vec = new_j
        self.k_vec = new_k

        self.i_label.clear_updaters()
        self.j_label.clear_updaters()
        self.k_label.clear_updaters()
        self.i_label.add_updater(lambda m: m.move_to(self.i_vec.get_end() + UP * 0.25 + RIGHT * 0.25))
        self.j_label.add_updater(lambda m: m.move_to(self.j_vec.get_end() + UP * 0.25 + LEFT * 0.25))
        self.k_label.add_updater(lambda m: m.move_to(self.k_vec.get_end() + UP * 0.35))

        self.m_tex = self._add_matrix_label("M = W_2 W_1", M, YELLOW)

        self.play(
            ApplyMatrix(M, self.cube, run_time=1.8),
            ApplyMatrix(M, self.i_vec, run_time=1.8),
            ApplyMatrix(M, self.j_vec, run_time=1.8),
            ApplyMatrix(M, self.k_vec, run_time=1.8),
            run_time=1.8,
        )

        self.move_camera(phi=50 * DEGREES, theta=-45 * DEGREES, zoom=1.0, run_time=1.0, rate_func=smooth)

        # Overlay wireframe to prove equivalence
        seq_cube = Cube(
            side_length=1.5,
            fill_color=GREEN,
            fill_opacity=0.0,
            stroke_color=GREEN,
            stroke_width=2,
        )
        seq_cube.apply_matrix(M)
        self.play(FadeIn(seq_cube), run_time=0.4)
        self.play(Flash(seq_cube, color=GREEN, line_length=0.2, flash_radius=1.0), run_time=0.3)
        self.play(FadeOut(seq_cube), run_time=0.3)

        wait = max(0.3, dur - 0.5 - 1.8 - 1.0 - 1.0)
        self.wait(wait)

    def _seg_why(self, seg, dur):
        self.play(FadeOut(self.m_tex), run_time=0.3)

        # Show column-wise composition: M[:,j] = W2 @ W1[:,j]
        col1_w1 = Vector(W1[:, 0] * 1.5, color=BASIS_I, buff=0)
        col2_w1 = Vector(W1[:, 1] * 1.5, color=BASIS_J, buff=0)
        col3_w1 = Vector(W1[:, 2] * 1.5, color=BASIS_K, buff=0)

        cols = VGroup(col1_w1, col2_w1, col3_w1)
        self.play(FadeIn(cols), run_time=0.5)

        self.play(
            ApplyMatrix(W2, col1_w1, run_time=1.0),
            ApplyMatrix(W2, col2_w1, run_time=1.0),
            ApplyMatrix(W2, col3_w1, run_time=1.0),
            run_time=1.0,
        )

        eq = MathTex(r"M_{:,j} = W_2 \cdot W_{1,:,j}", color=WHITE, font_size=36)
        eq.to_edge(UP, buff=1.1)
        eq.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(eq)

        self.play(FadeIn(eq), run_time=0.5)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(max(0.3, dur - 0.3 - 0.5 - 1.0 - 0.5 - 0.3))
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(cols), FadeOut(eq), run_time=0.3)

    def _seg_neural_net(self, seg, dur):
        title = self._viet_title("Mạng nơ-ron = chuỗi ma trận", size=32)

        # Clean scene
        self.play(
            *[FadeOut(m) for m in self.mobjects if m is not None],
            run_time=0.6,
        )

        blocks = VGroup()
        labels = VGroup()
        names = ["W_1", "W_2", r"\cdots", "W_n"]
        colors = [BLUE, PURPLE, GRAY, ORANGE]
        for i, (name, color) in enumerate(zip(names, colors)):
            rect = Rectangle(width=2.4, height=1.0, color=color, fill_color=color, fill_opacity=0.2, stroke_width=3)
            rect.shift(UP * (2.4 - i * 1.8))
            lab = MathTex(name, color=color, font_size=34)
            lab.move_to(rect.get_center())
            blocks.add(rect)
            labels.add(lab)

        arrows = VGroup()
        for i in range(len(blocks) - 1):
            a = Arrow(blocks[i].get_bottom(), blocks[i + 1].get_top(), color=WHITE, buff=0.15)
            arrows.add(a)

        x_label = MathTex("x", color=WHITE, font_size=34).next_to(blocks[0].get_top(), UP, buff=0.3)
        y_label = MathTex("y", color=WHITE, font_size=34).next_to(blocks[-1].get_bottom(), DOWN, buff=0.3)

        group = VGroup(blocks, labels, arrows, x_label, y_label)
        group.move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(group)

        self.play(FadeIn(title), run_time=0.4)
        self.play(
            FadeIn(blocks),
            FadeIn(labels),
            FadeIn(x_label),
            FadeIn(y_label),
            run_time=0.5,
        )
        self.play(*[Create(a) for a in arrows], run_time=0.6)

        # Pulse traveling down
        for a in arrows:
            self.play(a.animate.set_color(YELLOW), run_time=0.25)
        self.play(*[a.animate.set_color(WHITE) for a in arrows], run_time=0.25)

        wait = max(0.3, dur - 0.6 - 0.4 - 0.5 - 0.6 - 0.5 - 0.3)
        self.wait(wait)
        self.play(FadeOut(title), FadeOut(group), run_time=0.3)

    def _seg_forward_pass(self, seg, dur):
        title = self._viet_title("Dữ liệu chảy qua từng lớp", size=32)

        # Data vector x at top
        x_vec = MathTex("x", color=WHITE, font_size=38).to_edge(UP, buff=1.8)
        x_vec.add_background_rectangle(color=BLACK, opacity=0.8)

        # Layer blocks laid out vertically
        layer_names = ["W_1", "+ b", "ReLU", "W_2", "W_3"]
        layer_colors = [BLUE, GRAY, GREEN, PURPLE, ORANGE]
        blocks = VGroup()
        labels = VGroup()
        for i, (name, color) in enumerate(zip(layer_names, layer_colors)):
            rect = RoundedRectangle(width=2.6, height=0.9, color=color, fill_color=color, fill_opacity=0.2, stroke_width=3, corner_radius=0.15)
            rect.shift(UP * (1.4 - i * 1.35))
            lab = MathTex(name, color=color, font_size=30)
            lab.move_to(rect.get_center())
            blocks.add(rect)
            labels.add(lab)

        arrows = VGroup()
        for i in range(len(blocks) - 1):
            a = Arrow(blocks[i].get_bottom(), blocks[i + 1].get_top(), color=WHITE, buff=0.12)
            arrows.add(a)

        y_label = MathTex("y", color=WHITE, font_size=38).next_to(blocks[-1].get_bottom(), DOWN, buff=0.4)
        y_label.add_background_rectangle(color=BLACK, opacity=0.8)

        # ReLU plot
        relu_axes = Axes(
            x_range=(-2, 2, 1),
            y_range=(-0.5, 2, 0.5),
            x_length=1.6,
            y_length=1.2,
            tips=False,
            axis_config={"color": GRAY_B, "stroke_width": 1.5},
        ).next_to(blocks[2], RIGHT, buff=0.4)
        relu_graph = relu_axes.plot(lambda x: max(0, x), x_range=(-2, 2), color=GREEN, stroke_width=3)
        relu_label = MathTex(r"\max(0, z)", color=GREEN, font_size=22).next_to(relu_axes, UP, buff=0.1)
        relu_group = VGroup(relu_axes, relu_graph, relu_label)

        group = VGroup(blocks, labels, arrows, x_vec, y_label, relu_group)
        self.add_fixed_in_frame_mobjects(group)

        self.play(FadeIn(title), run_time=0.4)
        self.play(FadeIn(x_vec), run_time=0.3)
        self.play(FadeIn(blocks), FadeIn(labels), run_time=0.5)
        self.play(*[Create(a) for a in arrows], run_time=0.5)

        # Animate a dot traveling through layers
        dot = Dot(color=YELLOW, radius=0.08).move_to(blocks[0].get_top())
        self.add_fixed_in_frame_mobjects(dot)
        self.play(FadeIn(dot), run_time=0.2)
        for block, arrow in zip(blocks, arrows):
            self.play(dot.animate.move_to(block.get_center()), run_time=0.35)
            self.play(Indicate(block, color=YELLOW, scale_factor=1.05), run_time=0.2)
            self.play(dot.animate.move_to(arrow.get_end()), run_time=0.2)

        self.play(FadeIn(relu_group), run_time=0.3)
        self.play(dot.animate.move_to(blocks[-1].get_center()), run_time=0.35)
        self.play(FadeIn(y_label), run_time=0.3)

        wait = max(0.3, dur - 0.4 - 0.3 - 0.5 - 0.5 - 0.2 - 3.0 - 0.3 - 0.35 - 0.3 - 0.3)
        self.wait(wait)
        self.play(FadeOut(title), FadeOut(group), FadeOut(dot), run_time=0.3)

    def _seg_recap_cta(self, seg, dur):
        title = self._viet_title("AI không ma thuật", size=42)
        sub = self._viet_subtitle("Chỉ là hàng triệu\nphép nhân ma trận", title, size=32, color=YELLOW)

        eq = MathTex(r"y = W_n \cdots W_2 \cdot W_1 x", color=CUBE_COLOR, font_size=36)
        eq.next_to(sub, DOWN, buff=0.6)
        eq.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(eq)

        cta = Text("Theo dõi để xem thêm toán học đằng sau AI", font_size=28, color=GRAY, weight=BOLD, font="Arial")
        cta.to_edge(DOWN, buff=1.0)
        cta.add_background_rectangle(color=BLACK, opacity=0.8)
        self.add_fixed_in_frame_mobjects(cta)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.85)
        preview = self.cube.copy().scale(0.5)
        self.add(preview)

        self.play(FadeIn(title), FadeIn(sub), FadeIn(eq), FadeIn(preview), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(max(0.3, dur - 0.6 - 0.3 - 0.4))
        self.play(FadeIn(cta), run_time=0.3)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(title), FadeOut(sub), FadeOut(eq), FadeOut(cta), FadeOut(preview), run_time=0.4)
