from manim import *
from utils import CNNBaseScene
import numpy as np

class ImageToMatrixScene(CNNBaseScene):
    """Second scene: From an image to a matrix of numbers."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create sample image (a handwritten digit)
        # We'll use a simple 8x8 matrix for the digit
        digit_array = np.array([
            [0.0, 0.0, 0.3, 0.5, 0.5, 0.2, 0.0, 0.0],
            [0.0, 0.2, 0.9, 0.3, 0.8, 0.5, 0.0, 0.0],
            [0.0, 0.5, 0.2, 0.0, 0.8, 0.5, 0.0, 0.0],
            [0.0, 0.5, 0.5, 0.6, 0.8, 0.2, 0.0, 0.0],
            [0.0, 0.0, 0.8, 0.9, 0.6, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.3, 0.6, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.3, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.9, 0.0]
        ])
        
        # Create a stylized "image" representation
        image_mob = self.create_matrix_from_array(digit_array, color_map=True, cell_size=0.5)
        image_mob.scale(1.5)
        image_mob.to_edge(LEFT, buff=1)
        
        # Add a border to make it look like an image
        image_border = SurroundingRectangle(image_mob, color=WHITE, buff=0.1)
        image = VGroup(image_mob, image_border)
        
        # Create a matrix representation of the same data
        matrix_mob = Matrix(
            digit_array.round(1),
            h_buff=1.8,
            v_buff=1.0,
            bracket_h_buff=0.1,
            bracket_v_buff=0.1
        )
        matrix_mob.scale(0.6)
        matrix_mob.to_edge(RIGHT, buff=1)
        
        # Create a grid to overlay on the image
        grid = VGroup()
        for i in range(9):  # Horizontal lines
            line = Line(
                start=image_mob.get_corner(UL) + RIGHT * 0 + DOWN * i * 0.5 * 1.5,
                end=image_mob.get_corner(UR) + LEFT * 0 + DOWN * i * 0.5 * 1.5,
                stroke_width=1,
                stroke_opacity=0.5
            )
            grid.add(line)
        
        for j in range(9):  # Vertical lines
            line = Line(
                start=image_mob.get_corner(UL) + RIGHT * j * 0.5 * 1.5 + DOWN * 0,
                end=image_mob.get_corner(DL) + RIGHT * j * 0.5 * 1.5 + UP * 0,
                stroke_width=1,
                stroke_opacity=0.5
            )
            grid.add(line)
            
        # Create labels for the axes
        height_label = Text("Height", font_size=24, color=self.color_palette["text"])
        height_label.next_to(image, LEFT, buff=0.5)
        
        width_label = Text("Width", font_size=24, color=self.color_palette["text"])
        width_label.next_to(image, DOWN, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """Every colored image is just a grid of numbers. Here, we convert pixels to a matrix 
            of intensities. Our goal: learn patterns in these numbers automatically."""
        ):
            # Show the image
            self.play(FadeIn(image))
            self.wait(0.5)
            
            # Overlay the grid
            self.play(Create(grid))
            self.wait(0.5)
            
            # Transform to matrix
            self.play(
                TransformFromCopy(image_mob, matrix_mob),
                run_time=2
            )
            self.wait(0.5)
            
            # Add axis labels
            self.play(
                Write(height_label),
                Write(width_label)
            )
            self.wait(1) 