from manim import *

class CoverageBallVisualization(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # Parameters
        measurement_loc = np.array([0, 0, 0])
        r_kernel = 2

        # 1. Measurement point
        meas_dot = Dot(point=measurement_loc, color=RED, radius=0.1)
        self.play(FadeIn(meas_dot), run_time=1)

        # 2. Coverage circle
        coverage_circle = Circle(radius=r_kernel, color=RED).move_to(measurement_loc)
        self.play(Create(coverage_circle), run_time=1)

        # 3. Test points
        test_points = [
            np.array([0.5, 1, 0]),
            np.array([-1.5, -0.5, 0]),
            np.array([1.8, 0.2, 0]),
            np.array([-2.2, 1.5, 0]),   # outside
            np.array([2.5, 0.3, 0]),    # outside
            np.array([0.7, -1.7, 0])
        ]

        dots = VGroup()
        for p in test_points:
            color = GREEN if np.linalg.norm(p - measurement_loc) <= r_kernel else GRAY
            dot = Dot(point=p, color=color).scale(0.6)
            dots.add(dot)

        self.play(FadeIn(dots), run_time=1.5)
        self.wait(2)

        # Optional: Label covered vs not covered
        covered_label = Text("Covered", color=GREEN, font_size=28).to_edge(LEFT).shift(UP)
        not_covered_label = Text("Not Covered", color=GRAY, font_size=28).to_edge(LEFT).shift(DOWN)
        self.play(FadeIn(covered_label), FadeIn(not_covered_label), run_time=1)

        self.wait(3)
