from manim import *

class GraphPathsScene(Scene):
    def construct(self):
        # Define five fixed waypoints (2D positions)
        waypoints = [
            LEFT * 4 + UP * 1,
            RIGHT * 2 + UP * 1,
            RIGHT * 3 + DOWN * 2,
            RIGHT * 2 + UP * 3
        ]

        # Draw waypoints as blue dots
        dots = [Dot(point, radius=0.12, color=BLUE) for point in waypoints]
        for dot in dots:
            self.add(dot)

        # Define 3 curved connections (as triplets or pairs of waypoints)
        paths = [
            (waypoints[0], waypoints[1]),  # curve 1
            (waypoints[1], waypoints[3]),  # curve 2
            (waypoints[3], waypoints[2])   # curve 3
        ]

        colors = [RED, GREEN, BLUE]

        for (start, end), color in zip(paths, colors):
            # Use CubicBezier or a QuadraticCurve approximation
            ctrl_offset = 0.5 * UP + 0.5 * RIGHT  # adjust for curvature
            mid = (start + end) / 2 + ctrl_offset
            curve = CubicBezier(start, mid, mid, end).set_color(color).set_stroke(width=4)
            self.play(Create(curve), run_time=2)
        
        self.wait(2)
