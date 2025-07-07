from manim import *
import numpy as np
from scipy.interpolate import BSpline

class BSplineDemo(Scene):
    def construct(self):
        # Define control points
        ctrl_pts = np.array([[-4, -1, 0], [-2, 2, 0], [0, -2, 0], [2, 2, 0], [4, 0, 0]])
        dots = [Dot(point=pt, color=BLUE) for pt in ctrl_pts]

        # B-spline basis (cubic, clamped)
        degree = 3
        n_ctrl = len(ctrl_pts)
        n_knots = n_ctrl + degree + 1
        knots = np.concatenate(([0]*(degree+1), np.linspace(0, 1, n_knots - 2*degree - 2), [1]*(degree+1)))
        spline = BSpline(knots, ctrl_pts, degree)

        def get_spline_curve():
            t_vals = np.linspace(0, 1, 100)
            points = spline(t_vals)
            return VMobject().set_points_smoothly([np.array(p) for p in points]).set_color(ORANGE)

        spline_curve = always_redraw(lambda: get_spline_curve())

        self.add(*dots, spline_curve)

        # Animate control point movement
        self.play(dots[1].animate.shift(UP*1.5 + RIGHT),
                  dots[2].animate.shift(DOWN*1.5 + LEFT),
                  run_time=3)
        self.wait()




class BSplineLocalEffect(Scene):
    def construct(self):
        # Control points (as ValueTrackers)
        ctrl_vals = [
            [-4, -1],
            [-2,  2],
            [ 0, -2],
            [ 2,  2],
            [ 4,  0]
        ]
        trackers = [ValueTracker(x) for x, y in ctrl_vals]
        trackers_y = [ValueTracker(y) for x, y in ctrl_vals]

        def get_control_points():
            return [np.array([x.get_value(), y.get_value(), 0.0]) for x, y in zip(trackers, trackers_y)]

        # Create Dots bound to the trackers
        dots = [always_redraw(lambda x=x, y=y: Dot(point=np.array([x.get_value(), y.get_value(), 0.0]), color=BLUE))
                for x, y in zip(trackers, trackers_y)]

        labels = [Text(f"P{i}", font_size=24).next_to(dot, UP) for i, dot in enumerate(dots)]
        self.add(*dots, *labels)

        # B-spline setup
        k = 3
        n = len(dots)
        num_knots = n + k + 1
        internal = np.linspace(0, 1, num_knots - 2*k)
        knots = np.concatenate(([0]*k, internal, [1]*k))

        def build_bspline():
            ctrl_pts = np.array(get_control_points())
            spline = BSpline(knots, ctrl_pts, k)
            t_vals = np.linspace(0, 1, 200)
            points = [spline(t) for t in t_vals]
            return VMobject().set_points_smoothly(points).set_color(ORANGE)

        spline = always_redraw(lambda: build_bspline())
        self.add(spline)

        self.wait(1)

        # Animate: move one control point (dot 2)
        self.play(
            trackers[2].animate.increment_value(-1.5),
            trackers_y[2].animate.increment_value(-1.0),
            run_time=3
        )
        self.wait(1)
        self.play(
            trackers[2].animate.increment_value(1.5),
            trackers_y[2].animate.increment_value(1.0),
            run_time=3
        )

        #animate: move another control point (dot 3)
        self.play(
            trackers[3].animate.increment_value(1.5),
            trackers_y[3].animate.increment_value(1.0),
            run_time=3
        )
        self.wait(1)
        self.play(
            trackers[3].animate.increment_value(-1.5),
            trackers_y[3].animate.increment_value(-1.0),
            run_time=3
        )
        self.wait()
