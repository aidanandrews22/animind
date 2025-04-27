from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import os
import numpy as np
from utils import TransformerBaseScene
from scene1_title import TitleScene
from scene2_sequence_vectors import SequenceVectorsScene
from scene3_query_key_value import QueryKeyValueScene
from scene4_scaled_dot_product import ScaledDotProductScene
from scene5_multi_head_attention import MultiHeadAttentionScene
from scene6_positional_encoding import PositionalEncodingScene
from scene7_encoder_block import EncoderBlockScene
from scene8_stacking_decoder import StackingDecoderScene
from scene9_applications import ApplicationsScene

# Define the main class that runs all scenes
class TransformerVideo(Scene):
    def construct(self):
        # Create all scenes
        scenes = [
            TitleScene(),
            SequenceVectorsScene(),
            QueryKeyValueScene(),
            ScaledDotProductScene(),
            MultiHeadAttentionScene(),
            PositionalEncodingScene(),
            EncoderBlockScene(),
            StackingDecoderScene(),
            ApplicationsScene()
        ]
        
        # For each scene, run its construct method
        for scene in scenes:
            scene.construct()
            # Only try to fade out if there are mobjects
            if self.mobjects:
                self.play(*[FadeOut(mob) for mob in self.mobjects])
            self.clear()  # Make sure to clear the scene afterwards

if __name__ == "__main__":
    # Command to run the video generation
    os.system("manim -pqh /Users/aidan/Documents/Code/Projects/animind/backend/mock1/transformer_video/main.py TransformerVideo") 