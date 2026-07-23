"""Manim scene for the Vietnamese Shorts about the architecture of mathematical space."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np
from manim import *

PROJECT = Path(__file__).resolve().parent
CONFIG = PROJECT / "config.json"

# Vertical 9:16 Shorts canvas
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = "#05070A"
config.frame_rate = 30

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Palette
C_BG = "#05070A"
C_CYAN = "#00E5FF"
C_VIOLET = "#9D4EDD"
C_RED = "#FF3B3B"
C_WHITE = "#FFFFFF"
C_GRAY = "#555555"
C_BLACK = "#000000"
C_AMBER = "#FFB800"


def load_segments() -> list[float]:
    if CONFIG.exists():
        with open(CONFIG, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("segments", [6.0, 9.0, 12.0, 14.0, 12.0, 13.0, 13.0, 10.0])
    return [6.0, 9.0, 12.0, 14.0, 12.0, 13.0, 13.0, 10.0]


class SafeHelpers:
    """Helpers for safe, readable text and glows."""

    def _viet_text(self, text: str, size: int = 38, color: str = C_WHITE, weight: str = BOLD) -> Mobject:
        lines = text.split("\n")
        if len(lines) == 1:
            return Text(text, font_size=size, color=color, weight=weight, font="Arial")
        block = VGroup(*[
            Text(line, font_size=size, color=color, weight=weight, font="Arial")
            for line in lines
        ])
        block.arrange(DOWN, buff=0.12, center=False)
        return block

    def _title(self, text: str, size: int = 76) -> Mobject:
        t = self._viet_text(text, size=size, color=C_WHITE, weight=BOLD)
        t.move_to(ORIGIN)
        bg = SurroundingRectangle(t, fill_color=C_BLACK, fill_opacity=0.7, stroke_width=0, buff=0.25, corner_radius=0.15)
        return VGroup(bg, t)

    def _sub_text(self, text: str, ref: Mobject | None = None, size: int = 34, color: str = C_CYAN) -> Mobject:
        t = self._viet_text(text, size=size, color=color)
        if ref is None:
            t.to_edge(DOWN, buff=2.0)
        else:
            t.next_to(ref, DOWN, buff=0.4)
        return t

    def _math(self, tex: str, size: int = 42, color: str = C_WHITE) -> MathTex:
        return MathTex(tex, font_size=size, color=color)

    def _glow(self, mobj: Mobject, color: str = C_CYAN, layers: int = 3, scale: float = 1.05) -> VGroup:
        copies = [mobj.copy().set_color(color).set_opacity(0.12 * (1 - i / layers)).scale(scale + i * 0.03) for i in range(layers)]
        return VGroup(*copies, mobj)

    def _backing(self, mobj: Mobject, color: str = C_BLACK, opacity: float = 0.7, buff: float = 0.2) -> SurroundingRectangle:
        return SurroundingRectangle(mobj, fill_color=color, fill_opacity=opacity, stroke_width=0, buff=buff, corner_radius=0.12)


class SpaceArchitectureShort(ThreeDScene, SafeHelpers):
    def setup(self):
        self.segment_durations = load_segments()
        self.total_duration = sum(self.segment_durations)
        self.stage = VGroup()

    def construct(self):
        self.camera.background_color = C_BG
        self._background_grid()
        # Start with a slight 3D tilt for depth
        self.move_camera(phi=55 * DEGREES, theta=-60 * DEGREES, zoom=0.9, run_time=0.01)

        segment_methods = [
            self._seg_01_hook,
            self._seg_02_origin_vector,
            self._seg_03_basis,
            self._seg_04_span,
            self._seg_05_basis_alt,
            self._seg_06_dimension,
            self._seg_07_higher_dim,
            self._seg_08_outro,
        ]
        for dur, method in zip(self.segment_durations, segment_methods):
            method(dur)
            if len(self.stage) > 0:
                self.play(FadeOut(self.stage), run_time=0.3)
                self.stage = VGroup()

    def _add(self, *mobjects: Mobject):
        self.stage.add(*mobjects)
        self.add(*mobjects)

    def _add_fixed(self, *mobjects: Mobject):
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.stage.add(*mobjects)
        self.add(*mobjects)

    def _wait_remaining(self, dur: float, used: float) -> None:
        wait = dur - used - 0.3
        if wait > 0:
            self.wait(wait)

    def _background_grid(self):
        lines = VGroup()
        for x in np.linspace(-4.5, 4.5, 11):
            line = Line([x, -8, -6], [x, 8, -6], color=C_CYAN, stroke_width=1).set_opacity(0.04)
            lines.add(line)
        for y in np.linspace(-8, 8, 17):
            line = Line([-4.5, y, -6], [4.5, y, -6], color=C_CYAN, stroke_width=1).set_opacity(0.04)
            lines.add(line)
        self.add(lines)

    def _axes_2d(self, opacity: float = 0.25):
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-1, 1, 1],
            x_length=7,
            y_length=7,
            z_length=0.01,
            axis_config={"stroke_opacity": opacity, "color": C_GRAY},
        )
        return axes

    def _axes_3d(self, opacity: float = 0.35):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            z_length=5,
            axis_config={"stroke_opacity": opacity, "color": C_GRAY},
        )
        return axes

    # ------------------------------------------------------------------
    # Scene 1: Hook
    # ------------------------------------------------------------------
    def _seg_01_hook(self, dur: float):
        used = 0.0
        axes = self._axes_2d(opacity=0.2)
        self._add(axes)
        self.play(Create(axes), run_time=dur * 0.15)
        used += dur * 0.15

        origin = Dot3D(radius=0.08, color=C_WHITE)
        self._add(origin)
        self.play(GrowFromCenter(origin), run_time=dur * 0.12)
        used += dur * 0.12

        title = self._title("KIẾN TRÚC\nTOÁN HỌC\nKHÔNG GIAN", size=68)
        self._add_fixed(title)
        self.play(FadeIn(title, scale=0.8), run_time=dur * 0.25)
        used += dur * 0.25

        sub = self._sub_text("Mỗi con số sống\ntrong một không gian.", size=30)
        self._add_fixed(sub)
        self.play(FadeIn(sub, shift=UP * 0.3), run_time=dur * 0.2)
        used += dur * 0.2

        # A single vector hints at the theme
        hint = Arrow3D(ORIGIN, [2.5, 1.5, 0], color=C_CYAN, thickness=0.03)
        self._add(hint)
        self.play(Create(hint), run_time=dur * 0.18)
        used += dur * 0.18

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 2: Origin and vector
    # ------------------------------------------------------------------
    def _seg_02_origin_vector(self, dur: float):
        used = 0.0
        axes = self._axes_2d()
        self._add(axes)
        self.play(FadeIn(axes), run_time=dur * 0.15)
        used += dur * 0.15

        origin = Dot3D(radius=0.08, color=C_WHITE)
        origin_label = self._math("O", size=36, color=C_WHITE).next_to(origin, DL * 0.4)
        self._add_fixed(origin_label)
        self._add(origin)
        self.play(GrowFromCenter(origin), FadeIn(origin_label), run_time=dur * 0.15)
        used += dur * 0.15

        vec = Arrow3D(ORIGIN, [2.2, 1.2, 0], color=C_CYAN, thickness=0.04)
        vec_label = self._math(r"\vec{v}", size=42, color=C_CYAN)
        vec_label.next_to(vec.get_end(), UR * 0.3)
        self._add(vec)
        self._add_fixed(vec_label)

        sub = self._sub_text("Từ điểm gốc,\nmột vector bước ra.", size=30)
        self._add_fixed(sub)

        self.play(Create(vec), run_time=dur * 0.25)
        self.play(FadeIn(vec_label), FadeIn(sub), run_time=dur * 0.15)
        used += dur * 0.4

        # gentle wiggle on the vector tip
        self.play(vec.animate.scale(1.05, about_point=ORIGIN), rate_func=there_and_back, run_time=dur * 0.2)
        used += dur * 0.2

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 3: Basis vectors and coordinates
    # ------------------------------------------------------------------
    def _seg_03_basis(self, dur: float):
        used = 0.0
        axes = self._axes_2d()
        self._add(axes)

        i_hat = Arrow3D(ORIGIN, RIGHT, color=C_CYAN, thickness=0.03)
        j_hat = Arrow3D(ORIGIN, UP, color=C_VIOLET, thickness=0.03)
        i_label = self._math(r"\hat{\imath}", size=38, color=C_CYAN).next_to(i_hat.get_end(), DOWN * 0.3)
        j_label = self._math(r"\hat{\jmath}", size=38, color=C_VIOLET).next_to(j_hat.get_end(), LEFT * 0.3)
        self._add(i_hat, j_hat)
        self._add_fixed(i_label, j_label)

        sub = self._sub_text("x, y là cách\nkéo giãn i-hat và j-hat.", size=32)
        self._add_fixed(sub)

        self.play(Create(axes), Create(i_hat), Create(j_hat), FadeIn(i_label), FadeIn(j_label), run_time=dur * 0.22)
        used += dur * 0.22

        # build v = 3 i-hat + 2 j-hat
        scaled_i = Arrow3D(ORIGIN, 3 * RIGHT, color=C_CYAN, thickness=0.03).set_opacity(0.5)
        shifted_j = Arrow3D(3 * RIGHT, 3 * RIGHT + 2 * UP, color=C_VIOLET, thickness=0.03).set_opacity(0.5)
        vec = Arrow3D(ORIGIN, 3 * RIGHT + 2 * UP, color=C_AMBER, thickness=0.05)
        vec_label = self._math(r"\vec{v}", size=40, color=C_AMBER).next_to(vec.get_end(), UR * 0.3)
        math_label = self._math(r"\vec{v}=3\hat{\imath}+2\hat{\jmath}", size=36, color=C_WHITE)
        math_label.to_edge(UP, buff=1.2)
        if math_label.width > 7.5:
            math_label.scale_to_fit_width(7.5)

        self._add(scaled_i, shifted_j, vec)
        self._add_fixed(vec_label, math_label)

        self.play(FadeIn(scaled_i), FadeIn(shifted_j), FadeIn(sub), run_time=dur * 0.2)
        self.play(Create(vec), FadeIn(vec_label), run_time=dur * 0.2)
        self.play(FadeIn(math_label), run_time=dur * 0.15)
        used += dur * 0.55

        # parallelogram ghost
        ghost = Polygon(
            ORIGIN, 3 * RIGHT, 3 * RIGHT + 2 * UP, 2 * UP,
            color=C_CYAN, fill_color=C_CYAN, fill_opacity=0.08, stroke_width=1
        )
        self._add(ghost)
        self.play(FadeIn(ghost), run_time=dur * 0.12)
        used += dur * 0.12

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 4: Linear combination and span
    # ------------------------------------------------------------------
    def _seg_04_span(self, dur: float):
        used = 0.0
        axes = self._axes_2d()
        self._add(axes)

        i_hat = Arrow3D(ORIGIN, RIGHT, color=C_CYAN, thickness=0.03)
        j_hat = Arrow3D(ORIGIN, UP, color=C_VIOLET, thickness=0.03)
        self._add(i_hat, j_hat)
        self.play(Create(axes), Create(i_hat), Create(j_hat), run_time=dur * 0.12)
        used += dur * 0.12

        # random linear combinations as dots
        rng = np.random.default_rng(SEED)
        dots = VGroup()
        coords = []
        for _ in range(60):
            a = rng.uniform(-2.8, 2.8)
            b = rng.uniform(-2.8, 2.8)
            coords.append([a, b, 0])
        for c in coords:
            d = Dot3D(point=c, radius=0.04, color=C_CYAN).set_opacity(0.6)
            dots.add(d)
        self._add(dots)
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=dur * 0.28)
        used += dur * 0.28

        # span plane overlay
        plane = Polygon(
            [-4, -4, 0], [4, -4, 0], [4, 4, 0], [-4, 4, 0],
            color=C_CYAN, fill_color=C_CYAN, fill_opacity=0.06, stroke_width=0
        )
        self._add(plane)
        self.play(FadeIn(plane), run_time=dur * 0.15)
        used += dur * 0.15

        span_label = self._title("SPAN", size=72)
        self._add_fixed(span_label)
        self.play(FadeIn(span_label, scale=0.8), run_time=dur * 0.15)
        used += dur * 0.15

        sub = self._sub_text("Tổ hợp tuyến tính:\nmọi điểm có thể đạt được.", size=30)
        self._add_fixed(sub)
        self.play(FadeIn(sub), run_time=dur * 0.15)
        used += dur * 0.15

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 5: Alternative basis
    # ------------------------------------------------------------------
    def _seg_05_basis_alt(self, dur: float):
        used = 0.0
        axes = self._axes_2d()
        self._add(axes)

        v = np.array([3.0, 2.0, 0.0])
        u = np.array([3.0, 1.0, 0.0])
        w = np.array([0.0, 2.0, 0.0])
        a, b = 1.0, 0.5

        i_hat = Arrow3D(ORIGIN, RIGHT, color=C_CYAN, thickness=0.03)
        j_hat = Arrow3D(ORIGIN, UP, color=C_VIOLET, thickness=0.03)
        vec = Arrow3D(ORIGIN, v, color=C_AMBER, thickness=0.05)
        i_label = self._math(r"\hat{\imath}", size=34, color=C_CYAN).next_to(RIGHT, DOWN * 0.3)
        j_label = self._math(r"\hat{\jmath}", size=34, color=C_VIOLET).next_to(UP, LEFT * 0.3)

        self._add(i_hat, j_hat, vec)
        self._add_fixed(i_label, j_label)
        self.play(Create(axes), Create(i_hat), Create(j_hat), Create(vec), FadeIn(i_label), FadeIn(j_label), run_time=dur * 0.18)
        used += dur * 0.18

        standard_text = self._sub_text("Cơ sở chuẩn:\ni-hat, j-hat", size=30, color=C_WHITE)
        self._add_fixed(standard_text)
        self.play(FadeIn(standard_text), run_time=dur * 0.08)
        used += dur * 0.08

        # swap to alternative basis
        u_hat = Arrow3D(ORIGIN, u, color=C_RED, thickness=0.04)
        w_hat = Arrow3D(ORIGIN, w, color=C_RED, thickness=0.04)
        u_label = self._math(r"\vec{u}", size=36, color=C_RED).next_to(u, UP * 0.3)
        w_label = self._math(r"\vec{w}", size=36, color=C_RED).next_to(w, LEFT * 0.3)
        alt_text = self._sub_text("Cơ sở khác:\nvẫn xây được cùng mặt phẳng", size=30, color=C_RED)

        self.play(
            Transform(i_hat, u_hat),
            Transform(j_hat, w_hat),
            Transform(i_label, u_label),
            Transform(j_label, w_label),
            FadeOut(standard_text),
            run_time=dur * 0.2,
        )
        self._add_fixed(u_label, w_label, alt_text)
        self.play(FadeIn(alt_text), run_time=dur * 0.08)
        used += dur * 0.28

        # show the alternative parallelogram
        scaled_u = Arrow3D(ORIGIN, a * u, color=C_RED, thickness=0.03).set_opacity(0.5)
        shifted_w = Arrow3D(a * u, a * u + b * w, color=C_RED, thickness=0.03).set_opacity(0.5)
        self._add(scaled_u, shifted_w)
        self.play(FadeIn(scaled_u), FadeIn(shifted_w), run_time=dur * 0.12)
        used += dur * 0.12

        math_label = self._math(r"\vec{v}=\vec{u}+0.5\vec{w}", size=34, color=C_WHITE)
        math_label.to_edge(UP, buff=1.2)
        if math_label.width > 7.5:
            math_label.scale_to_fit_width(7.5)
        self._add_fixed(math_label)
        self.play(FadeIn(math_label), run_time=dur * 0.1)
        used += dur * 0.1

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 6: Dimension
    # ------------------------------------------------------------------
    def _seg_06_dimension(self, dur: float):
        used = 0.0
        axes = self._axes_3d()
        self._add(axes)
        self.play(Create(axes), run_time=dur * 0.15)
        used += dur * 0.15

        # Camera swing to emphasise 3D
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.95, run_time=dur * 0.1)
        used += dur * 0.1

        i_hat = Arrow3D(ORIGIN, RIGHT, color=C_CYAN, thickness=0.03)
        j_hat = Arrow3D(ORIGIN, UP, color=C_VIOLET, thickness=0.03)
        k_hat = Arrow3D(ORIGIN, OUT, color=C_AMBER, thickness=0.03)
        i_label = self._math(r"\hat{\imath}", size=34, color=C_CYAN).next_to(RIGHT, DOWN * 0.3)
        j_label = self._math(r"\hat{\jmath}", size=34, color=C_VIOLET).next_to(UP, LEFT * 0.3)
        k_label = self._math(r"\hat{k}", size=34, color=C_AMBER).next_to(OUT, UP * 0.3)

        self._add(i_hat, j_hat, k_hat)
        self._add_fixed(i_label, j_label, k_label)

        self.play(
            Create(i_hat), Create(j_hat),
            FadeIn(i_label), FadeIn(j_label),
            run_time=dur * 0.1,
        )
        self.play(Create(k_hat), FadeIn(k_label), run_time=dur * 0.1)
        used += dur * 0.2

        # Build a vector in 3D
        target = np.array([1.8, 1.8, 1.2])
        vec = Arrow3D(ORIGIN, target, color=C_WHITE, thickness=0.05)
        self._add(vec)
        self.play(Create(vec), run_time=dur * 0.1)
        used += dur * 0.1

        # Dimension counter
        dim_counter = self._viet_text("1", size=72, color=C_CYAN)
        dim_counter.to_edge(UP, buff=1.0)
        dim_label = self._viet_text("chiều", size=28, color=C_WHITE).next_to(dim_counter, DOWN, buff=0.2)
        self._add_fixed(dim_counter, dim_label)
        self.play(FadeIn(dim_counter), FadeIn(dim_label), run_time=dur * 0.08)
        used += dur * 0.08

        for n in ["2", "3"]:
            new_counter = self._viet_text(n, size=72, color=C_CYAN)
            new_counter.move_to(dim_counter.get_center())
            self.play(Transform(dim_counter, new_counter), run_time=dur * 0.05)
            used += dur * 0.05

        sub = self._sub_text("Số vector tối thiểu\nbằng số chiều.", size=32)
        self._add_fixed(sub)
        self.play(FadeIn(sub), run_time=dur * 0.08)
        used += dur * 0.08

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 7: Higher dimensions / data
    # ------------------------------------------------------------------
    def _seg_07_higher_dim(self, dur: float):
        used = 0.0
        # pull camera back to 2.5D abstract view
        self.move_camera(phi=70 * DEGREES, theta=-80 * DEGREES, zoom=0.85, run_time=dur * 0.05)
        used += dur * 0.05

        # coordinate axes as thin lines fading into the distance
        axes = VGroup()
        for i in range(8):
            angle = 2 * PI * i / 8
            end = [3.5 * math.cos(angle), 3.5 * math.sin(angle), 0]
            axis = Arrow3D(ORIGIN, end, color=C_GRAY, thickness=0.015).set_opacity(0.4)
            axes.add(axis)
        self._add(axes)
        self.play(FadeIn(axes, lag_ratio=0.05), run_time=dur * 0.12)
        used += dur * 0.12

        # a single high-dimensional vector stylised as a bar chart / coordinate list
        bars = VGroup()
        rng = np.random.default_rng(SEED)
        for i in range(12):
            h = rng.uniform(0.4, 2.2)
            bar = Rectangle(width=0.28, height=h, color=C_CYAN, fill_color=C_CYAN, fill_opacity=0.6)
            bar.move_to([i * 0.35 - 2.0, h / 2 - 1.5, 0])
            bars.add(bar)
        self._add(bars)
        self.play(FadeIn(bars, lag_ratio=0.05), run_time=dur * 0.12)
        used += dur * 0.12

        rn_label = self._math(r"\mathbb{R}^n", size=56, color=C_AMBER)
        rn_label.to_edge(UP, buff=1.3)
        if rn_label.width > 6:
            rn_label.scale_to_fit_width(6)
        dim_text = self._viet_text("100+ chiều", size=40, color=C_AMBER).next_to(rn_label, DOWN, buff=0.2)
        self._add_fixed(rn_label, dim_text)
        self.play(FadeIn(rn_label), FadeIn(dim_text), run_time=dur * 0.12)
        used += dur * 0.12

        # data point moving along dimensions
        data_dot = Dot3D(radius=0.08, color=C_RED)
        self._add(data_dot)
        positions = [[0.5, 0.5, 0], [1.2, -0.8, 0], [-0.5, 1.5, 0], [2.0, 2.0, 0], [-1.5, -1.0, 0]]
        data_dot.move_to(positions[0])
        self.play(FadeIn(data_dot), run_time=dur * 0.06)
        used += dur * 0.06
        for pos in positions[1:]:
            self.play(data_dot.animate.move_to(pos), run_time=dur * 0.04)
            used += dur * 0.04

        sub = self._sub_text("Dữ liệu AI\nsống trong hàng trăm chiều.", size=30)
        self._add_fixed(sub)
        self.play(FadeIn(sub), run_time=dur * 0.1)
        used += dur * 0.1

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 8: Outro
    # ------------------------------------------------------------------
    def _seg_08_outro(self, dur: float):
        used = 0.0
        # Summary chain
        chain = self._viet_text("ĐIỂM → VECTOR\nCƠ SỞ → SỐ CHIỀU", size=30, color=C_CYAN)
        chain.to_edge(UP, buff=1.4)
        self._add_fixed(chain)

        title = self._title("KIẾN TRÚC\nKHÔNG GIAN", size=64)
        title.move_to(ORIGIN + UP * 1.2)
        self._add_fixed(title)

        cta = self._sub_text("Hiểu nó, bạn thấy toán học\nở khắp nơi. Đăng ký để xem thêm!", size=28, color=C_WHITE)
        self._add_fixed(cta)

        self.play(FadeIn(chain), FadeIn(title, scale=0.85), run_time=dur * 0.25)
        used += dur * 0.25

        self.play(FadeIn(cta, shift=UP * 0.3), run_time=dur * 0.2)
        used += dur * 0.2

        # subtle rotating axes in background
        axes = self._axes_3d(opacity=0.12)
        self._add(axes)
        self.play(Create(axes), run_time=dur * 0.15)
        self.play(Rotate(axes, angle=PI / 6, about_point=ORIGIN, run_time=dur * 0.25, rate_func=linear))
        used += dur * 0.4

        self._wait_remaining(dur, used)
