from manim import *
import numpy as np
from scipy.spatial.distance import cdist

config.pixel_height = 720
config.pixel_width = 1280
config.frame_height = 6
config.frame_width = 12

def rbf_kernel(x1, x2, lengthscale=0.2, sigma_f=1.0):
    sqdist = cdist(x1, x2, 'sqeuclidean')
    return sigma_f ** 2 * np.exp(-0.5 / lengthscale ** 2 * sqdist)

def sample_gp(x, kernel_fn, n_samples=3):
    K = kernel_fn(x, x)
    return np.random.multivariate_normal(mean=np.zeros(len(x)), cov=K + 1e-6 * np.eye(len(x)), size=n_samples)

class GP1DPrior(Scene):
    def construct(self):
        title = Text("Gaussian Process Prior", font_size=36).to_edge(UP)
        self.play(Write(title))

        # GP prior definition
        x_vals = np.linspace(0, 1, 100).reshape(-1, 1)
        kernel = rbf_kernel
        cov = kernel(x_vals, x_vals)
        std = np.sqrt(np.diag(cov))
        mean = np.zeros_like(x_vals).flatten()

       # Use this one axes for all plots
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-3, 3, 1],
            x_length=10,
            y_length=5,
            tips=False
        ).move_to(DOWN)

        # Sample curves
        for sample in sample_gp(x_vals, kernel, n_samples=4):
            self.play(Create(axes.plot_line_graph(x_vals.flatten(), sample)))

        # Mean + confidence band
        mean = np.zeros_like(x_vals).flatten()
        upper = mean + 2 * std
        lower = mean - 2 * std

        # Polygon fill for confidence band
        upper_pts = [axes.c2p(x_vals[i, 0], upper[i]) for i in range(len(x_vals))]
        lower_pts = [axes.c2p(x_vals[i, 0], lower[i]) for i in reversed(range(len(x_vals)))]
        band = Polygon(*upper_pts, *lower_pts, color=BLUE_E, fill_opacity=0.3, stroke_width=0)

        self.play(FadeIn(band))
        self.play(Create(axes.plot_line_graph(x_vals.flatten(), mean, line_color=YELLOW)))
        self.wait(2)


class GP1DPosteriorSameCov(Scene):
    def construct(self):
        title = Text("Posterior Variance is Independent of Measurement Value", font_size=30).to_edge(UP)
        self.play(Write(title))

        # Setup
        x_vals = np.linspace(0, 1, 100).reshape(-1, 1)
        x_obs = np.array([[0.3]])
        kernel = rbf_kernel

        # Compute posterior variance (same for all)
        K = kernel(x_vals, x_vals)
        K_s = kernel(x_vals, x_obs)
        K_ss = kernel(x_obs, x_obs) + 1e-6 * np.eye(1)
        K_inv = np.linalg.inv(K_ss)
        post_cov = K - K_s @ K_inv @ K_s.T
        std = np.sqrt(np.diag(post_cov))

        # Plot axes and uncertainty band
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-3, 3, 1],
            x_length=10,
            y_length=5,
            tips=False
        ).move_to(DOWN)

        self.play(Create(axes))

        # Draw confidence band (±2 std)
        x_flat = x_vals.flatten()
        upper = std * 2
        lower = -std * 2

        band = axes.get_area(
            axes.plot_line_graph(x_flat, upper, line_color=BLUE_E),
            axes.plot_line_graph(x_flat, lower, line_color=BLUE_E),
            color=BLUE_E, opacity=0.3
        )

        self.play(FadeIn(band))

        # Show three different measurement values
        for meas_val in [-1.0, 0.0, 1.0]:
            mu_post = K_s.T @ K_inv @ np.array([meas_val])

            posterior_mean = mu_post.flatten()
            mean_graph = axes.plot_line_graph(x_flat, posterior_mean, line_color=YELLOW)

            dot = Dot(point=axes.c2p(x_obs[0, 0], meas_val), color=RED)

            self.play(FadeIn(dot), Create(mean_graph), run_time=1.5)
            self.wait(1)
            self.play(FadeOut(mean_graph), FadeOut(dot))

        self.wait(2)



