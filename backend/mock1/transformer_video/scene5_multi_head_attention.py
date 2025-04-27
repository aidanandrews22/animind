from manim import *
from utils import TransformerBaseScene
import numpy as np

class MultiHeadAttentionScene(TransformerBaseScene):
    """Fifth scene: Multi-Head Attention mechanism."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Set up the number of heads and tokens
        num_heads = 4
        num_tokens = 6
        
        # Create the input representation (a row of embedding vectors)
        input_blocks = []
        for i in range(num_tokens):
            block = self.create_vector_block(
                height=0.8, 
                width=0.6, 
                label=f"x_{i+1}", 
                color=self.color_palette["embedding"]
            )
            input_blocks.append(block)
        
        input_row = VGroup(*input_blocks)
        input_row.arrange(RIGHT, buff=0.3)
        input_row.to_edge(UP, buff=1.5)
        
        # Animation sequence
        with self.voiceover(
            """Transformers use multiple attention heads in parallel—each learning to focus on 
            different relationships. Their outputs are concatenated and linearly transformed 
            back into our model's dimension."""
        ):
            # Show the input sequence
            self.play(FadeIn(input_row))
            self.wait(0.5)
            
            # Create the multi-head structure
            head_boxes = []
            head_labels = []
            
            for i in range(num_heads):
                # Create a box for each attention head
                head_box = Rectangle(
                    height=2.5, 
                    width=6, 
                    fill_color=self.color_palette["vector"],
                    fill_opacity=0.3,
                    stroke_color=WHITE,
                    stroke_width=2
                )
                
                # Position the boxes in a vertical arrangement
                if i == 0:
                    head_box.next_to(input_row, DOWN, buff=1)
                else:
                    head_box.next_to(head_boxes[i-1], DOWN, buff=0.5)
                
                head_boxes.append(head_box)
                
                # Add a label for each head
                head_label = Text(f"Head {i+1}", font_size=28)
                head_label.next_to(head_box, LEFT, buff=0.5)
                head_labels.append(head_label)
                
                # Add the head components (simplified representation)
                q_label = MathTex("Q_" + str(i+1), font_size=28, color=self.color_palette["query"])
                k_label = MathTex("K_" + str(i+1), font_size=28, color=self.color_palette["key"])
                v_label = MathTex("V_" + str(i+1), font_size=28, color=self.color_palette["value"])
                
                attn_label = Text("Attention", font_size=24)
                
                # Position components within the head box
                q_label.move_to(head_box.get_left() + RIGHT * 1 + UP * 0.5)
                k_label.next_to(q_label, RIGHT, buff=0.5)
                v_label.next_to(k_label, RIGHT, buff=0.5)
                
                attn_label.move_to(head_box.get_center())
                
                # Create an output block for each head
                output_block = self.create_vector_block(
                    height=0.8, 
                    width=0.6, 
                    color=self.color_palette["embedding"]
                )
                output_block.move_to(head_box.get_right() + LEFT * 1)
                
                # Group all elements for this head
                head_elements = VGroup(head_box, q_label, k_label, v_label, attn_label, output_block)
                
                # Show the attention head
                if i == 0:
                    # For the first head, do a more detailed animation
                    self.play(
                        Create(head_box),
                        Write(head_label)
                    )
                    
                    self.play(
                        Write(q_label),
                        Write(k_label),
                        Write(v_label)
                    )
                    
                    self.play(
                        Write(attn_label)
                    )
                    
                    self.play(
                        FadeIn(output_block)
                    )
                else:
                    # For subsequent heads, animate all at once for brevity
                    self.play(
                        Create(head_box),
                        Write(head_label),
                        Write(q_label),
                        Write(k_label),
                        Write(v_label),
                        Write(attn_label),
                        FadeIn(output_block)
                    )
            
            # Create arrows from input to each head
            input_arrows = []
            for head_box in head_boxes:
                arrow = Arrow(
                    input_row.get_center() + DOWN * 0.5,
                    head_box.get_top(),
                    buff=0.1
                )
                input_arrows.append(arrow)
            
            # Show the input connections
            self.play(
                *[GrowArrow(arrow) for arrow in input_arrows],
                run_time=1
            )
            
            # Create outputs for each head
            head_outputs = []
            for i, head_box in enumerate(head_boxes):
                output = self.create_vector_block(
                    height=0.8, 
                    width=0.6, 
                    color=self.color_palette["embedding"]
                )
                
                # Position outputs in a row
                output.next_to(head_box, RIGHT, buff=1)
                
                head_outputs.append(output)
                
                # Create arrow from head to output
                output_arrow = Arrow(
                    head_box.get_right(),
                    output.get_left(),
                    buff=0.1
                )
                
                # Show the output and arrow
                self.play(
                    GrowArrow(output_arrow),
                    FadeIn(output),
                    run_time=0.5
                )
            
            # Group head outputs
            output_row = VGroup(*head_outputs)
            
            # Create the concatenation operation
            concat_box = Rectangle(
                height=3, 
                width=1, 
                fill_color=self.color_palette["vector"],
                fill_opacity=0.3,
                stroke_color=WHITE,
                stroke_width=2
            )
            concat_box.next_to(output_row, RIGHT, buff=1.5)
            
            concat_label = Text("Concat", font_size=28)
            concat_label.next_to(concat_box, UP, buff=0.3)
            
            # Show the concatenation box
            self.play(
                Create(concat_box),
                Write(concat_label)
            )
            
            # Create arrows from each output to the concatenation
            concat_arrows = []
            for output in head_outputs:
                arrow = Arrow(
                    output.get_right(),
                    concat_box.get_left() + UP * (output.get_center()[1] - concat_box.get_center()[1]),
                    buff=0.1
                )
                concat_arrows.append(arrow)
            
            # Show the concatenation arrows
            self.play(
                *[GrowArrow(arrow) for arrow in concat_arrows],
                run_time=1
            )
            
            # Create the final projection
            proj_label = MathTex("W_O", font_size=36)
            proj_label.next_to(concat_box, RIGHT, buff=0.5)
            
            final_output = self.create_vector_block(
                height=1.2, 
                width=0.8, 
                color=self.color_palette["embedding"]
            )
            final_output.next_to(proj_label, RIGHT, buff=0.5)
            
            final_label = Text("Multi-Head\nAttention\nOutput", font_size=24)
            final_label.next_to(final_output, DOWN, buff=0.3)
            
            # Show the final projection
            self.play(
                Write(proj_label)
            )
            
            # Show the final output
            final_arrow = Arrow(
                concat_box.get_right(),
                final_output.get_left(),
                buff=0.1
            )
            
            self.play(
                GrowArrow(final_arrow),
                FadeIn(final_output),
                Write(final_label)
            )
            
            # Highlight the entire multi-head structure
            highlight_box = SurroundingRectangle(
                VGroup(input_row, *head_boxes, output_row, concat_box, final_output),
                color=self.color_palette["highlight"],
                buff=0.5
            )
            
            self.play(
                Create(highlight_box)
            )
            
            self.wait(1) 