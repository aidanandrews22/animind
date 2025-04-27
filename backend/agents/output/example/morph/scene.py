\
from manim_agent import *

class CircleToSquareMorph(Scene):
    def construct(self):
        # Narration: "We begin with a perfect blue circle at the center of the screen."
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait(1) # Pause for narration

        # Narration: "As we observe, the circle begins to transform."
        # Narration: "The circular shape gradually morphs, its smooth edges becoming more angular."
        # Narration: "The transformation continues, with the blue color shifting towards red."
        square = Square(color=RED)
        self.play(Transform(circle, square))
        self.wait(1) # Pause for narration

        # Narration: "Finally, the shape completes its metamorphosis into a perfect red square."
        # Narration: "This simple animation demonstrates the power of shape morphing in mathematical visualizations."
        self.wait(2) # Hold the final square
