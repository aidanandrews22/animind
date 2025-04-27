from manim import *
from utils import CNNBaseScene
import numpy as np

class TrainingScene(CNNBaseScene):
    """Ninth scene: Training and Backpropagation of CNNs."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a simplified CNN architecture diagram
        # Input
        input_box = Rectangle(height=2, width=1, fill_color=self.color_palette["background"], 
                            fill_opacity=1, stroke_color=self.color_palette["text"])
        input_label = Text("Input", font_size=20, color=self.color_palette["text"])
        input_label.move_to(input_box)
        input_group = VGroup(input_box, input_label)
        input_group.to_edge(LEFT, buff=1.5)
        
        # Convolution layers
        conv1 = Rectangle(height=1.8, width=0.8, fill_color=self.color_palette["accent1"], 
                         fill_opacity=0.5, stroke_color=self.color_palette["accent1"])
        conv1_label = Text("Conv1", font_size=16, color=self.color_palette["text"])
        conv1_label.move_to(conv1)
        conv1_group = VGroup(conv1, conv1_label)
        conv1_group.next_to(input_group, RIGHT, buff=0.5)
        
        conv2 = Rectangle(height=1.5, width=0.8, fill_color=self.color_palette["accent1"], 
                         fill_opacity=0.5, stroke_color=self.color_palette["accent1"])
        conv2_label = Text("Conv2", font_size=16, color=self.color_palette["text"])
        conv2_label.move_to(conv2)
        conv2_group = VGroup(conv2, conv2_label)
        conv2_group.next_to(conv1_group, RIGHT, buff=0.5)
        
        # Fully connected layer
        fc = Rectangle(height=1.2, width=0.8, fill_color=self.color_palette["accent2"], 
                     fill_opacity=0.5, stroke_color=self.color_palette["accent2"])
        fc_label = Text("FC", font_size=16, color=self.color_palette["text"])
        fc_label.move_to(fc)
        fc_group = VGroup(fc, fc_label)
        fc_group.next_to(conv2_group, RIGHT, buff=0.5)
        
        # Output
        output_box = Rectangle(height=1, width=1, fill_color=self.color_palette["background"], 
                             fill_opacity=1, stroke_color=self.color_palette["text"])
        output_label = Text("Output", font_size=20, color=self.color_palette["text"])
        output_label.move_to(output_box)
        output_group = VGroup(output_box, output_label)
        output_group.next_to(fc_group, RIGHT, buff=0.5)
        
        # Forward arrows
        forward_arrows = VGroup()
        for i, (start, end) in enumerate([
            (input_group, conv1_group),
            (conv1_group, conv2_group),
            (conv2_group, fc_group),
            (fc_group, output_group)
        ]):
            arrow = Arrow(
                start.get_right(), 
                end.get_left(),
                buff=0.1,
                color=self.color_palette["text"]
            )
            forward_arrows.add(arrow)
        
        # Backward arrows (for backpropagation)
        backward_arrows = VGroup()
        for i, (start, end) in enumerate([
            (output_group, fc_group),
            (fc_group, conv2_group),
            (conv2_group, conv1_group),
            (conv1_group, input_group)
        ]):
            arrow = Arrow(
                start.get_left() + DOWN * 0.2, 
                end.get_right() + DOWN * 0.2,
                buff=0.1,
                color=self.color_palette["accent2"]
            )
            backward_arrows.add(arrow)
        
        # Group the entire network
        network = VGroup(
            input_group, conv1_group, conv2_group, fc_group, output_group,
            forward_arrows
        )
        
        # Create a loss curve
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 1, 0.2],
            axis_config={
                "color": self.color_palette["text"],
                "include_numbers": True
            },
            x_length=4,
            y_length=3
        )
        
        x_label = Text("Epochs", font_size=20, color=self.color_palette["text"])
        x_label.next_to(axes.x_axis, DOWN)
        
        y_label = Text("Loss", font_size=20, color=self.color_palette["text"])
        y_label.next_to(axes.y_axis, LEFT)
        
        # Create a decreasing loss curve
        loss_values = [0.9, 0.7, 0.55, 0.42, 0.32, 0.25, 0.2, 0.17, 0.15, 0.13]
        loss_points = [axes.coords_to_point(x, y) for x, y in enumerate(loss_values)]
        loss_graph = VMobject()
        loss_graph.set_points_as_corners(loss_points)
        loss_graph.set_stroke(self.color_palette["accent2"], 3)
        
        # Add dots for each epoch
        dots = VGroup()
        for point in loss_points:
            dot = Dot(point, radius=0.05, color=self.color_palette["accent2"])
            dots.add(dot)
        
        # Position the loss curve
        loss_group = VGroup(axes, x_label, y_label, loss_graph, dots)
        loss_group.scale(0.9)
        loss_group.to_edge(DOWN + RIGHT, buff=0.5)
        
        # Create a target/expected output
        target = Text("Expected: 7", font_size=24, color=self.color_palette["accent3"])
        target.next_to(output_group, UP, buff=0.5)
        
        # Create a prediction with error
        prediction = Text("Predicted: 2", font_size=24, color=self.color_palette["accent2"])
        prediction.next_to(output_group, DOWN, buff=0.5)
        
        # Create a loss indicator
        loss_indicator = Text("Loss", font_size=24, color=self.color_palette["accent2"])
        loss_indicator.next_to(prediction, DOWN, buff=0.5)
        
        # Create a tick mark for correct prediction (will be shown at the end)
        tick = Text("✓", font_size=48, color=self.color_palette["accent3"])
        tick.move_to(prediction.get_center())
        
        # Animation sequence
        with self.voiceover(
            """During training, backpropagation nudges each filter's weights to minimize error. 
            Over many images and iterations, CNNs become incredibly accurate at tasks like 
            object detection and classification."""
        ):
            # Show network architecture
            self.play(
                FadeIn(input_group),
                FadeIn(conv1_group),
                FadeIn(conv2_group),
                FadeIn(fc_group),
                FadeIn(output_group),
                *[GrowArrow(arrow) for arrow in forward_arrows]
            )
            self.wait(0.5)
            
            # Show target and initial prediction
            self.play(
                Write(target),
                Write(prediction)
            )
            self.wait(0.5)
            
            # Show loss indicator
            self.play(
                Write(loss_indicator)
            )
            self.wait(0.3)
            
            # Show loss curve axes
            self.play(
                Create(axes),
                Write(x_label),
                Write(y_label)
            )
            self.wait(0.3)
            
            # Show backpropagation in action with multiple training iterations
            for i in range(5):  # 5 training iterations
                # Show backward arrows for backpropagation
                self.play(
                    *[GrowArrow(arrow) for arrow in backward_arrows],
                    run_time=0.8
                )
                
                # Update weights (simulated by slight color changes)
                self.play(
                    conv1.animate.set_fill(
                        interpolate_color(
                            self.color_palette["accent1"], 
                            self.color_palette["accent4"], 
                            0.2 * (i + 1)
                        ),
                        opacity=0.5
                    ),
                    conv2.animate.set_fill(
                        interpolate_color(
                            self.color_palette["accent1"], 
                            self.color_palette["accent4"], 
                            0.2 * (i + 1)
                        ),
                        opacity=0.5
                    ),
                    fc.animate.set_fill(
                        interpolate_color(
                            self.color_palette["accent2"], 
                            self.color_palette["accent4"], 
                            0.2 * (i + 1)
                        ),
                        opacity=0.5
                    ),
                    run_time=0.5
                )
                
                # Update prediction (for the last iteration, show correct prediction)
                if i < 4:
                    new_prediction = Text(f"Predicted: {9 - i}", font_size=24, color=self.color_palette["accent2"])
                else:
                    new_prediction = Text("Predicted: 7", font_size=24, color=self.color_palette["accent3"])
                
                new_prediction.move_to(prediction.get_center())
                self.play(
                    Transform(prediction, new_prediction),
                    run_time=0.5
                )
                
                # Update loss curve for this iteration
                if i == 0:
                    # Start the loss curve
                    self.play(
                        Create(loss_graph),
                        FadeIn(dots),
                        run_time=1
                    )
                else:
                    # Continue the loss curve
                    updated_graph = VMobject()
                    updated_graph.set_points_as_corners(loss_points[:i+2])
                    updated_graph.set_stroke(self.color_palette["accent2"], 3)
                    
                    updated_dots = VGroup()
                    for j in range(i+2):
                        dot = Dot(loss_points[j], radius=0.05, color=self.color_palette["accent2"])
                        updated_dots.add(dot)
                    
                    self.play(
                        Transform(loss_graph, updated_graph),
                        Transform(dots, updated_dots),
                        run_time=0.5
                    )
                
                # Remove backward arrows for next forward pass
                self.play(
                    *[FadeOut(arrow) for arrow in backward_arrows],
                    run_time=0.5
                )
            
            # Show a tick mark over the correct prediction
            self.play(
                Flash(prediction, color=self.color_palette["accent3"], flash_radius=0.7),
                run_time=0.5
            )
            
            # Final view of the trained network and completed loss curve
            self.play(
                self.camera.frame.animate.scale(0.9).shift(DOWN * 0.2),
                run_time=1
            )
            self.wait(1)
            
            # Group everything for later reference
            self.training_group = VGroup(
                network, loss_group, target, prediction, loss_indicator
            ) 