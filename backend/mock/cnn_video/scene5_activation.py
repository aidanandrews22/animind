from manim import *
from utils import CNNBaseScene
import numpy as np

class ActivationScene(CNNBaseScene):
    """Fifth scene: Non-linearity and activation functions (ReLU)."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a feature map with both positive and negative values
        feature_map = np.array([
            [-0.5,  0.7, -0.3,  0.1, -0.6,  0.2],
            [ 0.4, -0.8,  0.3, -0.7,  0.5, -0.4],
            [-0.3,  0.2, -0.9,  0.6, -0.1,  0.8],
            [ 0.7, -0.5,  0.4, -0.2,  0.9, -0.5],
            [-0.2,  0.5, -0.6,  0.3, -0.8,  0.1],
            [ 0.1, -0.4,  0.8, -0.3,  0.2, -0.7]
        ])
        
        # Create ReLU activated feature map
        relu_map = np.maximum(0, feature_map)
        
        # Create visualizations for the feature maps
        feature_vis = self.create_matrix_from_array(feature_map, cell_size=0.5)
        feature_vis.scale(1.2)
        feature_vis.to_edge(LEFT, buff=2)
        
        relu_vis = self.create_matrix_from_array(relu_map, cell_size=0.5)
        relu_vis.scale(1.2)
        relu_vis.to_edge(RIGHT, buff=2)
        
        # Add labels
        feature_label = Text("Feature Map", font_size=24, color=self.color_palette["text"])
        feature_label.next_to(feature_vis, UP, buff=0.5)
        
        relu_label = Text("After ReLU Activation", font_size=24, color=self.color_palette["text"])
        relu_label.next_to(relu_vis, UP, buff=0.5)
        
        # Create ReLU function graph
        axes = Axes(
            x_range=[-1.5, 1.5, 0.5],
            y_range=[-0.5, 1.5, 0.5],
            axis_config={"color": self.color_palette["text"]},
            x_length=4,
            y_length=3
        )
        
        relu_graph = axes.plot(
            lambda x: max(0, x),
            x_range=[-1.5, 1.5],
            color=self.color_palette["accent2"]
        )
        
        relu_eq = MathTex("ReLU(x) = max(0, x)", color=self.color_palette["text"])
        relu_eq.next_to(axes, UP, buff=0.2)
        
        graph_group = VGroup(axes, relu_graph, relu_eq)
        graph_group.scale(0.8)
        graph_group.to_corner(DR, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """Next, we apply a non-linear activation—like ReLU—setting negatives to zero. 
            This lets the network model complex relationships beyond simple linear filters."""
        ):
            # Show feature map and label
            self.play(
                FadeIn(feature_vis),
                Write(feature_label)
            )
            self.wait(0.5)
            
            # Show ReLU function graph
            self.play(
                Create(axes),
                Write(relu_eq),
                run_time=1
            )
            self.play(
                Create(relu_graph),
                run_time=1
            )
            self.wait(0.5)
            
            # Apply ReLU to feature map
            # First highlight negative values
            negative_cells = []
            for i in range(6):
                for j in range(6):
                    if feature_map[i, j] < 0:
                        # Get the corresponding cell in the visualization
                        cell_idx = i * 6 + j
                        cell = feature_vis[cell_idx]
                        negative_cells.append(cell)
            
            negative_group = VGroup(*negative_cells)
            self.play(
                negative_group.animate.set_color(RED).set_opacity(0.7),
                run_time=0.5
            )
            self.wait(0.5)
            
            # Flash the negative cells before turning them to zero
            for cell in negative_cells:
                self.play(
                    Flash(cell, color=RED, flash_radius=0.3, line_length=0.1),
                    run_time=0.05
                )
            
            # Transform to ReLU activated feature map
            self.play(
                TransformFromCopy(feature_vis, relu_vis),
                Write(relu_label),
                run_time=1.5
            )
            self.wait(0.5)
            
            # Fade out the graph
            self.play(
                FadeOut(graph_group),
                run_time=0.5
            )
            
            # Group everything for later reference
            self.activation_group = VGroup(
                feature_vis, feature_label,
                relu_vis, relu_label
            ) 