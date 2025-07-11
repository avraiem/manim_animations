from manim import *
import numpy as np

class SplineInEllipse(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        title = Text("Spline Contained Within Ellipse", font_size=30, color=WHITE).to_edge(UP)
        self.play(Write(title))

        # === Foci (start and end points of the spline) ===
        p1 = np.array([-4, -2, 0])
        p2 = np.array([4, 2, 0])
        foci_dots = VGroup(
            Dot(p1, color=RED),
            Dot(p2, color=RED)
        )
        self.play(FadeIn(foci_dots))

        # === Draw Spline (Bezier Cubic Example) ===
        control1 = np.array([-2, 2, 0])
        control2 = np.array([2, -3, 0])
        spline = CubicBezier(p1, control1, control2, p2).set_color(BLUE).set_stroke(width=4)
        control_dots = VGroup(Dot(control1, color=GRAY), Dot(control2, color=GRAY))
        control_lines = VGroup(
            Line(p1, control1, color=GRAY, stroke_opacity=0.5),
            Line(control1, control2, color=GRAY, stroke_opacity=0.5),
            Line(control2, p2, color=GRAY, stroke_opacity=0.5)
        )

        self.play(Create(control_lines), FadeIn(control_dots))
        self.play(Create(spline))

        # === Ellipse with foci p1 and p2, and major axis length L ===
        foci_dist = np.linalg.norm(p1 - p2)
        L = foci_dist + 2  # Make ellipse large enough to contain spline
        a = L / 2
        c = foci_dist / 2
        b = np.sqrt(a**2 - c**2)  # semi-minor axis

        center = (p1 + p2) / 2
        angle = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
        ellipse = Ellipse(width=2*a, height=2*b, color=ORANGE).move_to(center).rotate(angle)

        self.play(Create(ellipse), run_time=2)
        self.wait(2)

        # Label things (optional)
        a_label = Text("a", font_size=24, color=ORANGE).next_to(ellipse, RIGHT)
        f1_label = Text("Start", font_size=20, color=RED).next_to(p1, LEFT)
        f2_label = Text("End", font_size=20, color=RED).next_to(p2, RIGHT)
        self.play(FadeIn(a_label, f1_label, f2_label))

        self.wait(3)
