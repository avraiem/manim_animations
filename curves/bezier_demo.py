from manim import *

class BezierCurveDemo(Scene):
    def construct(self):
        # Initial control points
        points = [LEFT*4 + DOWN, LEFT*2 + UP, RIGHT*2 + DOWN, RIGHT*4 + UP]
        ctrl_dots = [Dot(point=p, color=BLUE) for p in points]
        ctrl_group = VGroup(*ctrl_dots)

        # Connect control points
        polyline = always_redraw(lambda: VGroup(
    DashedLine(ctrl_dots[0].get_center(), ctrl_dots[1].get_center(), color=GRAY),
    DashedLine(ctrl_dots[1].get_center(), ctrl_dots[2].get_center(), color=GRAY),
    DashedLine(ctrl_dots[2].get_center(), ctrl_dots[3].get_center(), color=GRAY)
))

        # Bézier curve
        curve = always_redraw(lambda: CubicBezier(ctrl_dots[0].get_center(),
                                                  ctrl_dots[1].get_center(),
                                                  ctrl_dots[2].get_center(),
                                                  ctrl_dots[3].get_center()).set_color(YELLOW))

        self.add(polyline, curve, *ctrl_dots)

        # Animate movement of control points
        self.play(ctrl_dots[1].animate.shift(UP*2 + RIGHT),
                  ctrl_dots[2].animate.shift(DOWN*2 + LEFT),
                  run_time=3)
        self.wait()



class BezierCurveGlobalEffect(Scene):
    def construct(self):
        # Control points (initial)
        ctrl_points = [LEFT*4 + DOWN, LEFT*2 + UP, RIGHT*2 + DOWN, RIGHT*4 + UP]
        ctrl_dots = [Dot(p, color=BLUE) for p in ctrl_points]
        ctrl_labels = [Text(f"P{i}", font_size=24).next_to(dot, UP) for i, dot in enumerate(ctrl_dots)]
        ctrl_group = VGroup(*ctrl_dots)

        # Control polygon (lines between control points)
        control_lines = always_redraw(lambda: VGroup(
            *[DashedLine(ctrl_dots[i].get_center(), ctrl_dots[i+1].get_center(), color=GRAY)
              for i in range(len(ctrl_dots)-1)]
        ))

        # Bézier curve (updates as control points move)
        bezier_curve = always_redraw(lambda:
            CubicBezier(*[dot.get_center() for dot in ctrl_dots]).set_color(YELLOW)
        )

        self.add(*ctrl_dots, *ctrl_labels, control_lines, bezier_curve)

        self.wait(1)

        # Animate: Move only one control point and watch whole curve change
        self.play(ctrl_dots[1].animate.shift(UP*2 + RIGHT), run_time=3)
        self.wait(1)
        self.play(ctrl_dots[1].animate.shift(DOWN*2 + LEFT), run_time=3)
        self.wait()