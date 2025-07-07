from manim import *
import numpy as np

from manim import *
import numpy as np

class EllipseFromFociCoverage(Scene):
    def construct(self):
        # Foci (trajectory endpoints)
        s = np.array([-2.5, -1.0, 0])
        e = np.array([2.5, 1.0, 0])
        kernel_radius = 0.4

        # Geometry
        c_vec = (e - s) / 2
        c = np.linalg.norm(c_vec)
        center = (s + e) / 2
        angle = np.arctan2(c_vec[1], c_vec[0])  # rotation angle

        # Length tracker (must be > 2c)
        L = ValueTracker(2 * c + 0.1)  # start just slightly larger

        # Test points
        num_pts = 50
        rng = np.random.default_rng(123)
        test_coords = 5 * (rng.random((num_pts, 2)) - 0.5)
        test_points = [Dot(point=[x, y, 0], radius=0.05) for x, y in test_coords]

        # Foci
        start_dot = Dot(s, color=WHITE)
        end_dot = Dot(e, color=WHITE)
        baseline = Line(s, e, color=WHITE, stroke_opacity=0.3)

        # Correct parametric ellipse construction
        def get_ellipse():
            a = L.get_value() / 2
            if a <= c:
                return VGroup()  # ellipse is undefined if L < 2c
            b = np.sqrt(a**2 - c**2)

            # Parametrize the ellipse
            theta = np.linspace(0, 2 * np.pi, 200)
            pts = np.stack([a * np.cos(theta), b * np.sin(theta), np.zeros_like(theta)], axis=-1)

            # Rotate and shift
            rot = rotation_matrix(angle)
            pts = pts @ rot.T + center
            return Polygon(*pts, color=YELLOW, stroke_width=2).set_opacity(0.3)

        def rotation_matrix(theta):
            return np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta),  np.cos(theta), 0],
                [0,              0,             1]
            ])

        ellipse = always_redraw(lambda: get_ellipse())

        # Coverage counter
        def update_colors():
            count = 0
            a = L.get_value() / 2
            if a <= c:
                for dot in test_points:
                    dot.set_color(RED)
                return 0
            for i, pt in enumerate(test_coords):
                x = np.array([pt[0], pt[1], 0])
                dist = np.linalg.norm(x - s) + np.linalg.norm(x - e)
                if dist <= L.get_value() + 2 * kernel_radius:
                    test_points[i].set_color(GREEN)
                    count += 1
                else:
                    test_points[i].set_color(RED)
            return count

        counter = always_redraw(lambda:
            Text(f"Covered: {update_colors()}/{num_pts}", font_size=36)
            .to_corner(UL)
        )

        self.add(baseline, start_dot, end_dot, ellipse, *test_points, counter)
        self.wait(1)
        self.play(L.animate.set_value(2 * c + 2.5), run_time=5)
        self.wait()






