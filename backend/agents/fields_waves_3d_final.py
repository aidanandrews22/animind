from manim import *
import numpy as np

class FieldsAndWaves3D(ThreeDScene):
    def construct(self):
        # Set up axes and camera
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-2, 2, 1],
            x_length=8,
            y_length=8,
            z_length=4,
        )
        # Set camera angle for a good 3D view
        self.set_camera_orientation(phi=75 * DEGREES, theta=-60 * DEGREES, distance=12)

        # Add axes to the scene
        self.play(Create(axes))

        # --- Create the Field ---

        # Define the vector field function (example: swirling pattern)
        def field_func(point):
            x, y, z = point
            # Simple swirling field, mainly in xy plane, strength decreases with distance from z-axis
            scale = 0.5
            radial_dist_sq = x**2 + y**2 + 0.1 # Avoid division by zero
            dx = scale * (-y / radial_dist_sq)
            dy = scale * (x / radial_dist_sq)
            dz = scale * np.sin(np.sqrt(radial_dist_sq)) # Add some z-component variation
            # Dampen field further away
            dampening = 1 / (1 + 0.1 * (x**2 + y**2 + z**2))
            vec = np.array([dx, dy, dz]) * dampening * 3 # Scale vector magnitude
            return vec


        # Create the 3D Vector Field visual
        vector_field = ArrowVectorField(
            field_func,
            x_range=[-3.5, 3.5, 1.5], # Define the grid for vectors
            y_range=[-3.5, 3.5, 1.5],
            z_range=[-1.5, 1.5, 1.5],
            length_func=lambda norm: 0.4 * sigmoid(norm), # Control vector arrow length
            # Use 'colors' list. The default color_scheme maps vector norm to this list.
            colors=[BLUE, GREEN, YELLOW],
            opacity=0.7
        )

        # Animate the appearance of the field
        field_label = Text("Vector Field", font_size=36).to_corner(UL).set_color(WHITE)
        self.add_fixed_in_frame_mobjects(field_label) # Keep label fixed during camera rotation

        self.play(Create(vector_field, lag_ratio=0.1), run_time=3)
        self.wait(1)

        # --- Create the Wave ---

        # Value tracker for wave animation (time)
        time = ValueTracker(0)

        # Define the wave surface function (e.g., sine wave propagating along x)
        def wave_surface_func(u, v):
            # u corresponds to x, v corresponds to y
            x = u
            y = v
            # Wave propagates along x (u), frequency = 2, amplitude = 0.5
            # time.get_value() makes it animate
            z = 0.5 * np.sin(2 * u + 2 * time.get_value())
            # Corrected typo: coords_to_point instead of cords_to_point
            return axes.coords_to_point(x, y, z)

        # Create the Parametric Surface for the wave
        wave_surface = Surface(
            wave_surface_func,
            u_range=[-4, 4],
            v_range=[-4, 4],
            resolution=(32, 32), # Adjust for smoothness vs performance
            fill_opacity=0.6,
            checkerboard_colors=[PURPLE_A, PURPLE_D], # Use checkerboard for better 3D perception
            stroke_width=0.5,
            stroke_color=WHITE
        )

        # Add an updater to the wave surface to make it move
        wave_surface.add_updater(
            lambda mob: mob.become(
                 Surface(
                    wave_surface_func,
                    u_range=[-4, 4],
                    v_range=[-4, 4],
                    resolution=(32, 32),
                    fill_opacity=0.6,
                    checkerboard_colors=[PURPLE_A, PURPLE_D],
                    stroke_width=0.5,
                    stroke_color=WHITE
                )
            )
        )

        # Animate the appearance of the wave
        wave_label = Text("Propagating Wave", font_size=36).next_to(field_label, DOWN, buff=0.2).set_color(PURPLE_A)
        self.play(FadeOut(field_label)) # Remove old label
        self.add_fixed_in_frame_mobjects(wave_label) # Add new label

        self.play(Create(wave_surface), run_time=2)

        # Animate the wave propagation
        self.play(time.animate.set_value(2 * PI), run_time=5, rate_func=linear) # Animate for one full cycle

        # --- Combined View and Rotation ---

        # Rotate the camera to showcase the 3D structure
        combined_label = Text("Field and Wave Interaction", font_size=36).to_corner(UL).set_color(YELLOW)
        self.play(FadeOut(wave_label)) # Remove old label
        self.add_fixed_in_frame_mobjects(combined_label) # Add new label

        self.move_camera(phi=60 * DEGREES, theta=-135 * DEGREES, added_anims=[time.animate.set_value(4*PI)], run_time=6) # Rotate while wave continues
        self.move_camera(phi=80 * DEGREES, theta=-45 * DEGREES, added_anims=[time.animate.set_value(6*PI)], run_time=6) # Rotate more

        # Keep wave animating for a bit longer
        self.play(time.animate.set_value(8 * PI), run_time=4, rate_func=linear)

        self.wait(2)

        # Fade out everything
        self.play(FadeOut(vector_field), FadeOut(wave_surface), FadeOut(axes), FadeOut(combined_label))
        self.wait(1)
