from manim import *
from utils import CNNBaseScene
import numpy as np

class FlattenFullyConnectedScene(CNNBaseScene):
    """Eighth scene: Flatten and fully connected layers for classification."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create feature maps (3x3) with different colors representing different types of features
        feature_map1 = np.random.random((3, 3)) * 0.5 + 0.5
        feature_map2 = np.random.random((3, 3)) * 0.5 + 0.5
        feature_map3 = np.random.random((3, 3)) * 0.5 + 0.5
        
        # Create visualizations
        feature_vis1 = self.create_matrix_from_array(feature_map1, cell_size=0.5)
        feature_vis1.set_color(self.color_palette["accent1"])
        feature_vis1.scale(0.8)
        feature_vis1.to_edge(LEFT, buff=2).shift(UP)
        
        feature_vis2 = self.create_matrix_from_array(feature_map2, cell_size=0.5)
        feature_vis2.set_color(self.color_palette["accent2"])
        feature_vis2.scale(0.8)
        feature_vis2.next_to(feature_vis1, DOWN, buff=0.5)
        
        feature_vis3 = self.create_matrix_from_array(feature_map3, cell_size=0.5)
        feature_vis3.set_color(self.color_palette["accent3"])
        feature_vis3.scale(0.8)
        feature_vis3.next_to(feature_vis2, DOWN, buff=0.5)
        
        # Group the feature maps
        feature_maps = VGroup(feature_vis1, feature_vis2, feature_vis3)
        
        # Create a flattened vector of all the feature maps
        flattened_values = np.concatenate([
            feature_map1.flatten(), 
            feature_map2.flatten(), 
            feature_map3.flatten()
        ])
        
        # Create visualization for the flattened vector
        flattened_vector = VGroup()
        colors = [self.color_palette["accent1"]] * 9 + [self.color_palette["accent2"]] * 9 + [self.color_palette["accent3"]] * 9
        
        for i, val in enumerate(flattened_values):
            cell = Square(side_length=0.4)
            cell.set_stroke(WHITE, 1)
            cell.set_fill(colors[i], opacity=val)
            cell.shift(RIGHT * 0.45 * i)
            flattened_vector.add(cell)
        
        # Position the flattened vector
        flattened_vector.rotate(PI/2)  # Vertical orientation
        flattened_vector.move_to(ORIGIN + RIGHT * 2)
        
        # Create fully connected network
        # Output neurons (for digit classification)
        output_neurons = VGroup()
        for i in range(10):  # 10 digits (0-9)
            neuron = Circle(radius=0.3, stroke_width=2, stroke_color=WHITE)
            neuron.set_fill(self.color_palette["background"], opacity=1)
            digit = Text(str(i), font_size=20, color=self.color_palette["text"])
            digit.move_to(neuron)
            output_neurons.add(VGroup(neuron, digit))
        
        # Arrange output neurons in a circle
        output_neurons.arrange_in_grid(rows=5, cols=2, buff=0.3)
        output_neurons.move_to(ORIGIN + RIGHT * 5)
        
        # Create connecting lines from flattened vector to output neurons
        connections = VGroup()
        for i, neuron in enumerate(output_neurons):
            # Only connect a subset of inputs to keep visualization clean
            connected_indices = np.random.choice(range(len(flattened_values)), size=5, replace=False)
            for idx in connected_indices:
                start = flattened_vector[idx].get_center() + RIGHT * 0.3
                end = neuron.get_center() + LEFT * 0.3
                line = Line(start, end, stroke_width=1, stroke_opacity=0.5)
                connections.add(line)
        
        # Create labels
        feature_label = Text("Feature Maps", font_size=24, color=self.color_palette["text"])
        feature_label.next_to(feature_maps, UP, buff=0.5)
        
        flatten_label = Text("Flatten", font_size=24, color=self.color_palette["text"])
        flatten_label.next_to(flattened_vector, UP, buff=0.5)
        
        fc_label = Text("Fully Connected", font_size=24, color=self.color_palette["text"])
        fc_label.next_to(output_neurons, UP, buff=0.5)
        
        # Create arrows connecting the components
        arrow1 = Arrow(
            feature_maps.get_right(), 
            flattened_vector.get_left(),
            buff=0.2,
            color=self.color_palette["text"]
        )
        
        arrow2 = Arrow(
            flattened_vector.get_right(), 
            output_neurons.get_left(),
            buff=0.2,
            color=self.color_palette["text"]
        )
        
        # Animation sequence
        with self.voiceover(
            """Finally, we flatten the features and feed them into a fully connected layer, 
            where the network scores each class. A softmax turns scores into probabilities—our final prediction."""
        ):
            # Show feature maps
            self.play(
                FadeIn(feature_maps),
                Write(feature_label)
            )
            self.wait(0.5)
            
            # Show flattening process
            self.play(
                GrowArrow(arrow1)
            )
            
            # Create temporary squares for the animation
            temp_squares = []
            offset = 0
            for feature_map, color in zip([feature_map1, feature_map2, feature_map3], 
                                         [self.color_palette["accent1"], self.color_palette["accent2"], self.color_palette["accent3"]]):
                for i in range(3):
                    for j in range(3):
                        cell = Square(side_length=0.4)
                        cell.set_stroke(WHITE, 1)
                        cell.set_fill(color, opacity=feature_map[i, j])
                        
                        # Start position (in the feature map)
                        if color == self.color_palette["accent1"]:
                            start_pos = feature_vis1[i * 3 + j].get_center()
                        elif color == self.color_palette["accent2"]:
                            start_pos = feature_vis2[i * 3 + j].get_center()
                        else:
                            start_pos = feature_vis3[i * 3 + j].get_center()
                        
                        cell.move_to(start_pos)
                        
                        # End position (in the flattened vector)
                        end_pos = flattened_vector[offset].get_center()
                        offset += 1
                        
                        temp_squares.append((cell, end_pos))
            
            # Add all temp squares to the scene
            for cell, _ in temp_squares:
                self.add(cell)
            
            # Animate the flattening process
            animations = []
            for cell, end_pos in temp_squares:
                animations.append(cell.animate.move_to(end_pos))
            
            self.play(
                *animations,
                run_time=1.5,
                lag_ratio=0.05
            )
            
            # Remove temp squares and show the actual flattened vector
            for cell, _ in temp_squares:
                self.remove(cell)
            
            self.play(
                FadeIn(flattened_vector),
                Write(flatten_label)
            )
            self.wait(0.5)
            
            # Show connections to output neurons
            self.play(
                GrowArrow(arrow2)
            )
            
            self.play(
                FadeIn(output_neurons),
                Write(fc_label)
            )
            self.wait(0.3)
            
            # Show connections
            self.play(
                LaggedStartMap(Create, connections, lag_ratio=0.01),
                run_time=1.5
            )
            self.wait(0.3)
            
            # Highlight the prediction (random digit)
            predicted_digit = np.random.randint(0, 10)
            self.play(
                output_neurons[predicted_digit][0].animate.set_fill(self.color_palette["accent5"], opacity=1),
                Flash(output_neurons[predicted_digit], color=self.color_palette["accent5"], flash_radius=0.6),
                run_time=1
            )
            
            # Group everything for later reference
            self.fc_group = VGroup(
                feature_maps, feature_label,
                flattened_vector, flatten_label,
                output_neurons, fc_label,
                connections,
                arrow1, arrow2
            ) 