class PosteriorAfterSensors(Scene):
    def construct(self):
        title = Text("Posterior After Sparse Sensor Placement", font_size=30).to_edge(UP)
        self.play(Write(title))

        # Setup domain
        x_vals = np.linspace(0, 1, 100).reshape(-1, 1)
        x = x_vals.flatten()

        # Sensor locations (subset)
        sensor_locs = np.array([[0.15], [0.4], [0.65], [0.85]])
        y_obs = np.zeros(len(sensor_locs))  # fixed value for showing variance-only effect

        # Compute GP posterior (mean + std)
        kernel = rbf_kernel
        K = kernel(x_vals, x_vals)
        K_s = kernel(x_vals, sensor_locs)
        K_ss = kernel(sensor_locs, sensor_locs) + 1e-6 * np.eye(len(sensor_locs))
        K_inv = np.linalg.inv(K_ss)

        mean_post = K_s @ K_inv @ y_obs
        cov_post = K - K_s @ K_inv @ K_s.T
        std_post = np.sqrt(np.clip(np.diag(cov_post), a_min=0, a_max=None))

        # Axes
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2.5, 2.5, 1],
            x_length=10,
            y_length=5,
            tips=False
        ).shift(DOWN)

        self.play(Create(axes))

        # Confidence band (posterior)
        upper = mean_post + 2 * std_post
        lower = mean_post - 2 * std_post

        upper_points = [axes.c2p(x[i], upper[i]) for i in range(len(x))]
        lower_points = [axes.c2p(x[i], lower[i]) for i in reversed(range(len(x)))]
        band = Polygon(*upper_points, *lower_points, color=BLUE_E, fill_opacity=0.3, stroke_width=0)

        mean_curve = axes.plot_line_graph(x, mean_post, line_color=YELLOW)

        self.play(FadeIn(band), Create(mean_curve))

        # Show sensor dots
        sensor_dots = VGroup(*[
            Dot(color=RED).move_to(axes.c2p(xi[0], y_obs[i])) for i, xi in enumerate(sensor_locs)
        ])
        self.play(FadeIn(sensor_dots))

        label = Text("Variance drops near sensor locations", font_size=24).next_to(axes, UP)
        self.play(Write(label))

        self.wait(2)


class PriorToPosteriorWithSensors(Scene):
    def construct(self):
        title = Text("Posterior Updates After Sparse Sensor Placement", font_size=30).to_edge(UP)
        self.play(Write(title))

        # Setup domain
        x_vals = np.linspace(0, 1, 100).reshape(-1, 1)
        x = x_vals.flatten()

        # Define kernel
        kernel = rbf_kernel
        cov_prior = kernel(x_vals, x_vals)
        std_prior = np.sqrt(np.diag(cov_prior))
        mean_prior = np.zeros_like(x)

        # Axes
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2.5, 2.5, 1],
            x_length=10,
            y_length=5,
            tips=False
        ).shift(DOWN)

        self.play(Create(axes))

        # Step 1: Show Prior Band
        upper_prior = mean_prior + 2 * std_prior
        lower_prior = mean_prior - 2 * std_prior
        upper_pts = [axes.c2p(x[i], upper_prior[i]) for i in range(len(x))]
        lower_pts = [axes.c2p(x[i], lower_prior[i]) for i in reversed(range(len(x)))]
        prior_band = Polygon(*upper_pts, *lower_pts, color=BLUE_E, fill_opacity=0.3, stroke_width=0)
        mean_curve = axes.plot_line_graph(x, mean_prior, line_color=YELLOW)

        self.play(FadeIn(prior_band), Create(mean_curve))

        # Step 2: Add test points
        test_points = np.linspace(0.05, 0.95, 12)
        test_dots = VGroup(*[
            Dot(color=BLUE).scale(0.6).move_to(axes.c2p(tx, -2.2)) for tx in test_points
        ])
        self.play(FadeIn(test_dots))
        self.wait(1)

        # Step 3: Place sparse sensors
        sensor_locs = np.array([[0.15], [0.4], [0.65], [0.85]])
        y_obs = np.zeros(len(sensor_locs))  # fixed values

        sensor_dots = VGroup(*[
            Dot(color=RED).move_to(axes.c2p(sx[0], 0)) for sx in sensor_locs
        ])
        sensor_labels = VGroup(*[
            Text(f"{sx[0]:.2f}", font_size=20).next_to(axes.c2p(sx[0], 0), UP)
            for sx in sensor_locs
        ])
        self.play(FadeIn(sensor_dots), FadeIn(sensor_labels))
        self.wait(1)

        # Step 4: Transition to Posterior
        self.play(FadeOut(prior_band), FadeOut(mean_curve))

        # Compute posterior
        K = kernel(x_vals, x_vals)
        K_s = kernel(x_vals, sensor_locs)
        K_ss = kernel(sensor_locs, sensor_locs) + 1e-6 * np.eye(len(sensor_locs))
        K_inv = np.linalg.inv(K_ss)

        mean_post = K_s @ K_inv @ y_obs
        cov_post = K - K_s @ K_inv @ K_s.T
        std_post = np.sqrt(np.clip(np.diag(cov_post), a_min=0, a_max=None))

        upper_post = mean_post + 2 * std_post
        lower_post = mean_post - 2 * std_post
        upper_pts_post = [axes.c2p(x[i], upper_post[i]) for i in range(len(x))]
        lower_pts_post = [axes.c2p(x[i], lower_post[i]) for i in reversed(range(len(x)))]
        post_band = Polygon(*upper_pts_post, *lower_pts_post, color=GREEN_E, fill_opacity=0.3, stroke_width=0)
        post_curve = axes.plot_line_graph(x, mean_post, line_color=GREEN)

        self.play(FadeIn(post_band), Create(post_curve))

        label = Text("Uncertainty drops near sensors", font_size=24).next_to(axes, UP)
        self.play(Write(label))
        self.wait(2)



