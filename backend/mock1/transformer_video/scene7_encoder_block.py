from manim import *
from utils import TransformerBaseScene
import numpy as np

class EncoderBlockScene(TransformerBaseScene):
    """Seventh scene: Encoder Block Structure."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Define the components of an encoder block
        title = Text("Transformer Encoder Layer", font_size=48)
        title.to_edge(UP, buff=0.5)
        
        # Create blocks for the different components of the encoder
        block_width = 6
        block_height = 1.2
        
        # Multi-head attention block
        attention_block = Rectangle(
            width=block_width,
            height=block_height,
            fill_color=self.color_palette["query"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=2
        )
        attention_label = Text("Multi-Head Attention", font_size=32)
        attention_label.move_to(attention_block)
        attention_group = VGroup(attention_block, attention_label)
        
        # Add & Norm 1
        add_norm1_block = Rectangle(
            width=block_width,
            height=block_height,
            fill_color=self.color_palette["vector"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=2
        )
        add_norm1_label = Text("Add & Normalize", font_size=32)
        add_norm1_label.move_to(add_norm1_block)
        add_norm1_group = VGroup(add_norm1_block, add_norm1_label)
        add_norm1_group.next_to(attention_group, DOWN, buff=0.5)
        
        # Feed Forward Network
        ffn_block = Rectangle(
            width=block_width,
            height=block_height,
            fill_color=self.color_palette["embedding"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=2
        )
        ffn_label = Text("Feed-Forward Network", font_size=32)
        ffn_label.move_to(ffn_block)
        ffn_group = VGroup(ffn_block, ffn_label)
        ffn_group.next_to(add_norm1_group, DOWN, buff=0.5)
        
        # Add & Norm 2
        add_norm2_block = Rectangle(
            width=block_width,
            height=block_height,
            fill_color=self.color_palette["vector"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=2
        )
        add_norm2_label = Text("Add & Normalize", font_size=32)
        add_norm2_label.move_to(add_norm2_block)
        add_norm2_group = VGroup(add_norm2_block, add_norm2_label)
        add_norm2_group.next_to(ffn_group, DOWN, buff=0.5)
        
        # Position the first block
        attention_group.next_to(title, DOWN, buff=1)
        
        # Create arrows for the main flow
        arrow1 = Arrow(
            attention_group.get_bottom(),
            add_norm1_group.get_top(),
            buff=0.1
        )
        
        arrow2 = Arrow(
            add_norm1_group.get_bottom(),
            ffn_group.get_top(),
            buff=0.1
        )
        
        arrow3 = Arrow(
            ffn_group.get_bottom(),
            add_norm2_group.get_top(),
            buff=0.1
        )
        
        # Create residual connections
        residual1_start = attention_group.get_top() + LEFT * 2
        residual1_end = add_norm1_group.get_top() + LEFT * 2
        
        residual1 = CurvedArrow(
            residual1_start,
            residual1_end,
            angle=TAU/4
        )
        
        residual2_start = add_norm1_group.get_top() + RIGHT * 2
        residual2_end = add_norm2_group.get_top() + RIGHT * 2
        
        residual2 = CurvedArrow(
            residual2_start,
            residual2_end,
            angle=-TAU/4
        )
        
        # Input and Output labels
        input_label = Text("Input", font_size=24)
        input_label.next_to(attention_group, UP, buff=0.5).shift(LEFT * 2)
        
        output_label = Text("Output", font_size=24)
        output_label.next_to(add_norm2_group, DOWN, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """An encoder layer stacks multi-head attention with residual connections and 
            normalization, followed by a position-wise feed-forward network—letting the model 
            learn both context and transformation."""
        ):
            # Show the title
            self.play(Write(title))
            
            # Show the input label
            self.play(Write(input_label))
            
            # Show each component in sequence
            self.play(FadeIn(attention_group))
            self.play(GrowArrow(arrow1))
            self.play(FadeIn(add_norm1_group))
            
            # Show first residual connection
            self.play(Create(residual1))
            
            # Continue with the main flow
            self.play(GrowArrow(arrow2))
            self.play(FadeIn(ffn_group))
            self.play(GrowArrow(arrow3))
            self.play(FadeIn(add_norm2_group))
            
            # Show second residual connection
            self.play(Create(residual2))
            
            # Show output label
            self.play(Write(output_label))
            
            # Highlight the complete block
            encoder_block = VGroup(
                attention_group, add_norm1_group, 
                ffn_group, add_norm2_group,
                arrow1, arrow2, arrow3,
                residual1, residual2
            )
            
            block_highlight = SurroundingRectangle(
                encoder_block,
                color=self.color_palette["highlight"],
                buff=0.3
            )
            
            encoder_block_label = Text("Encoder Block", font_size=36, color=self.color_palette["highlight"])
            encoder_block_label.next_to(block_highlight, LEFT, buff=0.5)
            
            self.play(
                Create(block_highlight),
                Write(encoder_block_label)
            )
            
            # Show more details about components (optional annotations)
            attention_details = Text("Self-attention\nmechanism", font_size=20)
            attention_details.next_to(attention_block, LEFT, buff=0.5)
            
            ffn_details = Text("Two linear layers\nwith ReLU", font_size=20)
            ffn_details.next_to(ffn_block, RIGHT, buff=0.5)
            
            self.play(
                Write(attention_details),
                Write(ffn_details)
            )
            
            self.wait(1)
            
            # Emphasize the full structure
            self.play(
                block_highlight.animate.set_stroke(width=4),
                run_time=0.5
            )
            
            self.wait(1) 