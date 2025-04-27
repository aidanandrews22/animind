from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import os
import numpy as np
from utils import CNNBaseScene
from scene1_title import TitleScene
from scene2_image_to_matrix import ImageToMatrixScene
from scene3_convolution import ConvolutionOperationScene
from scene4_multiple_filters import MultipleFiltersScene
from scene5_activation import ActivationScene
from scene6_pooling import PoolingScene
from scene7_stacking_layers import StackingLayersScene
from scene8_flatten_fc import FlattenFullyConnectedScene
from scene9_training import TrainingScene

# Define the main class that runs all scenes
class CNNVideo(Scene):
    def construct(self):
        # Create all scenes
        scenes = [
            TitleScene(),
            ImageToMatrixScene(),
            ConvolutionOperationScene(),
            MultipleFiltersScene(),
            ActivationScene(),
            PoolingScene(),
            StackingLayersScene(),
            FlattenFullyConnectedScene(),
            TrainingScene()
        ]
        
        # For each scene, run its construct method
        for scene in scenes:
            scene.construct()
            self.play(*[FadeOut(mob) for mob in self.mobjects])

if __name__ == "__main__":
    os.system("manim -pqh cnn_video/main.py CNNVideo") 