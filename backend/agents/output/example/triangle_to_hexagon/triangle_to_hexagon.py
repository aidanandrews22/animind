\
from manim import *

class TriangleToHexagon(Scene):
    def construct(self):
        # Set background to white as per script description
        self.camera.background_color = WHITE

        # Narration: "We begin with a single green triangle, centered against a white background."
        triangle = Triangle(color=GREEN, fill_opacity=1).scale(1.5)
        # Add outline for better visibility on white background
        triangle.set_stroke(color=BLACK, width=2)
        self.play(FadeIn(triangle, scale=0.5))
        self.wait(1)

        # Narration: "The triangle slowly starts to rotate, completing a full revolution."
        self.play(Rotate(triangle, angle=360 * DEGREES, run_time=3))
        self.wait(0.5)

        # Narration: "As it spins, the triangle fractures into three smaller identical triangles."
        # Create three smaller triangles (scaled copies). Using copies simplifies the visual.
        small_triangles = VGroup(*[
            triangle.copy().scale(0.5) for _ in range(3)
        ])
        small_triangles.move_to(triangle.get_center()) # Start at the same center

        # Position them slightly offset for the "fracture" effect before moving out
        small_triangles[0].shift(UP*0.05)
        small_triangles[1].shift(LEFT*0.05 + DOWN*0.025)
        small_triangles[2].shift(RIGHT*0.05 + DOWN*0.025)


        self.play(
            FadeOut(triangle, run_time=0.5),
            FadeIn(small_triangles, run_time=0.5)
        )
        self.wait(0.5)

        # Narration: "The smaller triangles gracefully drift outward, maintaining their rotation."
        # Define outward movement paths
        outward_shifts = [UP * 1.5, DL * 1.5, DR * 1.5]
        self.play(
            *[small_triangles[i].animate.shift(outward_shifts[i]).rotate(120*DEGREES) for i in range(3)],
            run_time=2.5
        )
        self.wait(0.5)

        # Narration: "Then, in a synchronized motion, they reorient and slide back together. Their reunion forms a perfect hexagon, now glowing with a vibrant gold hue."
        # Define the target hexagon
        hexagon = RegularPolygon(n=6, color=GOLD, fill_opacity=1).scale(1.8) # Scale to be visually prominent
        hexagon.set_stroke(color=BLACK, width=2)
        # Manim doesn't have a built-in simple glow effect applicable here.
        # We represent 'glowing with a vibrant gold hue' with the GOLD color.

        # Transform the group of small triangles into the hexagon
        self.play(Transform(small_triangles, hexagon, run_time=3))
        self.wait(1.5)

        # Narration: "This complex animation illustrates principles of rotational symmetry and geometric transformation."
        # Keep the final hexagon on screen for a moment
        self.wait(3)

