
from manim import *

# Set the background color of the animation
config.background_color = "#111111" # Dark grey background

class Cool3DGraphics(ThreeDScene):
    """
    An animation showcasing a rotating 3D Dodecahedron and zooming into it.
    """
    def construct(self):
        # Set up 3D axes for spatial reference
        # Added axis labels for clarity
        axes = ThreeDAxes(
            x_range=(-3.5, 3.5, 1),
            y_range=(-3.5, 3.5, 1),
            z_range=(-3.5, 3.5, 1),
            x_length=7,
            y_length=7,
            z_length=7,
        )
        axis_labels = axes.get_axis_labels(
            x_label=MathTex("x"), y_label=MathTex("y"), z_label=MathTex("z")
        )

        # Create a Dodecahedron - a platonic solid with 12 pentagonal faces
        # Using a vibrant color and slight transparency
        shape = Dodecahedron(
            color=TEAL,       # Use Teal color
            fill_opacity=0.7, # Make it somewhat transparent to see structure
            stroke_width=1.5, # Slightly thicker edges
            stroke_color=WHITE # White edges for contrast
        ).scale(1.8) # Make the shape larger for better visual impact

        # Set initial camera perspective using spherical coordinates
        # phi = angle from the positive z-axis (inclination/latitude)
        # theta = angle from the positive x-axis in the xy-plane (azimuth/longitude)
        # distance = distance from the origin
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES, distance=9)

        # Introduce the axes and the shape
        self.play(Create(axes), Create(axis_labels), FadeIn(shape, scale=0.2), run_time=2)
        self.wait(0.5)

        # --- Rotations ---
        # Combine camera movement with object rotation for a dynamic effect

        # Rotate around the Z-axis (vector pointing OUT of the screen)
        # Simultaneously change the camera's azimuthal angle (theta)
        self.play(
            Rotate(
                shape,
                angle=TAU,      # Full rotation (2 * PI radians or 360 degrees)
                axis=OUT,       # Z-axis
                run_time=6,
                rate_func=linear # Constant speed rotation
            ),
            # Move camera around the object while it rotates
            self.camera.theta_tracker.animate.increment_value(120 * DEGREES),
            run_time=6,
            rate_func=smooth # Smooth camera movement
        )
        self.wait(0.5)

        # Rotate around the Y-axis (UP vector)
        # Simultaneously change the camera's inclination angle (phi)
        self.play(
            Rotate(
                shape,
                angle=TAU,
                axis=UP,        # Y-axis
                run_time=6,
                rate_func=linear
            ),
            # Move camera up and down slightly while object rotates
            self.camera.phi_tracker.animate.set_value(80 * DEGREES), # Look more from above
            run_time=6,
            rate_func=smooth
        )
        self.wait(0.5)

        # Rotate around the X-axis (RIGHT vector)
        # Reset camera angles partially during rotation
        self.play(
            Rotate(
                shape,
                angle=TAU,
                axis=RIGHT,     # X-axis
                run_time=6,
                rate_func=linear
            ),
            # Bring camera back towards the initial viewing angle
            self.camera.theta_tracker.animate.set_value(-60 * DEGREES),
            self.camera.phi_tracker.animate.set_value(70 * DEGREES),
            run_time=6,
            rate_func=smooth
        )
        self.wait(1)

        # --- "Go Inside" Animation ---
        # Move the camera significantly closer to the object's center (origin)
        # This simulates zooming or flying into the object.
        self.play(
            # Animate the camera's distance property to a very small value
            # Getting close enough to pass through the faces depending on scale
            self.camera.distance_tracker.animate.set_value(0.8),
            # Optionally, adjust focal distance if needed, but distance is key here
            run_time=7,
            rate_func=smooth # Use smooth easing for the zoom/fly-in
        )
        self.wait(1) # Pause while very close / potentially "inside"

        # Perform a final slow rotation while close up to appreciate the internal view
        self.play(
            Rotate(
                shape,
                angle=PI, # Rotate 180 degrees
                axis=UP + RIGHT, # Rotate around a combined axis
                run_time=5
            ),
             rate_func=linear
        )

        # Hold the final close-up frame
        self.wait(3)

        # Optional: Zoom back out
        # self.play(self.camera.distance_tracker.animate.set_value(9), run_time=4, rate_func=smooth)
        # self.wait(1)
