from manim import *
from utils import CNNBaseScene
import numpy as np

class MultipleFiltersScene(CNNBaseScene):
    """Fourth scene: Using multiple filters to create different feature maps."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a larger input image matrix (8x8)
        input_array = np.zeros((8, 8))
        # Create a pattern (cross)
        for i in range(8):
            for j in range(8):
                if i == j or i == 7-j:
                    input_array[i, j] = 0.9
                else:
                    input_array[i, j] = 0.1 * np.random.random()
        
        # Create different 3x3 convolution kernels
        # Horizontal edge detector
        kernel1 = np.array([
            [ 1,  1,  1],
            [ 0,  0,  0],
            [-1, -1, -1]
        ])
        
        # Vertical edge detector
        kernel2 = np.array([
            [ 1,  0, -1],
            [ 1,  0, -1],
            [ 1,  0, -1]
        ])
        
        # Diagonal edge detector
        kernel3 = np.array([
            [-1, -1,  1],
            [-1,  1, -1],
            [ 1, -1, -1]
        ])
        
        # Create the input image visualization
        input_matrix = self.create_matrix_from_array(input_array, cell_size=0.5)
        input_matrix.scale(0.8)
        input_matrix.to_edge(LEFT, buff=2)
        
        # Create the kernel visualizations
        kernel_vis1 = self.create_conv_kernel(kernel1)
        kernel_vis1.scale(0.8)
        kernel_vis1.move_to(input_matrix.get_center() + RIGHT * 3.5 + UP * 2)
        
        kernel_vis2 = self.create_conv_kernel(kernel2)
        kernel_vis2.scale(0.8)
        kernel_vis2.move_to(input_matrix.get_center() + RIGHT * 3.5)
        
        kernel_vis3 = self.create_conv_kernel(kernel3)
        kernel_vis3.scale(0.8)
        kernel_vis3.move_to(input_matrix.get_center() + RIGHT * 3.5 + DOWN * 2)
        
        # Create output matrices (6x6 since they're reduced by the kernel size-1)
        # Apply convolutions to get the output arrays
        output_array1 = np.zeros((6, 6))
        output_array2 = np.zeros((6, 6))
        output_array3 = np.zeros((6, 6))
        
        for i in range(6):
            for j in range(6):
                # Apply each kernel
                for ki in range(3):
                    for kj in range(3):
                        output_array1[i, j] += input_array[i+ki, j+kj] * kernel1[ki, kj]
                        output_array2[i, j] += input_array[i+ki, j+kj] * kernel2[ki, kj]
                        output_array3[i, j] += input_array[i+ki, j+kj] * kernel3[ki, kj]
                
                # Normalize
                output_array1[i, j] = np.clip(output_array1[i, j] / 8, 0, 1)
                output_array2[i, j] = np.clip(output_array2[i, j] / 8, 0, 1)
                output_array3[i, j] = np.clip(output_array3[i, j] / 8, 0, 1)
        
        # Create the output matrix visualizations
        output_matrix1 = self.create_matrix_from_array(output_array1, cell_size=0.5)
        output_matrix1.scale(0.8)
        output_matrix1.move_to(kernel_vis1.get_center() + RIGHT * 3.5)
        
        output_matrix2 = self.create_matrix_from_array(output_array2, cell_size=0.5)
        output_matrix2.scale(0.8)
        output_matrix2.move_to(kernel_vis2.get_center() + RIGHT * 3.5)
        
        output_matrix3 = self.create_matrix_from_array(output_array3, cell_size=0.5)
        output_matrix3.scale(0.8)
        output_matrix3.move_to(kernel_vis3.get_center() + RIGHT * 3.5)
        
        # Add labels
        input_label = Text("Input Image", font_size=24, color=self.color_palette["text"])
        input_label.next_to(input_matrix, UP, buff=0.5)
        
        kernel_label1 = Text("Horizontal Filter", font_size=18, color=self.color_palette["accent1"])
        kernel_label1.next_to(kernel_vis1, UP, buff=0.2)
        
        kernel_label2 = Text("Vertical Filter", font_size=18, color=self.color_palette["accent2"])
        kernel_label2.next_to(kernel_vis2, UP, buff=0.2)
        
        kernel_label3 = Text("Diagonal Filter", font_size=18, color=self.color_palette["accent3"])
        kernel_label3.next_to(kernel_vis3, UP, buff=0.2)
        
        output_label1 = Text("Feature Map 1", font_size=18, color=self.color_palette["accent1"])
        output_label1.next_to(output_matrix1, UP, buff=0.2)
        
        output_label2 = Text("Feature Map 2", font_size=18, color=self.color_palette["accent2"])
        output_label2.next_to(output_matrix2, UP, buff=0.2)
        
        output_label3 = Text("Feature Map 3", font_size=18, color=self.color_palette["accent3"])
        output_label3.next_to(output_matrix3, UP, buff=0.2)
        
        # Create arrows connecting kernels to feature maps
        arrow1 = Arrow(
            kernel_vis1.get_right(), 
            output_matrix1.get_left(),
            buff=0.2,
            color=self.color_palette["accent1"]
        )
        
        arrow2 = Arrow(
            kernel_vis2.get_right(), 
            output_matrix2.get_left(),
            buff=0.2,
            color=self.color_palette["accent2"]
        )
        
        arrow3 = Arrow(
            kernel_vis3.get_right(), 
            output_matrix3.get_left(),
            buff=0.2,
            color=self.color_palette["accent3"]
        )
        
        # Animation sequence
        with self.voiceover(
            """By using multiple filters, a CNN can detect diverse features—horizontal edges, 
            vertical lines, or color patterns—all at once, resulting in multiple feature maps."""
        ):
            # Show input matrix and label
            self.play(
                FadeIn(input_matrix),
                Write(input_label)
            )
            self.wait(0.5)
            
            # Show kernels with their labels
            self.play(
                FadeIn(kernel_vis1),
                Write(kernel_label1)
            )
            self.wait(0.2)
            
            # Show first feature map with arrow
            self.play(
                GrowArrow(arrow1),
                FadeIn(output_matrix1),
                Write(output_label1)
            )
            self.wait(0.5)
            
            # Show second kernel and feature map
            self.play(
                FadeIn(kernel_vis2),
                Write(kernel_label2)
            )
            self.wait(0.2)
            
            self.play(
                GrowArrow(arrow2),
                FadeIn(output_matrix2),
                Write(output_label2)
            )
            self.wait(0.5)
            
            # Show third kernel and feature map
            self.play(
                FadeIn(kernel_vis3),
                Write(kernel_label3)
            )
            self.wait(0.2)
            
            self.play(
                GrowArrow(arrow3),
                FadeIn(output_matrix3),
                Write(output_label3)
            )
            self.wait(0.5)
            
            # Add a bit of camera movement to emphasize the 3D-like structure
            self.camera.frame.save_state()
            self.play(
                self.camera.frame.animate.set_euler_angles(
                    theta=15 * DEGREES,
                    phi=5 * DEGREES
                ),
                run_time=1
            )
            self.wait(0.5)
            self.play(Restore(self.camera.frame), run_time=1)
            
            # Group everything for later reference
            self.multiple_filters_group = VGroup(
                input_matrix, input_label,
                kernel_vis1, kernel_label1, 
                kernel_vis2, kernel_label2,
                kernel_vis3, kernel_label3,
                output_matrix1, output_label1,
                output_matrix2, output_label2,
                output_matrix3, output_label3,
                arrow1, arrow2, arrow3
            ) 