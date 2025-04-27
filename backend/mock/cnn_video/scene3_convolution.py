from manim import *
from utils import CNNBaseScene
import numpy as np

class ConvolutionOperationScene(CNNBaseScene):
    """Third scene: Convolution operation on an image."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a larger input image matrix (8x8)
        input_array = np.zeros((8, 8))
        # Create a simple pattern (diagonal line)
        for i in range(8):
            for j in range(8):
                if abs(i - j) < 2:
                    input_array[i, j] = 0.9
                else:
                    input_array[i, j] = 0.1 * np.random.random()
        
        # Create a 3x3 convolution kernel (Sobel filter for edge detection)
        kernel = np.array([
            [ 1,  2,  1],
            [ 0,  0,  0],
            [-1, -2, -1]
        ])
        
        # Create the input image visualization
        input_matrix = self.create_matrix_from_array(input_array, cell_size=0.5)
        input_matrix.scale(1.2)
        input_matrix.to_edge(LEFT, buff=1.5)
        
        # Create the kernel visualization
        kernel_vis = self.create_conv_kernel(kernel)
        kernel_vis.scale(1.2)
        kernel_vis.to_edge(UP, buff=1.5)
        
        # Create output matrix (6x6 since it's reduced by the kernel size-1)
        output_array = np.zeros((6, 6))
        output_matrix = self.create_matrix_from_array(output_array, cell_size=0.5)
        output_matrix.scale(1.2)
        output_matrix.to_edge(RIGHT, buff=1.5)
        
        # Add labels
        input_label = Text("Input Image", font_size=24, color=self.color_palette["text"])
        input_label.next_to(input_matrix, UP, buff=0.5)
        
        kernel_label = Text("Filter (Kernel)", font_size=24, color=self.color_palette["text"])
        kernel_label.next_to(kernel_vis, UP, buff=0.5)
        
        output_label = Text("Feature Map", font_size=24, color=self.color_palette["text"])
        output_label.next_to(output_matrix, UP, buff=0.5)
        
        # Sliding window
        window = SurroundingRectangle(
            VGroup(),  # Empty initially, will be updated
            color=YELLOW,
            stroke_width=2,
            buff=0
        )
        
        # Animation sequence
        with self.voiceover(
            """Convolution: slide a small filter across the image, multiply overlapping values, and sum them. 
            Each result populates a new feature map—revealing edges or textures our network can learn."""
        ):
            # Show input matrix and label
            self.play(
                FadeIn(input_matrix),
                Write(input_label)
            )
            self.wait(0.5)
            
            # Show kernel and label
            self.play(
                FadeIn(kernel_vis),
                Write(kernel_label)
            )
            self.wait(0.5)
            
            # Show empty output matrix and label
            self.play(
                FadeIn(output_matrix),
                Write(output_label)
            )
            self.wait(0.5)
            
            # Perform convolution animation
            for i in range(6):  # Output rows
                for j in range(6):  # Output columns
                    # Update the sliding window position
                    window_group = VGroup()
                    for ki in range(3):
                        for kj in range(3):
                            # Find the corresponding cell in the input matrix
                            cell_group = input_matrix[ki + i + kj + j]
                            if isinstance(cell_group, VGroup):
                                window_group.add(cell_group)
                    
                    window.become(SurroundingRectangle(window_group, color=YELLOW, stroke_width=2, buff=0))
                    
                    # Calculate convolution result
                    result = 0
                    for ki in range(3):
                        for kj in range(3):
                            result += input_array[i + ki, j + kj] * kernel[ki, kj]
                    
                    # Scale result and clip between 0 and 1
                    result = np.clip(result / 8, 0, 1)
                    output_array[i, j] = result
                    
                    # Update the output matrix
                    result_cell = Square(side_length=0.5)
                    result_cell.set_stroke(WHITE, 1)
                    result_cell.set_fill(color=interpolate_color(BLACK, WHITE, result), opacity=1)
                    result_cell.move_to(output_matrix[i * 6 + j].get_center())
                    
                    # Animation for this step
                    if i == 0 and j == 0:
                        # First position - show the process in detail
                        self.play(
                            Create(window),
                            run_time=0.5
                        )
                        self.wait(0.3)
                        
                        # Show multiplication and sum visually
                        calculation_text = MathTex(
                            f"\\sum (\\text{{input}} \\times \\text{{kernel}}) = {result:.2f}",
                            font_size=24
                        )
                        calculation_text.next_to(kernel_vis, DOWN, buff=0.5)
                        
                        self.play(
                            Write(calculation_text),
                            run_time=0.5
                        )
                        self.wait(0.3)
                        
                        # Update output cell
                        self.play(
                            ReplacementTransform(calculation_text, result_cell),
                            run_time=0.5
                        )
                        
                    else:
                        # For subsequent positions, move faster
                        self.play(
                            Transform(window, SurroundingRectangle(window_group, color=YELLOW, stroke_width=2, buff=0)),
                            ReplacementTransform(
                                output_matrix[i * 6 + j], 
                                result_cell
                            ),
                            run_time=0.15  # Quick animation
                        )
                    
                    # Update the output matrix
                    output_matrix[i * 6 + j] = result_cell
            
            # Final pause to see the completed feature map
            self.wait(1)
            
            # Group everything for later reference
            convolution_group = VGroup(
                input_matrix, input_label,
                kernel_vis, kernel_label,
                output_matrix, output_label,
                window
            )
            self.convolution_group = convolution_group 