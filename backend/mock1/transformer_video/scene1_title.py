from manim import *
from utils import TransformerBaseScene
import numpy as np

class TitleScene(TransformerBaseScene):
    """First scene: Title & Hook for Transformers & Attention Video."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a soft gradient background (lavender to white)
        background = self.create_gradient_background("#E6E6FA", "#FFFFFF")
        self.add(background)
        
        # Create title text
        title = Text("Transformers & Attention", font_size=72, color=self.color_palette["text"])
        title.move_to(UP * 1)
        
        # Create subtitle text
        subtitle = Text("Why attention matters", font_size=48, color=self.color_palette["embedding"])
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """Welcome! Today we'll peer inside Transformers—the model powering language 
            understanding and generation. At their core lies attention, letting networks focus 
            on the most relevant parts of input."""
        ):
            # Fade in the background
            self.play(FadeIn(background))
            
            # Animate title flying in with a slight bounce
            self.play(
                FadeIn(title, shift=DOWN),
                rate_func=lambda t: 1 - (1-t)**4  # Bounce effect with overshooting
            )
            
            # Type out subtitle letter by letter
            self.play(Write(subtitle))
            
            # Hold for a moment
            self.wait(2)
            
            # Shrink title to top-left
            self.play(
                title.animate.scale(0.4).to_corner(UL),
                subtitle.animate.scale(0.4).next_to(title, DOWN, aligned_edge=LEFT),
                run_time=1
            ) 