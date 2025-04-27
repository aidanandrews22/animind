from manim import *
from utils import CNNBaseScene
import numpy as np

class StackingLayersScene(CNNBaseScene):
    """Seventh scene: Stacking multiple CNN layers."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Define the CNN architecture blocks for visualization
        # Each block represents Convolution -> Activation -> Pooling
        
        # Image
        image_block = Rectangle(height=2, width=2, fill_color=self.color_palette["background"], 
                               fill_opacity=1, stroke_color=self.color_palette["text"])
        image_block.set_fill(self.color_palette["background"], opacity=1)
        image_icon = Text("Input\nImage", font_size=20, color=self.color_palette["text"])
        image_icon.move_to(image_block)
        image = VGroup(image_block, image_icon)
        image.to_edge(LEFT, buff=1)
        
        # Layer 1
        layer1_conv = Rectangle(height=1.8, width=1, fill_color=self.color_palette["accent1"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent1"])
        layer1_relu = Rectangle(height=1.8, width=0.3, fill_color=self.color_palette["accent2"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent2"])
        layer1_pool = Rectangle(height=0.9, width=1, fill_color=self.color_palette["accent3"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent3"])
        
        layer1_conv.next_to(image, RIGHT, buff=0.2)
        layer1_relu.next_to(layer1_conv, RIGHT, buff=0.05)
        layer1_pool.next_to(layer1_relu, RIGHT, buff=0.2)
        
        # Layer 1 labels
        layer1_conv_label = Text("Conv", font_size=16, color=self.color_palette["text"])
        layer1_conv_label.move_to(layer1_conv)
        
        layer1_relu_label = Text("ReLU", font_size=16, color=self.color_palette["text"])
        layer1_relu_label.rotate(PI/2)
        layer1_relu_label.move_to(layer1_relu)
        
        layer1_pool_label = Text("Pool", font_size=16, color=self.color_palette["text"])
        layer1_pool_label.move_to(layer1_pool)
        
        layer1 = VGroup(layer1_conv, layer1_conv_label, layer1_relu, layer1_relu_label, 
                       layer1_pool, layer1_pool_label)
        
        # Layer 2
        layer2_conv = Rectangle(height=0.8, width=0.9, fill_color=self.color_palette["accent1"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent1"])
        layer2_relu = Rectangle(height=0.8, width=0.3, fill_color=self.color_palette["accent2"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent2"])
        layer2_pool = Rectangle(height=0.4, width=0.9, fill_color=self.color_palette["accent3"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent3"])
        
        layer2_conv.next_to(layer1_pool, RIGHT, buff=0.2)
        layer2_relu.next_to(layer2_conv, RIGHT, buff=0.05)
        layer2_pool.next_to(layer2_relu, RIGHT, buff=0.2)
        
        # Layer 2 labels
        layer2_conv_label = Text("Conv", font_size=14, color=self.color_palette["text"])
        layer2_conv_label.move_to(layer2_conv)
        
        layer2_relu_label = Text("ReLU", font_size=14, color=self.color_palette["text"])
        layer2_relu_label.rotate(PI/2)
        layer2_relu_label.move_to(layer2_relu)
        
        layer2_pool_label = Text("Pool", font_size=14, color=self.color_palette["text"])
        layer2_pool_label.move_to(layer2_pool)
        
        layer2 = VGroup(layer2_conv, layer2_conv_label, layer2_relu, layer2_relu_label, 
                       layer2_pool, layer2_pool_label)
        
        # Layer 3 
        layer3_conv = Rectangle(height=0.4, width=0.8, fill_color=self.color_palette["accent1"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent1"])
        layer3_relu = Rectangle(height=0.4, width=0.3, fill_color=self.color_palette["accent2"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent2"])
        layer3_pool = Rectangle(height=0.2, width=0.8, fill_color=self.color_palette["accent3"], 
                               fill_opacity=0.5, stroke_color=self.color_palette["accent3"])
        
        layer3_conv.next_to(layer2_pool, RIGHT, buff=0.2)
        layer3_relu.next_to(layer3_conv, RIGHT, buff=0.05)
        layer3_pool.next_to(layer3_relu, RIGHT, buff=0.2)
        
        # Layer 3 labels
        layer3_conv_label = Text("Conv", font_size=12, color=self.color_palette["text"])
        layer3_conv_label.move_to(layer3_conv)
        
        layer3_relu_label = Text("ReLU", font_size=12, color=self.color_palette["text"])
        layer3_relu_label.rotate(PI/2)
        layer3_relu_label.move_to(layer3_relu)
        
        layer3_pool_label = Text("Pool", font_size=12, color=self.color_palette["text"])
        layer3_pool_label.move_to(layer3_pool)
        
        layer3 = VGroup(layer3_conv, layer3_conv_label, layer3_relu, layer3_relu_label, 
                       layer3_pool, layer3_pool_label)
        
        # Layer labels with braces
        layer1_brace = Brace(layer1, DOWN)
        layer1_text = layer1_brace.get_text("Layer 1")
        
        layer2_brace = Brace(layer2, DOWN)
        layer2_text = layer2_brace.get_text("Layer 2")
        
        layer3_brace = Brace(layer3, DOWN)
        layer3_text = layer3_brace.get_text("Layer 3")
        
        # Arrows between layers
        arrow1 = Arrow(
            image.get_right(), 
            layer1_conv.get_left(),
            buff=0.1,
            color=self.color_palette["text"]
        )
        
        arrow2 = Arrow(
            layer1_pool.get_right(), 
            layer2_conv.get_left(),
            buff=0.1,
            color=self.color_palette["text"]
        )
        
        arrow3 = Arrow(
            layer2_pool.get_right(), 
            layer3_conv.get_left(),
            buff=0.1,
            color=self.color_palette["text"]
        )
        
        # Feature visualizations
        low_level_features = VGroup()
        for i in range(3):
            for j in range(3):
                feature = Line(
                    start=[-0.2 + 0.2*j, 0.2 - 0.2*i, 0],
                    end=[0.2 + 0.2*j, -0.2 - 0.2*i, 0],
                    stroke_width=2,
                    color=self.color_palette["accent1"]
                )
                low_level_features.add(feature)
        
        mid_level_features = VGroup()
        for i in range(2):
            feature = Arc(
                radius=0.3,
                start_angle=PI/2,
                angle=-PI,
                stroke_width=2,
                color=self.color_palette["accent2"]
            )
            feature.shift(RIGHT * 0.7 * i - 0.35)
            mid_level_features.add(feature)
        
        high_level_features = VGroup(
            RegularPolygon(
                n=5,
                stroke_width=2,
                color=self.color_palette["accent3"]
            )
        )
        
        # Position feature visualizations
        low_level_features.scale(0.4)
        low_level_features.next_to(layer1_brace, DOWN, buff=0.5)
        
        mid_level_features.scale(0.4)
        mid_level_features.next_to(layer2_brace, DOWN, buff=0.5)
        
        high_level_features.scale(0.4)
        high_level_features.next_to(layer3_brace, DOWN, buff=0.5)
        
        # Title
        title = Text("CNN Layer Hierarchy", font_size=36, color=self.color_palette["text"])
        title.to_edge(UP, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """By stacking these blocks, a CNN learns hierarchical features: 
            from simple edges in early layers to complex shapes in deeper ones."""
        ):
            # Show title
            self.play(
                Write(title)
            )
            self.wait(0.5)
            
            # Show input image
            self.play(
                FadeIn(image)
            )
            self.wait(0.3)
            
            # Show first layer
            self.play(
                GrowArrow(arrow1)
            )
            
            self.play(
                FadeIn(layer1_conv),
                FadeIn(layer1_conv_label)
            )
            
            self.play(
                FadeIn(layer1_relu),
                FadeIn(layer1_relu_label)
            )
            
            self.play(
                FadeIn(layer1_pool),
                FadeIn(layer1_pool_label)
            )
            
            self.play(
                GrowFromCenter(layer1_brace),
                Write(layer1_text)
            )
            
            # Show low-level features
            self.play(
                FadeIn(low_level_features)
            )
            self.wait(0.3)
            
            # Show second layer
            self.play(
                GrowArrow(arrow2)
            )
            
            self.play(
                FadeIn(layer2)
            )
            
            self.play(
                GrowFromCenter(layer2_brace),
                Write(layer2_text)
            )
            
            # Show mid-level features
            self.play(
                FadeIn(mid_level_features)
            )
            self.wait(0.3)
            
            # Show third layer
            self.play(
                GrowArrow(arrow3)
            )
            
            self.play(
                FadeIn(layer3)
            )
            
            self.play(
                GrowFromCenter(layer3_brace),
                Write(layer3_text)
            )
            
            # Show high-level features
            self.play(
                FadeIn(high_level_features)
            )
            self.wait(0.3)
            
            # Zoom out to see the whole pipeline
            self.camera.frame.save_state()
            self.play(
                self.camera.frame.animate.set(width=14),
                run_time=1.5
            )
            self.wait(0.5)
            
            # Group everything for later reference
            self.stacking_group = VGroup(
                title, image,
                layer1, layer1_brace, layer1_text, low_level_features,
                layer2, layer2_brace, layer2_text, mid_level_features,
                layer3, layer3_brace, layer3_text, high_level_features,
                arrow1, arrow2, arrow3
            ) 