"""3D Manim scene: plotting the point (3, 2, 5) in space.

Output is a vertical 1080x1920 Shorts-style video with camera moves,
a moving trace dot, dashed coordinate projections, and an orbiting reveal.
"""
from __future__ import annotations

import json
from pathlib import Path

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


# Point we plot
P_COORDS = (3, 2, 5)

# Palette
AXIS_X = RED
AXIS_Y = GREEN
AXIS_Z = BLUE
POINT_COLOR = YELLOW
TRAIL_COLOR = YELLOW
PROJ_COLOR = GRAY
LABEL_COLOR = WHITE


class PlotPoint3D(ThreeDScene):
    def construct(self):
        config_path = Path(__file__).resolve().parent / "config.json"
        CONFIG = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        self.segments = CONFIG.get("segments", [])

        # Common 3D setup
        self._build_axes()
        self.moving_dot = Dot3D(
            point=self.axes.c2p(0, 0, 0),
            radius=0.12,
            color=POINT_COLOR,
            resolution=(6, 6),
        )
        # Keep it out of the scene until we need it
        self.moving_dot.set_opacity(0)
        self.add(self.moving_dot)

        for seg in self.segments:
            stype = seg["type"]
            dur = float(seg.get("duration", 3.0))
            getattr(self, f"_seg_{stype}")(seg, dur)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _build_axes(self):
        self.axes = ThreeDAxes(
            x_range=(0, 6, 1),
            y_range=(0, 6, 1),
            z_range=(0, 6, 1),
            x_length=6.5,
            y_length=6.5,
            z_length=6.5,
            axis_config={
                "include_tip": True,
                "tip_width": 0.25,
                "tip_height": 0.25,
                "include_numbers": False,
            },
            x_axis_config={"color": AXIS_X},
            y_axis_config={"color": AXIS_Y},
            z_axis_config={"color": AXIS_Z},
        )

        # Floor grid on the xy-plane
        self.floor_grid = NumberPlane(
            x_range=(0, 6, 1),
            y_range=(0, 6, 1),
            x_length=6.5,
            y_length=6.5,
            background_line_style={"stroke_color": "#222222", "stroke_width": 1},
            faded_line_style={"stroke_color": "#1a1a1a", "stroke_width": 0.5},
            faded_line_ratio=1,
        )

        # Axis labels that always face the camera
        x_label = Text("x", color=AXIS_X, font_size=32)
        y_label = Text("y", color=AXIS_Y, font_size=32)
        z_label = Text("z", color=AXIS_Z, font_size=32)
        self.labels = self.axes.get_axis_labels(x_label, y_label, z_label)

    def _point(self, x, y, z):
        return self.axes.c2p(x, y, z)

    def _make_label(self, text, coords, color=LABEL_COLOR, font_size=36):
        """Create a 3D label that always faces the camera."""
        label = Text(text, color=color, font_size=font_size)
        label.move_to(self._point(*coords))
        self.add_fixed_orientation_mobjects(label)
        return label

    def _move_dot(self, start_coords, end_coords, run_time, after_updaters=None):
        """Animate the moving dot from start to end with a live trail."""
        start = self._point(*start_coords)
        end = self._point(*end_coords)
        self.moving_dot.move_to(start)
        self.moving_dot.set_opacity(1)

        # Initialize the trail with two distinct points so Manim keeps a valid
        # (2, 3) points array even when start and end temporarily coincide.
        tiny = 0.01 * (end - start)
        trail = Line(start, start + tiny, color=TRAIL_COLOR, stroke_width=4)
        self.add(trail)

        tracker = ValueTracker(0)

        def update_dot(mob):
            t = tracker.get_value()
            mob.move_to(start + t * (end - start))

        def update_trail(mob):
            mob.put_start_and_end_on(start, self.moving_dot.get_center())

        self.moving_dot.add_updater(update_dot)
        trail.add_updater(update_trail)

        self.play(tracker.animate.set_value(1), run_time=run_time, rate_func=linear)

        self.moving_dot.remove_updater(update_dot)
        trail.remove_updater(update_trail)
        if after_updaters:
            after_updaters()

    # -----------------------------------------------------------------------
    # Segments
    # -----------------------------------------------------------------------
    def _seg_title(self, seg, dur):
        title = Text("Plot a Point in Space", font_size=52, color=WHITE, weight=BOLD)
        handle = Text("@learningverse123", font_size=28, color=GRAY)
        title.to_edge(UP, buff=0.8)
        handle.to_edge(DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(title, handle)

        self.play(FadeIn(title), FadeIn(handle), run_time=0.8)
        self.wait(max(0.4, dur - 0.8))
        self.play(FadeOut(title), FadeOut(handle), run_time=0.4)

    def _seg_axes(self, seg, dur):
        # Start from a nice angle
        self.set_camera_orientation(phi=70 * DEGREES, theta=-110 * DEGREES, zoom=0.85)

        self.play(FadeIn(self.floor_grid), run_time=0.8)
        self.play(Create(self.axes), run_time=1.2)
        self.add_fixed_orientation_mobjects(*self.labels)

        # A short camera move to show the 3D setup
        self.move_camera(phi=70 * DEGREES, theta=-80 * DEGREES, run_time=1.5, rate_func=smooth)

        wait = max(0.3, dur - 2.0 - 1.5)
        if wait > 0:
            self.wait(wait)

    def _seg_coords(self, seg, dur):
        formula = Text("(x , y , z)", font_size=56, color=WHITE)
        formula.to_edge(UP, buff=1.2)
        self.add_fixed_in_frame_mobjects(formula)

        self.play(FadeIn(formula), run_time=0.6)
        self.wait(max(0.5, dur - 0.6))
        self.play(FadeOut(formula), run_time=0.3)

    def _seg_plot_x(self, seg, dur):
        # Trail from origin to (3,0,0)
        self._move_dot((0, 0, 0), P_COORDS[:1] + (0, 0), run_time=max(1.5, dur * 0.6))

        # Mark the x-coordinate
        x_label = self._make_label("3", (3, 0, 0), color=AXIS_X, font_size=36)
        x_label.shift(DOWN * 0.4 + LEFT * 0.2)
        self.play(FadeIn(x_label), run_time=0.4)

        wait = dur - max(1.5, dur * 0.6) - 0.4
        if wait > 0:
            self.wait(wait)

    def _seg_plot_y(self, seg, dur):
        # Move from (3,0,0) to (3,2,0)
        self._move_dot(P_COORDS[:1] + (0, 0), P_COORDS[:2] + (0,), run_time=max(1.5, dur * 0.6))

        # Dashed projection to the x-axis
        proj_x = DashedLine(
            self._point(3, 2, 0),
            self._point(3, 0, 0),
            color=PROJ_COLOR,
            stroke_width=2,
        )
        y_label = self._make_label("2", (3, 2, 0), color=AXIS_Y, font_size=36)
        y_label.shift(LEFT * 0.5 + DOWN * 0.3)

        self.play(Create(proj_x), FadeIn(y_label), run_time=0.5)

        wait = dur - max(1.5, dur * 0.6) - 0.5
        if wait > 0:
            self.wait(wait)

    def _seg_plot_z(self, seg, dur):
        # Move from (3,2,0) up to (3,2,5)
        self._move_dot(P_COORDS[:2] + (0,), P_COORDS, run_time=max(1.5, dur * 0.6))

        # Vertical dashed projection down to the xy-plane
        proj_z = DashedLine(
            self._point(3, 2, 5),
            self._point(3, 2, 0),
            color=PROJ_COLOR,
            stroke_width=2,
        )
        z_label = self._make_label("5", (3, 2, 5), color=AXIS_Z, font_size=36)
        z_label.shift(LEFT * 0.6 + UP * 0.4)

        self.play(Create(proj_z), FadeIn(z_label), run_time=0.5)

        wait = dur - max(1.5, dur * 0.6) - 0.5
        if wait > 0:
            self.wait(wait)

    def _seg_reveal(self, seg, dur):
        # Final point in bright yellow with a pulse
        self.moving_dot.set_color(POINT_COLOR)
        self.play(self.moving_dot.animate.scale(1.6), run_time=0.4)
        self.play(self.moving_dot.animate.scale(1 / 1.6), run_time=0.3)

        # Add the remaining floor projection to the y-axis
        proj_y = DashedLine(
            self._point(3, 2, 0),
            self._point(0, 2, 0),
            color=PROJ_COLOR,
            stroke_width=2,
        )

        # Coordinate box edges: subtle gray lines completing the prism
        edges = VGroup(
            Line(self._point(3, 0, 0), self._point(3, 0, 5), color="#333333", stroke_width=2),
            Line(self._point(0, 2, 0), self._point(0, 2, 5), color="#333333", stroke_width=2),
            Line(self._point(3, 0, 5), self._point(3, 2, 5), color="#333333", stroke_width=2),
            Line(self._point(0, 2, 5), self._point(3, 2, 5), color="#333333", stroke_width=2),
            Line(self._point(0, 0, 5), self._point(3, 0, 5), color="#333333", stroke_width=2),
            Line(self._point(0, 0, 5), self._point(0, 2, 5), color="#333333", stroke_width=2),
        )

        final_label = Text("(3, 2, 5)", font_size=48, color=POINT_COLOR, weight=BOLD)
        final_label.next_to(self.moving_dot, UP + RIGHT, buff=0.3)
        self.add_fixed_orientation_mobjects(final_label)

        self.play(
            Create(proj_y),
            LaggedStart(*[Create(e) for e in edges], lag_ratio=0.2, run_time=1.2),
            FadeIn(final_label),
            run_time=1.5,
        )

        # A brief pulse + short camera shift for the reveal
        self.play(self.moving_dot.animate.scale(1.3), run_time=0.4)
        self.play(self.moving_dot.animate.scale(1 / 1.3), run_time=0.3)
        self.move_camera(
            phi=65 * DEGREES,
            theta=-60 * DEGREES,
            run_time=1.2,
            rate_func=smooth,
        )

        wait = dur - 1.5 - 0.7 - 1.2
        if wait > 0:
            self.wait(wait)

    def _seg_outro(self, seg, dur):
        title = Text("Plot a Point in Space", font_size=44, color=WHITE, weight=BOLD)
        handle = Text("@learningverse123", font_size=26, color=GRAY)
        title.to_edge(UP, buff=0.9)
        handle.to_edge(DOWN, buff=0.9)
        self.add_fixed_in_frame_mobjects(title, handle)

        self.play(FadeIn(title), FadeIn(handle), run_time=0.7)
        self.wait(max(0.5, dur - 0.7))
        self.play(FadeOut(title), FadeOut(handle), run_time=0.5)
