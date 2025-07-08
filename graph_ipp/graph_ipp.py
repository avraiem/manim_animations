import numpy as np
from manim import *
from PIL import Image
import matplotlib.pyplot as plt
class GraphIPPPathSelection(Scene):
    def construct(self):
        title = Text("Informative Path Planning on a Graph", font_size=30).to_edge(UP)
        self.play(Write(title))

        # Graph layout: manually placed for illustration
        nodes = {
            "A": [-4, -2, 0],
            "B": [-2,  0, 0],
            "C": [ 0,  2, 0],
            "D": [ 2,  0, 0],
            "E": [ 4, -2, 0],
            "F": [ 0, -1.5, 0]
        }

        edges = [
            ("A", "B"),
            ("B", "C"),
            ("C", "D"),
            ("D", "E"),
            ("B", "F"),
            ("F", "D"),
        ]

        # Draw graph nodes
        node_dots = {
            name: Dot(point=coords, color=WHITE).scale(0.8)
            for name, coords in nodes.items()
        }

        node_labels = {
            name: Text(name, font_size=24).next_to(dot, UP, buff=0.2)
            for name, dot in node_dots.items()
        }

        for dot in node_dots.values():
            self.add(dot)
        for label in node_labels.values():
            self.add(label)

        # Draw edges
        for (u, v) in edges:
            line = Line(node_dots[u].get_center(), node_dots[v].get_center(), color=GRAY)
            self.add(line)

        # Test points (randomly placed nearby)
        test_points = [
            [-3, 1, 0], [-1, 2.2, 0], [1, 1.8, 0], [3, -1, 0], [0.5, -2, 0], [-2.5, -0.5, 0]
        ]
        test_dots = VGroup(*[
            Dot(point=coords, color=BLUE).scale(0.5) for coords in test_points
        ])
        self.play(FadeIn(test_dots))
        self.wait(1)

        # Selected path (A → B → F → D → E)
        selected_path = ["A", "B", "F", "D", "E"]
        path_lines = VGroup()
        for i in range(len(selected_path) - 1):
            u = selected_path[i]
            v = selected_path[i + 1]
            path_lines.add(Line(
                node_dots[u].get_center(),
                node_dots[v].get_center(),
                color=RED,
                stroke_width=5
            ))

        self.play(Create(path_lines))
        self.wait(1)

        # Highlight measurement locations (vertices on path)
        measurement_dots = VGroup(*[
            node_dots[n].copy().set_color(RED).scale(1.2)
            for n in selected_path
        ])
        self.play(FadeIn(measurement_dots))
        self.wait(1)

        # Optional: draw coverage circles (range)
        coverage_circles = VGroup(*[
            Circle(radius=1.2, color=RED, stroke_opacity=0.5).move_to(node_dots[n])
            for n in selected_path
        ])
        self.play(Create(coverage_circles))

        label = Text("Only path vertices collect data", font_size=24).next_to(test_dots, DOWN, buff=1)
        self.play(Write(label))

        self.wait(2)


class GraphIPPPathSelection2(Scene):
    def construct(self):
        title = Text("Informative Path Planning on a Graph", font_size=30).to_edge(UP)
        self.play(Write(title), run_time=2)

        # === Graph Layout ===
        nodes = {
            "A": [-4, -2, 0],
            "B": [-2,  0, 0],
            "C": [ 0,  2, 0],
            "D": [ 2,  0, 0],
            "E": [ 4, -2, 0],
            "F": [ 0, -1.5, 0]
        }

        edges = [
            ("A", "B"),
            ("B", "C"),
            ("C", "D"),
            ("D", "E"),
            ("B", "F"),
            ("F", "D"),
        ]

        # === GP Variance Heatmap ===
        x_vals = np.linspace(-5, 5, 100)
        y_vals = np.linspace(-3, 3, 100)
        xx, yy = np.meshgrid(x_vals, y_vals)

        # Fake GP variance: high variance far from (0, 0)
        variance = np.exp(-0.2 * ((xx)**2 + (yy)**2))


        plt.imshow(variance, extent=[-5.5, 5.5, -3.5, 3.5], origin='lower', cmap='viridis')

        plt.axis("off")
        plt.savefig("variance_map.png", bbox_inches="tight", pad_inches=0)
        plt.close()

        heatmap = ImageMobject("variance_map.png")
        heatmap.set_width(11)  # Wider to match the X-range
        heatmap.set_height(7)  # Taller to match the Y-range
        heatmap.set_opacity(0.6)
        self.play(FadeIn(heatmap), run_time=1)
        self.bring_to_back(heatmap)
        # === Nodes and Edges ===
        node_dots = {name: Dot(point=coords, color=WHITE).scale(0.8) for name, coords in nodes.items()}
        node_labels = {name: Text(name, font_size=24).next_to(dot, UP, buff=0.2) for name, dot in node_dots.items()}

        for dot in node_dots.values():
            self.play(FadeIn(dot), run_time=0.4)
        for label in node_labels.values():
            self.play(FadeIn(label), run_time=0.2)

        for u, v in edges:
            edge = Line(node_dots[u].get_center(), node_dots[v].get_center(), color=GRAY)
            self.play(Create(edge), run_time=0.5)

        # === Test points ===
        test_points = [[-3, 1, 0], [-1, 2.2, 0], [1, 1.8, 0], [3, -1, 0], [0.5, -2, 0], [-2.5, -0.5, 0]]
        test_dots = VGroup(*[Dot(p, color=BLUE).scale(0.5) for p in test_points])
        self.play(FadeIn(test_dots), run_time=1)

        self.wait(1)

        # === Selected Path ===
        selected_path = ["A", "B", "F", "D", "E"]
        path_lines = VGroup()
        for i in range(len(selected_path) - 1):
            u, v = selected_path[i], selected_path[i+1]
            path_lines.add(Line(node_dots[u].get_center(), node_dots[v].get_center(), color=RED, stroke_width=6))

        self.play(Create(path_lines), run_time=2)

        # === Measurement nodes ===
        measurement_dots = VGroup(*[
            node_dots[n].copy().set_color(RED).scale(1.2)
            for n in selected_path
        ])
        self.play(FadeIn(measurement_dots), run_time=1.5)

        # === Coverage Circles ===
        coverage = VGroup(*[
            Circle(radius=1.2, color=RED, stroke_opacity=0.5).move_to(node_dots[n])
            for n in selected_path
        ])
        self.play(Create(coverage), run_time=2)

        label = Text("Only path vertices collect data", font_size=24).next_to(test_dots, DOWN, buff=1)
        self.play(Write(label), run_time=2)
        self.wait(3)
