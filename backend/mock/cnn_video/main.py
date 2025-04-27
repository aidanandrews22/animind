import sys
import os
from manim import config, logger
from manim import *
from dotenv import load_dotenv

# Import scene files
from scene1_title import TitleScene
from scene2_image_to_matrix import ImageToMatrixScene
from scene3_convolution import ConvolutionOperationScene
from scene4_multiple_filters import MultipleFiltersScene
from scene5_activation import ActivationScene
from scene6_pooling import PoolingScene
from scene7_stacking_layers import StackingLayersScene
from scene8_flatten_fc import FlattenFullyConnectedScene
from scene9_training import TrainingScene
# from scene7_conclusion import ConclusionScene # Removed - file missing

# Load environment variables from .env file
load_dotenv()

# Check for Google API key
if not os.environ.get("GOOGLE_API_KEY"):
    logger.warning("GOOGLE_API_KEY not found in environment. Voice narration may not work.")

def main():
    # Default to rendering all scenes
    # Render all scenes in sequence
    scenes = [
        TitleScene,
        ImageToMatrixScene,
        ConvolutionOperationScene, # Renamed from ConvolutionScene
        MultipleFiltersScene,
        ActivationScene,
        PoolingScene,
        StackingLayersScene,
        FlattenFullyConnectedScene,
        TrainingScene,
        # ConclusionScene # Removed - file missing
    ]
    
    # Configure Manim for high quality rendering
    config.quality = "high_quality"
    config.preview = True  # Set to False for final render
    
    # Render each scene
    for i, scene_class in enumerate(scenes):
        print(f"Rendering scene {i+1}/{len(scenes)}: {scene_class.__name__}")
        scene = scene_class()
        scene.render()
        
        # Save the output file with a numbered prefix
        output_file = f"scene{i+1}_{scene_class.__name__}.mp4"
        # This would require custom file handling, as Manim manages its own output

if __name__ == "__main__":
    main() 