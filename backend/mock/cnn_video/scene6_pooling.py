from manim import *
from utils import CNNBaseScene
import numpy as np

class PoolingScene(CNNBaseScene):
    """Sixth scene: Pooling layer to downsample feature maps."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a feature map (6x6)
        feature_map = np.array([
            [0.1, 0.2, 0.3, 0.1, 0.7, 0.2],
            [0.4, 0.9, 0.3, 0.2, 0.4, 0.6],
            [0.5, 0.3, 0.7, 0.8, 0.3, 0.2],
            [0.1, 0.2, 0.6, 0.9, 0.4, 0.1],
            [0.3, 0.5, 0.2, 0.3, 0.8, 0.5],
            [0.2, 0.1, 0.5, 0.4, 0.2, 0.7]
        ])
        
        # Create the max-pooled output (3x3)
        pooled_map = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                # 2x2 max pooling
                pooled_map[i, j] = np.max(feature_map[2*i:2*i+2, 2*j:2*j+2])
        
        # Create visualizations
        feature_vis = self.create_matrix_from_array(feature_map, cell_size=0.5)
        feature_vis.scale(1.2)
        feature_vis.to_edge(LEFT, buff=2)
        
        pooled_vis = self.create_matrix_from_array(pooled_map, cell_size=0.8)
        pooled_vis.scale(1.2)
        pooled_vis.to_edge(RIGHT, buff=2)
        
        # Add labels
        feature_label = Text("Feature Map", font_size=24, color=self.color_palette["text"])
        feature_label.next_to(feature_vis, UP, buff=0.5)
        
        pooled_label = Text("After Max Pooling (2×2)", font_size=24, color=self.color_palette["text"])
        pooled_label.next_to(pooled_vis, UP, buff=0.5)
        
        # Create 2x2 pooling windows
        pooling_windows = []
        for i in range(3):
            for j in range(3):
                window = SurroundingRectangle(
                    VGroup(),  # Will be updated for each position
                    color=YELLOW,
                    stroke_width=2,
                    buff=0
                )
                pooling_windows.append(window)
        
        # Animation sequence
        with self.voiceover(
            """Pooling downsamples each map, keeping only the strongest signals. 
            This reduces computation and adds spatial invariance—helpful when 
            objects shift slightly in images."""
        ):
            # Show feature map and label
            self.play(
                FadeIn(feature_vis),
                Write(feature_label)
            )
            self.wait(0.5)
            
            # Create empty pooled output
            empty_pooled_vis = self.create_matrix_from_array(np.zeros((3, 3)), cell_size=0.8)
            empty_pooled_vis.scale(1.2)
            empty_pooled_vis.move_to(pooled_vis.get_center())
            
            self.play(
                FadeIn(empty_pooled_vis),
                Write(pooled_label)
            )
            self.wait(0.5)
            
            # Perform max pooling with animation
            for i in range(3):
                for j in range(3):
                    # Highlight the 2x2 region in the feature map
                    window_group = VGroup()
                    window_values = []
                    
                    for ki in range(2):
                        for kj in range(2):
                            # Find the corresponding cell in the feature matrix
                            cell_idx = (2*i + ki) * 6 + (2*j + kj)
                            cell = feature_vis[cell_idx]
                            window_group.add(cell)
                            window_values.append(feature_map[2*i + ki, 2*j + kj])
                    
                    window = SurroundingRectangle(
                        window_group,
                        color=YELLOW,
                        stroke_width=2,
                        buff=0
                    )
                    
                    # Find the max value and its position
                    max_value = max(window_values)
                    max_idx = window_values.index(max_value)
                    max_ki, max_kj = max_idx // 2, max_idx % 2
                    max_cell = window_group[max_idx]
                    
                    # Highlight the 2x2 window
                    self.play(
                        Create(window),
                        run_time=0.5
                    )
                    
                    # Highlight the maximum value
                    self.play(
                        max_cell.animate.set_color(self.color_palette["accent3"]).set_opacity(1),
                        run_time=0.3
                    )
                    
                    # Create the pooled output cell
                    pooled_cell = Square(side_length=0.8)
                    pooled_cell.set_stroke(WHITE, 1)
                    pooled_cell.set_fill(
                        color=interpolate_color(BLACK, WHITE, max_value),
                        opacity=1
                    )
                    
                    # Position to match the empty grid
                    pooled_cell.move_to(empty_pooled_vis[i * 3 + j].get_center())
                    
                    # Add the value text
                    value_text = Text(f"{max_value:.1f}", font_size=20)
                    value_text.move_to(pooled_cell.get_center())
                    
                    pooled_result = VGroup(pooled_cell, value_text)
                    
                    # Transfer the max value to the pooled output
                    self.play(
                        TransformFromCopy(max_cell, pooled_result),
                        run_time=0.5
                    )
                    
                    # Replace in the output visualization
                    empty_pooled_vis[i * 3 + j] = pooled_result
                    
                    # Remove the window highlight
                    self.play(
                        FadeOut(window),
                        max_cell.animate.set_color(WHITE).set_opacity(max_value),
                        run_time=0.2
                    )
            
            # Show the final pooled output
            self.play(
                empty_pooled_vis.animate.become(pooled_vis),
                run_time=1
            )
            
            # Demonstrate spatial invariance with a quick animation
            self.play(
                feature_vis.animate.shift(DOWN * 0.2 + RIGHT * 0.2),
                run_time=0.5
            )
            
            self.play(
                feature_vis.animate.shift(UP * 0.4 + LEFT * 0.4),
                run_time=0.5
            )
            
            self.play(
                feature_vis.animate.shift(DOWN * 0.2 + RIGHT * 0.2),
                run_time=0.5
            )
            
            self.play(
                Indicate(pooled_vis, color=GREEN, scale_factor=1.05),
                run_time=1
            )
            
            # Group everything for later reference
            self.pooling_group = VGroup(
                feature_vis, feature_label,
                empty_pooled_vis, pooled_label
            ) 