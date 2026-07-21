"""High-end Manim Shorts: Fourier series building a square wave.

1080x1920 vertical, 30 fps, dark background, LaTeX formulas, dynamic graph
build-up, and a clean payoff reveal.
"""
from __future__ import annotations

import json
from functools import partial
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
config.background_color = "#0d0d0d"
config.frame_rate = 30

TERM_COLORS = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE, PINK]


def square_wave(x):
    return np.sign(np.sin(x))


def fourier_sum(x, max_k: int):
    """Cumulative Fourier sum for square wave, 0-indexed up to max_k."""
    total = np.zeros_like(x)
    for k in range(max_k + 1):
        n = 2 * k + 1
        total += np.sin(n * x) / n
    return (4.0 / np.pi) * total


def harmonic_term(x, k: int):
    """Single harmonic term (4/pi) * sin(n x) / n."""
    n = 2 * k + 1
    return (4.0 / np.pi) * np.sin(n * x) / n


class FourierSquareWave(Scene):
    def construct(self):
        config_path = Path(__file__).resolve().parent / "config.json"
        CONFIG = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        self.segments = CONFIG.get("segments", [])

        # Shared axes
        self.axes = self._make_axes()
        self.sum_graph = None

        for seg in self.segments:
            stype = seg["type"]
            dur = float(seg.get("duration", 3.0))
            getattr(self, f"_seg_{stype}")(seg, dur)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _make_axes(self):
        axes = Axes(
            x_range=[0, TAU, PI / 2],
            y_range=[-1.6, 1.6, 1],
            x_length=7.5,
            y_length=4.0,
            axis_config={
                "include_tip": False,
                "include_numbers": False,
                "stroke_color": "#555555",
                "stroke_width": 1.5,
            },
            x_axis_config={"include_numbers": False},
            y_axis_config={"numbers_to_include": [-1, 0, 1]},
        )
        axes.shift(UP * 0.5)
        return axes

    def _plot(self, func, color=WHITE, width=3, opacity=1.0):
        return self.axes.plot(
            func,
            x_range=[0, TAU, 0.12],
            color=color,
            stroke_width=width,
            stroke_opacity=opacity,
        )

    def _dashed_square(self):
        graph = self.axes.plot(square_wave, x_range=[0, TAU, 0.05], color=GRAY, stroke_width=2)
        graph.set_stroke(opacity=0.35)
        return DashedVMobject(graph, num_dashes=80, dashed_ratio=0.35)

    def _formula(self):
        return MathTex(
            r"\frac{4}{\pi}\sum_{k=0}^{\infty}",
            r"\frac{\sin\big((2k+1)t\big)}{2k+1}",
            font_size=38,
            color=WHITE,
        )

    # -----------------------------------------------------------------------
    # Segments
    # -----------------------------------------------------------------------
    def _seg_hook(self, seg, dur):
        title = Text("A square wave from sine waves?", font_size=48, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=1.0)
        subtitle = Text("(Fourier series in 60 seconds)", font_size=28, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.2)

        preview = self._dashed_square()
        preview.fade(0.4)

        self.play(FadeIn(title), FadeIn(subtitle), run_time=0.6)
        self.play(Create(preview), run_time=0.8)
        self.wait(max(0.5, dur - 1.4))
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.5)

    def _seg_setup(self, seg, dur):
        self.play(FadeIn(self.axes), run_time=0.8)
        labels = self.axes.get_axis_labels(
            MathTex("t", color=WHITE, font_size=28),
            MathTex("f(t)", color=WHITE, font_size=28),
        )
        self.play(FadeIn(labels), run_time=0.4)

        sine = self._plot(np.sin, color=BLUE, width=3)
        self.play(Create(sine), run_time=1.2)

        self.wait(max(0.3, dur - 0.8 - 0.4 - 1.2))
        self.play(FadeOut(sine), run_time=0.4)

    def _seg_formula(self, seg, dur):
        formula = self._formula()
        formula.to_edge(UP, buff=2.2)
        self.play(Write(formula), run_time=1.2)
        self.wait(max(0.6, dur - 1.2))
        self.play(FadeOut(formula), run_time=0.4)

    def _add_harmonic(self, k: int, dur: float):
        """Shared logic for each harmonic segment."""
        color = TERM_COLORS[k % len(TERM_COLORS)]

        if k == 0:
            # First harmonic is also the first sum
            func = partial(fourier_sum, max_k=0)
            self.sum_graph = self._plot(func, color=YELLOW, width=4)
            self.play(Create(self.sum_graph), run_time=min(1.4, dur * 0.6))
            self.wait(max(0.3, dur - 1.4))
            return

        # Draw the new harmonic term (thin, color-coded)
        term_func = partial(harmonic_term, k=k)
        term_graph = self._plot(term_func, color=color, width=2)
        self.play(Create(term_graph), run_time=min(0.9, dur * 0.35))

        # Morph the cumulative sum into the next approximation
        new_func = partial(fourier_sum, max_k=k)
        new_sum = self._plot(new_func, color=YELLOW, width=4)
        self.play(
            ReplacementTransform(self.sum_graph, new_sum),
            FadeOut(term_graph),
            run_time=min(1.2, dur * 0.55),
        )
        self.sum_graph = new_sum
        self.wait(max(0.2, dur - 0.9 - 1.2))

    def _seg_harmonic_1(self, seg, dur):
        self._add_harmonic(0, dur)

    def _seg_harmonic_3(self, seg, dur):
        self._add_harmonic(1, dur)

    def _seg_harmonic_5(self, seg, dur):
        self._add_harmonic(2, dur)

    def _seg_harmonic_7(self, seg, dur):
        self._add_harmonic(3, dur)

    def _seg_harmonic_9(self, seg, dur):
        self._add_harmonic(4, dur)

    def _seg_payoff(self, seg, dur):
        ideal = self._dashed_square()
        self.play(Create(ideal), run_time=1.0)
        self.wait(max(0.5, dur - 1.0))

    def _seg_formula_reveal(self, seg, dur):
        formula = self._formula()
        formula.to_edge(UP, buff=2.2)
        box = SurroundingRectangle(formula, color=YELLOW, buff=0.25, corner_radius=0.1)
        self.play(Write(formula), Create(box), run_time=1.0)
        self.wait(max(0.5, dur - 1.0))
        self.play(FadeOut(formula), FadeOut(box), run_time=0.4)

    def _seg_cta(self, seg, dur):
        cta = Text("Follow for more math magic", font_size=42, color=WHITE, weight=BOLD)
        handle = Text("@MathInMotion", font_size=26, color=GRAY)
        cta.to_edge(UP, buff=1.2)
        handle.next_to(cta, DOWN, buff=0.3)
        self.play(FadeIn(cta), FadeIn(handle), run_time=0.6)
        self.wait(max(0.5, dur - 0.6))
        self.play(FadeOut(cta), FadeOut(handle), run_time=0.5)
