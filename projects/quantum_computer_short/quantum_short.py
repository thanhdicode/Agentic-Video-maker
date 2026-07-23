"""Manim scene for the quantum computing Vietnamese Shorts."""
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


def load_segments() -> list[float]:
    if CONFIG.exists():
        with open(CONFIG, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("segments", [3.5, 4.5, 9.0, 8.0, 10.0, 12.0, 7.0, 5.3])
    return [3.5, 4.5, 9.0, 8.0, 10.0, 12.0, 7.0, 5.3]


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

    def _title(self, text: str, size: int = 80) -> Mobject:
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


class QuantumComputerShort(ThreeDScene, SafeHelpers):
    def setup(self):
        self.segment_durations = load_segments()
        self.total_duration = sum(self.segment_durations)
        self.stage = VGroup()

    def construct(self):
        self.camera.background_color = C_BG
        # subtle background grid
        self._background_grid()
        # set default 3D camera
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0, run_time=0.01)

        segment_methods = [
            self._seg_01_hook,
            self._seg_02_classical_bit,
            self._seg_03_qubit_bloch,
            self._seg_04_hadamard,
            self._seg_05_bell,
            self._seg_06_interference,
            self._seg_07_measurement,
            self._seg_08_outro,
        ]
        for i, (dur, method) in enumerate(zip(self.segment_durations, segment_methods)):
            method(dur)
            # clear stage between segments
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
        wait = dur - used - 0.3  # reserve end fade
        if wait > 0:
            self.wait(wait)

    # ------------------------------------------------------------------
    def _background_grid(self):
        lines = VGroup()
        for x in np.linspace(-4.5, 4.5, 11):
            line = Line([x, -8, -5], [x, 8, -5], color=C_CYAN, stroke_width=1).set_opacity(0.04)
            lines.add(line)
        for y in np.linspace(-8, 8, 17):
            line = Line([-4.5, y, -5], [4.5, y, -5], color=C_CYAN, stroke_width=1).set_opacity(0.04)
            lines.add(line)
        self.add(lines)

    # ------------------------------------------------------------------
    # Scene 1: Hook
    # ------------------------------------------------------------------
    def _seg_01_hook(self, dur: float):
        used = 0.0
        # binary tunnel
        rng = np.random.default_rng(SEED)
        digits = VGroup()
        for _ in range(50):
            d = Text(str(rng.integers(0, 2)), font_size=12 + rng.integers(0, 18), color=C_CYAN, font="Arial")
            x = rng.uniform(-3.5, 3.5)
            y = rng.uniform(-6, 6)
            z = rng.uniform(2, 10)
            d.move_to([x, y, z]).set_opacity(0.2 + rng.random() * 0.5)
            digits.add(d)
        self._add(digits)

        # rush toward camera
        self.play(digits.animate.shift(IN * 7).set_opacity(0), rate_func=linear, run_time=dur * 0.4)
        used += dur * 0.4

        myth = self._title("THỬ MỌI\nĐÁP ÁN?", size=72)
        self._add_fixed(myth)
        self.play(FadeIn(myth, scale=0.8), run_time=dur * 0.2)
        used += dur * 0.2

        x_line = Line(UP * 2.5 + LEFT * 2.5, DOWN * 2.5 + RIGHT * 2.5, color=C_RED, stroke_width=8)
        self._add_fixed(x_line)
        self.play(Create(x_line), run_time=dur * 0.12)
        used += dur * 0.12

        # replace with qubit hint
        sphere = Sphere(radius=0.5, resolution=(18, 32)).set_color(C_CYAN)
        sphere.set_opacity(0.8)
        glow = self._glow(sphere, color=C_CYAN, layers=3)
        self._add(glow)
        self.play(FadeOut(myth), FadeOut(x_line), FadeIn(glow, scale=0.5), run_time=dur * 0.18)
        used += dur * 0.18

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 2: Classical bit
    # ------------------------------------------------------------------
    def _seg_02_classical_bit(self, dur: float):
        used = 0.0
        # two waves
        wave1 = FunctionGraph(lambda x: 0.4 * math.sin(x * 2), x_range=[-4, 4], color=C_CYAN)
        wave2 = FunctionGraph(lambda x: 0.4 * math.cos(x * 2), x_range=[-4, 4], color=C_VIOLET)
        waves = VGroup(wave1, wave2).shift(UP * 1.5)
        label = self._sub_text("SÓNG XÁC SUẤT", ref=waves, size=48)
        self._add(waves, label)
        self.play(Create(wave1), Create(wave2), FadeIn(label), run_time=dur * 0.25)
        used += dur * 0.25

        # bit cube
        cube = Cube(side_length=1.2, fill_opacity=0.8, stroke_color=C_WHITE, stroke_width=2)
        cube.set_color(C_CYAN).shift(DOWN * 1.2)
        switch = Rectangle(width=0.35, height=0.7, color=C_WHITE, fill_opacity=1).move_to(cube.get_center() + UP * 0.15)
        l0 = self._viet_text("0", size=70, color=C_WHITE).next_to(cube, LEFT, buff=0.5)
        l1 = self._viet_text("1", size=70, color=C_WHITE).next_to(cube, RIGHT, buff=0.5)
        bit_group = VGroup(cube, switch, l0, l1)
        self._add(bit_group)
        self.play(Transform(waves.copy(), cube), FadeOut(waves), FadeOut(label), run_time=dur * 0.2)
        used += dur * 0.2

        # switch 0 -> 1
        self.play(switch.animate.shift(DOWN * 0.3), Indicate(l0, scale_factor=1.4, color=C_RED), run_time=dur * 0.12)
        used += dur * 0.12
        self.play(switch.animate.shift(UP * 0.3), Indicate(l1, scale_factor=1.4, color=C_CYAN), run_time=dur * 0.12)
        used += dur * 0.12

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 3: Qubit / Bloch sphere
    # ------------------------------------------------------------------
    def _seg_03_qubit_bloch(self, dur: float):
        used = 0.0
        self.move_camera(phi=55 * DEGREES, theta=-40 * DEGREES, zoom=1.0, run_time=0.5)
        used += 0.5

        sphere = Sphere(radius=1.2, resolution=(20, 40)).set_color(C_CYAN)
        sphere.set_opacity(0.15)
        axes = ThreeDAxes(
            x_range=[-1.5, 1.5],
            y_range=[-1.5, 1.5],
            z_range=[-1.5, 1.5],
            axis_config={"stroke_width": 2, "include_ticks": False},
        )
        axes.set_color(C_GRAY)
        self._add(sphere, axes)
        self.play(Create(sphere), Create(axes), run_time=dur * 0.2)
        used += dur * 0.2

        l0 = self._math(r"|0\rangle", size=34, color=C_WHITE).move_to(UP * 1.7)
        l1 = self._math(r"|1\rangle", size=34, color=C_WHITE).move_to(DOWN * 1.7)
        self._add_fixed(l0, l1)
        self.play(FadeIn(l0), FadeIn(l1), run_time=dur * 0.08)
        used += dur * 0.08

        # state vector
        vec = Arrow3D(start=ORIGIN, end=[0, 0, 1.2], color=C_CYAN, thickness=0.04)
        glow = self._glow(vec.copy(), color=C_CYAN, layers=2)
        self._add(vec, glow)
        self.play(FadeIn(vec), FadeIn(glow), run_time=dur * 0.12)
        used += dur * 0.12

        # formula
        formula = self._math(r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle", size=44, color=C_WHITE)
        formula.to_edge(UP, buff=0.8)
        self._add_fixed(formula)
        self.play(Write(formula), run_time=dur * 0.18)
        used += dur * 0.18

        # amplitude bars
        bar0 = Rectangle(width=0.5, height=0.1, color=C_CYAN, fill_opacity=1).shift(LEFT * 2 + DOWN * 2.4)
        bar1 = Rectangle(width=0.5, height=0.1, color=C_VIOLET, fill_opacity=1).shift(RIGHT * 2 + DOWN * 2.4)
        amp_label = self._sub_text("Biên độ", size=28)
        self._add_fixed(bar0, bar1, amp_label)
        self.play(TransformFromCopy(vec, bar0), TransformFromCopy(vec, bar1), FadeIn(amp_label), run_time=dur * 0.25)
        used += dur * 0.25

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 4: Hadamard
    # ------------------------------------------------------------------
    def _seg_04_hadamard(self, dur: float):
        used = 0.0
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0, run_time=0.5)
        used += 0.5

        wire = Line(LEFT * 3.5, RIGHT * 3.5, color=C_WHITE, stroke_width=4)
        gate = Square(side_length=0.8, color=C_CYAN, fill_opacity=0.8).move_to(LEFT * 1.0)
        gate_label = self._math(r"H", size=48).move_to(gate.get_center())
        self._add(wire, gate, gate_label)
        self.play(Create(wire), Create(gate), Write(gate_label), run_time=dur * 0.2)
        used += dur * 0.2

        # Bloch sphere at right
        sphere = Sphere(radius=1.0, resolution=(18, 32)).set_color(C_CYAN).set_opacity(0.15).shift(RIGHT * 2.2)
        vec = Arrow3D(start=RIGHT * 2.2, end=RIGHT * 2.2 + UP * 1.0, color=C_CYAN, thickness=0.04)
        self._add(sphere, vec)
        self.play(FadeIn(sphere), FadeIn(vec), run_time=dur * 0.15)
        used += dur * 0.15

        # rotate vector to equator (Hadamard effect visualized as 90 deg rotation around X)
        target_vec = Arrow3D(start=RIGHT * 2.2, end=RIGHT * 2.2 + RIGHT * 1.0, color=C_CYAN, thickness=0.04)
        self.play(Transform(vec, target_vec), run_time=dur * 0.25)
        used += dur * 0.25

        # probability bars
        bars = VGroup(
            Rectangle(width=0.55, height=1.1, color=C_CYAN, fill_opacity=1).shift(LEFT * 1.2 + DOWN * 2.2),
            Rectangle(width=0.55, height=1.1, color=C_VIOLET, fill_opacity=1).shift(RIGHT * 1.2 + DOWN * 2.2),
        )
        blabels = VGroup(
            self._viet_text("50%", size=24).next_to(bars[0], DOWN, buff=0.15),
            self._viet_text("50%", size=24).next_to(bars[1], DOWN, buff=0.15),
        )
        self._add_fixed(bars, blabels)
        self.play(GrowFromEdge(bars[0], DOWN), GrowFromEdge(bars[1], DOWN), Write(blabels), run_time=dur * 0.2)
        used += dur * 0.2

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 5: Bell state
    # ------------------------------------------------------------------
    def _seg_05_bell(self, dur: float):
        used = 0.0
        wires = VGroup(
            Line(LEFT * 3.5 + UP * 0.7, RIGHT * 3.5 + UP * 0.7, color=C_WHITE, stroke_width=4),
            Line(LEFT * 3.5 + DOWN * 0.7, RIGHT * 3.5 + DOWN * 0.7, color=C_WHITE, stroke_width=4),
        )
        self._add(wires)
        self.play(Create(wires), run_time=dur * 0.12)
        used += dur * 0.12

        h_gate = Square(side_length=0.7, color=C_CYAN, fill_opacity=0.8).move_to(LEFT * 1.5 + UP * 0.7)
        h_label = self._math(r"H", size=42).move_to(h_gate.get_center())
        self._add(h_gate, h_label)
        self.play(Create(h_gate), Write(h_label), run_time=dur * 0.12)
        used += dur * 0.12

        cnot = VGroup(
            Dot(point=RIGHT * 0.5 + UP * 0.7, color=C_CYAN).scale(1.4),
            Circle(radius=0.28, color=C_CYAN).move_to(RIGHT * 0.5 + DOWN * 0.7),
            Line(RIGHT * 0.5 + UP * 0.7, RIGHT * 0.5 + DOWN * 0.7, color=C_CYAN, stroke_width=3),
        )
        self._add(cnot)
        self.play(Create(cnot), run_time=dur * 0.12)
        used += dur * 0.12

        # pulse travels
        pulse = Dot(color=C_WHITE).move_to(LEFT * 1.5 + UP * 0.7)
        self._add(pulse)
        self.play(MoveAlongPath(pulse, Line(LEFT * 1.5 + UP * 0.7, RIGHT * 0.5 + UP * 0.7)), run_time=dur * 0.12)
        used += dur * 0.12
        self.play(MoveAlongPath(pulse, Line(RIGHT * 0.5 + UP * 0.7, RIGHT * 0.5 + DOWN * 0.7)), run_time=dur * 0.08)
        used += dur * 0.08

        # Bell formula
        bell = self._math(r"\frac{|00\rangle + |11\rangle}{\sqrt{2}}", size=48, color=C_WHITE)
        bell.to_edge(UP, buff=0.9)
        self._add_fixed(bell)
        self.play(Write(bell), run_time=dur * 0.18)
        used += dur * 0.18

        # measurement results strip
        results = self._viet_text("00   11   00   11", size=38, color=C_CYAN)
        results.to_edge(DOWN, buff=1.0)
        self._add_fixed(results)
        self.play(FadeIn(results), run_time=dur * 0.1)
        used += dur * 0.1

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 6: Interference
    # ------------------------------------------------------------------
    def _seg_06_interference(self, dur: float):
        used = 0.0
        vt = ValueTracker(0)
        wave_good = always_redraw(lambda: FunctionGraph(
            lambda x: 0.5 * math.sin(2 * x + vt.get_value()),
            x_range=[-4, 4],
            color=C_CYAN,
        ).shift(UP * 1.2))
        wave_bad = always_redraw(lambda: FunctionGraph(
            lambda x: 0.5 * math.sin(2 * x + vt.get_value() + math.pi),
            x_range=[-4, 4],
            color=C_RED,
        ).shift(UP * 1.2))
        self._add(wave_good, wave_bad)
        self.play(Create(wave_good), Create(wave_bad), run_time=dur * 0.2)
        used += dur * 0.2

        # animate phase so waves overlap
        self.play(
            vt.animate.set_value(2 * PI),
            wave_bad.animate.set_opacity(0.25),
            wave_good.animate.scale(1.4),
            run_time=dur * 0.45,
        )
        used += dur * 0.45

        text = self._title("SAI → TRIỆT TIÊU\nĐÚNG → CỘNG HƯỞNG", size=58)
        text.move_to(DOWN * 2.2)
        self._add_fixed(text)
        self.play(FadeIn(text, scale=0.9), run_time=dur * 0.2)
        used += dur * 0.2

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 7: Measurement
    # ------------------------------------------------------------------
    def _seg_07_measurement(self, dur: float):
        used = 0.0
        # histogram
        heights = [0.15, 0.15, 0.05, 0.05, 0.6, 0.05, 0.05, 0.15]
        bars = VGroup()
        for i, h in enumerate(heights):
            color = C_CYAN if h > 0.2 else C_RED
            r = Rectangle(width=0.5, height=h * 4.5, color=color, fill_opacity=1).shift(RIGHT * (i - 3.5) * 0.6 + DOWN * 2 + UP * h * 2.25)
            bars.add(r)
        self._add(bars)
        self.play(FadeIn(bars), run_time=dur * 0.2)
        used += dur * 0.2

        sweep = Rectangle(width=0.12, height=6, color=C_WHITE, fill_opacity=0.3).shift(LEFT * 4 + UP * 0)
        self._add(sweep)
        self.play(sweep.animate.shift(RIGHT * 8), run_time=dur * 0.3)
        used += dur * 0.3

        # collapse to one bar
        target = Rectangle(width=0.6, height=2.7, color=C_CYAN, fill_opacity=1).shift(DOWN * 0.8)
        self.play(Transform(bars, target), run_time=dur * 0.25)
        used += dur * 0.25

        label = self._viet_text("QUANTUM PROCESS → CLASSICAL RESULT", size=28, color=C_WHITE)
        label.to_edge(UP, buff=0.9)
        self._add_fixed(label)
        self.play(FadeIn(label), run_time=dur * 0.1)
        used += dur * 0.1

        self._wait_remaining(dur, used)

    # ------------------------------------------------------------------
    # Scene 8: Outro
    # ------------------------------------------------------------------
    def _seg_08_outro(self, dur: float):
        used = 0.0
        chip = Rectangle(width=3, height=2, color=C_CYAN, fill_opacity=0.2, stroke_width=3).move_to(UP * 0.8)
        circuits = VGroup()
        for i in range(4):
            y = 0.4 - i * 0.35
            circuits.add(Line(LEFT * 1.2 + UP * y, RIGHT * 1.2 + UP * y, color=C_CYAN, stroke_width=2))
            circuits.add(Dot(point=LEFT * 0.6 + UP * y, color=C_WHITE).scale(0.5))
            circuits.add(Circle(radius=0.12, color=C_WHITE).move_to(RIGHT * 0.6 + UP * y))
        chip_group = VGroup(chip, circuits).move_to(UP * 0.8)
        self._add(chip_group)
        self.play(FadeIn(chip_group), run_time=dur * 0.18)
        used += dur * 0.18

        line1 = self._title("KHÔNG PHẢI\nNHIỀU ĐÁP ÁN.", size=64)
        line1.move_to(DOWN * 2.2)
        self._add_fixed(line1)
        self.play(FadeIn(line1), run_time=dur * 0.15)
        used += dur * 0.15

        line2 = self._title("LÀ GIAO THOA\nĐƯỢC THIẾT KẾ.", size=64)
        line2.move_to(DOWN * 2.2)
        self.play(Transform(line1, line2), run_time=dur * 0.2)
        used += dur * 0.2

        particle = Dot(color=C_CYAN).move_to(chip.get_center())
        self._add(particle)
        self.play(MoveAlongPath(particle, Line(chip.get_center(), UP * 5)), run_time=dur * 0.15)
        used += dur * 0.15

        cta = self._sub_text("Phần sau: Thuật toán Grover?", size=26, color=C_WHITE)
        self._add_fixed(cta)
        self.play(FadeIn(cta), run_time=dur * 0.1)
        used += dur * 0.1

        self._wait_remaining(dur, used)
