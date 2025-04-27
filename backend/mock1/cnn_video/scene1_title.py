from manim import *
from utils import CNNBaseScene
import numpy as np

class TitleScene(CNNBaseScene):
    """First scene: Title and motivation for CNNs."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a soft gradient background
        gradient = Rectangle(
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            fill_color=self.color_palette["background"],
            fill_opacity=1
        )
        self.add(gradient)
        
        # Create title text
        title = Text("Convolutional Neural Networks", font_size=72, color=self.color_palette["text"])
        title.move_to(UP * 1)
        
        # Create subtitle text
        subtitle = Text("How machines see", font_size=48, color=self.color_palette["accent1"])
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """Welcome! Today we'll see how convolutional neural networks—CNNs—power modern 
            image recognition. By the end, you'll understand how simple filters detect edges, 
            textures, and even complex patterns."""
        ):
            # Fade in the background
            self.play(FadeIn(gradient))
            
            # Animate title flying in from top
            self.play(
                FadeIn(title, shift=DOWN),
                rate_func=lambda t: 1 - (1-t)**4  # Bounce effect with overshooting
            )
            
            # Type out subtitle letter by letter
            self.play(Write(subtitle, run_time=1.5))
            
            # Hold for 2 seconds
            self.wait(2)
            
            # Shrink title to top-left
            self.play(
                title.animate.scale(0.4).to_corner(UL),
                subtitle.animate.scale(0.4).next_to(title, DOWN, aligned_edge=LEFT),
                run_time=1
            ) 