class ExactSensorCoverage(Scene):
    def construct(self):
        title = Text("Full Coverage: #Sensors = #Test Points", font_size=30).to_edge(UP)
        self.play(Write(title))

        # Setup domain
        x_vals = np.linspace(0, 1, 100).reshape(-1, 1)
        x = x_vals.flatten()

        # Define test/sensor locations
        sensor_locs = np.array([[0.1], [0.35], [0.6], [0.85]])
        y_obs = np.zeros(len(sensor_locs))  # again, value doesn't matter

        # GP posterior with full coverage
        kernel = rbf_kernel
        K = kernel(x_vals, x_vals)
        K_s = kernel(x_vals, sensor_locs)
        K_ss = kernel(sensor_locs, sensor_locs) + 1e-6 * np.eye(len(sensor_locs))
        K_inv = np.linalg.inv(K_ss)

        mean_post = K_s @ K_inv @ y_obs
        cov_post = K - K_s @ K_inv @ K_s.T
        std_post = np.sqrt(np.clip(np.diag(cov_post), a_min=0, a_max=None))

        # Axes
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2.5, 2.5, 1],
            x_length=10,
            y_length=5,
            tips=False
        ).shift(DOWN)

        self.play(Create(axes))

        # Plot test points
        test_dots = VGroup(*[
            Dot(color=BLUE).scale(0.6).move_to(axes.c2p(sx[0], -2.2))
            for sx in sensor_locs
        ])
        self.play(FadeIn(test_dots))

        # Plot sensors at same locations
        sensor_dots = VGroup(*[
            Dot(color=RED).move_to(axes.c2p(sx[0], 0)) for sx in sensor_locs
        ])
        self.play(FadeIn(sensor_dots))

        # Confidence band
        upper = mean_post + 2 * std_post
        lower = mean_post - 2 * std_post
        upper_pts = [axes.c2p(x[i], upper[i]) for i in range(len(x))]
        lower_pts = [axes.c2p(x[i], lower[i]) for i in reversed(range(len(x)))]
        band = Polygon(*upper_pts, *lower_pts, color=GREEN_E, fill_opacity=0.3, stroke_width=0)
        mean_curve = axes.plot_line_graph(x, mean_post, line_color=GREEN)

        self.play(FadeIn(band), Create(mean_curve))

        label = Text("Posterior covers entire region accurately", font_size=24).next_to(axes, UP)
        self.play(Write(label))
        self.wait(2)