class MultiSegmentEllipseCoverage(Scene):
    def construct(self):
        kernel_radius = 0.4
        total_budget = 15

        # Waypoints
        V = [
            np.array([-5, -1, 0]),
            np.array([-1,  2, 0]),
            np.array([ 2, -1, 0]),
            np.array([ 5,  1.5, 0])
        ]
        dots = [Dot(v, color=WHITE) for v in V]
        lines = [Line(V[i], V[i+1], color=GRAY, stroke_opacity=0.3) for i in range(3)]

        # Segment lengths (start safely above min)
        min_lengths = [np.linalg.norm(V[i+1] - V[i]) for i in range(3)]
        initial_lengths = [l + 2.0 for l in min_lengths]  # Safe buffer
        L = [ValueTracker(l) for l in initial_lengths]

        # Normalize to total budget
        scale = total_budget / sum([l.get_value() for l in L])
        for l in L:
            l.set_value(l.get_value() * scale)

        # Test points
        rng = np.random.default_rng(42)
        num_pts = 80
        coords = 6 * (rng.random((num_pts, 2)) - 0.5)
        test_points = [Dot([x, y, 0], radius=0.05) for x, y in coords]

        # Helper to generate ellipse polygon safely
        def make_ellipses(s, e, L_tracker, kernel_radius):
            def ellipse(a, color, dashed=False):
                c_vec = (e - s) / 2
                c = np.linalg.norm(c_vec)
                if a <= c:
                    pts = np.array([
                        (s + e)/2 + 1e-3 * RIGHT,
                        (s + e)/2 + 1e-3 * UP,
                        (s + e)/2 - 1e-3 * RIGHT,
                        (s + e)/2 - 1e-3 * UP,
                    ])
                    return Polygon(*pts, color=color, stroke_width=0).set_opacity(0.01)

                b = np.sqrt(a**2 - c**2)
                theta = np.linspace(0, 2*np.pi, 200)
                pts = np.stack([a * np.cos(theta), b * np.sin(theta), np.zeros_like(theta)], axis=-1)
                angle = np.arctan2(c_vec[1], c_vec[0])
                rot = np.array([
                    [np.cos(angle), -np.sin(angle), 0],
                    [np.sin(angle),  np.cos(angle), 0],
                    [0, 0, 1]
                ])
                center = (s + e)/2
                pts = pts @ rot.T + center

                poly = Polygon(*pts, color=color, stroke_width=2)
                if dashed:
                    try:
                        # Try native dashed styling if available
                        poly.set_dashe([0.1, 0.1])
                    except AttributeError:
                        # Fallback: use lower opacity if dashed lines aren't supported
                        poly.set_opacity(0.15)
                else:
                    poly.set_opacity(0.25)
                return poly

            true_ellipse = always_redraw(lambda: ellipse(L_tracker.get_value() / 2, YELLOW, dashed=False))
            inflated_ellipse = always_redraw(lambda: ellipse((L_tracker.get_value() + 2 * kernel_radius) / 2, BLUE, dashed=True))
            return VGroup(true_ellipse, inflated_ellipse)



        # Define ellipses
        ellipses = [
    make_ellipses(V[0], V[1], L[0], kernel_radius),
    make_ellipses(V[1], V[2], L[1], kernel_radius),
    make_ellipses(V[2], V[3], L[2], kernel_radius),
]

        # Live coverage counter
        def update_colors():
            count = 0
            for i, pt in enumerate(coords):
                p = np.array([pt[0], pt[1], 0])
                covered = False
                for s, e, l in zip(V[:-1], V[1:], L):
                    d = np.linalg.norm(p - s) + np.linalg.norm(p - e)
                    if d <= l.get_value() + 2 * kernel_radius:
                        covered = True
                        break
                test_points[i].set_color(GREEN if covered else RED)
                if covered:
                    count += 1
            return count

        counter = always_redraw(lambda:
            Text(f"Covered: {update_colors()}/{num_pts}", font_size=32).to_corner(UL)
        )

        self.add(*dots, *lines)

        for ellipse_pair in ellipses:
            self.add(*ellipse_pair)  # unpack each VGroup into scene

        self.add(*test_points, counter)
        self.wait(1)

        # Animate redistribution of budget
        self.play(
            L[0].animate.set_value(L[0].get_value() - 0.4),
            L[1].animate.set_value(L[1].get_value() + 0.4),
            run_time=4
        )
        self.wait()
        self.play(
            L[1].animate.set_value(L[1].get_value() - 0.6),
            L[2].animate.set_value(L[2].get_value() + 0.6),
            run_time=4
        )
        self.wait()
        self.play(
            L[0].animate.set_value(L[0].get_value() + 0.5),
            L[2].animate.set_value(L[2].get_value() - 0.5),
            run_time=4
        )
        self.wait()
        self.play(
            L[1].animate.set_value(L[1].get_value() + 0.9),
            L[2].animate.set_value(L[2].get_value() - 0.9),
            run_time=4
        )

        self.wait()
