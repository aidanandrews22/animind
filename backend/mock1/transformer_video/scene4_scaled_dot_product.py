from manim import *
from utils import TransformerBaseScene
import numpy as np

class ScaledDotProductScene(TransformerBaseScene):
    """Fourth scene: Scaled Dot-Product Attention mechanism."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Number of tokens
        num_tokens = 6
        
        # Create a simple attention example
        # We'll highlight the first query and its interaction with all keys
        
        # Create Q, K, V rows from the previous scene
        q_blocks = []
        k_blocks = []
        v_blocks = []
        
        # Create labels for Q, K, V rows
        q_label = MathTex("Q", font_size=40, color=self.color_palette["query"])
        k_label = MathTex("K", font_size=40, color=self.color_palette["key"])
        v_label = MathTex("V", font_size=40, color=self.color_palette["value"])
        
        # Position labels
        q_label.to_edge(LEFT, buff=1).to_edge(UP, buff=1.5)
        k_label.next_to(q_label, DOWN, buff=1)
        v_label.next_to(k_label, DOWN, buff=1)
        
        # Create blocks for each row
        for i in range(num_tokens):
            q_block = self.create_vector_block(
                height=0.8, 
                width=0.6, 
                color=self.color_palette["query"]
            )
            k_block = self.create_vector_block(
                height=0.8, 
                width=0.6, 
                color=self.color_palette["key"]
            )
            v_block = self.create_vector_block(
                height=0.8, 
                width=0.6, 
                color=self.color_palette["value"]
            )
            
            q_blocks.append(q_block)
            k_blocks.append(k_block)
            v_blocks.append(v_block)
        
        # Arrange blocks in rows
        q_row = VGroup(*q_blocks)
        k_row = VGroup(*k_blocks)
        v_row = VGroup(*v_blocks)
        
        q_row.arrange(RIGHT, buff=0.3)
        k_row.arrange(RIGHT, buff=0.3)
        v_row.arrange(RIGHT, buff=0.3)
        
        q_row.next_to(q_label, RIGHT, buff=0.5)
        k_row.next_to(k_label, RIGHT, buff=0.5)
        v_row.next_to(v_label, RIGHT, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """Attention scores come from dot products between a query and each key, 
            scaled by the square root of their dimension, then normalized via softmax. 
            These weights determine how much we 'attend' to each value, which are then 
            aggregated into our output."""
        ):
            # Start with existing Q, K, V rows
            self.play(
                FadeIn(q_label), FadeIn(q_row),
                FadeIn(k_label), FadeIn(k_row),
                FadeIn(v_label), FadeIn(v_row)
            )
            
            # Highlight the first query vector
            highlighted_query = q_blocks[0].copy()
            highlighted_query.set_stroke(self.color_palette["highlight"], width=3)
            
            self.play(
                Transform(q_blocks[0], highlighted_query)
            )
            
            # Move the query down for the dot product visualization
            query_for_dot = q_blocks[0].copy()
            query_for_dot.generate_target()
            query_for_dot.target.move_to(DOWN * 0.5)
            
            self.play(
                MoveToTarget(query_for_dot)
            )
            
            # Dot products between the query and each key
            dot_product_results = []
            dot_product_equations = []
            
            for i, k_block in enumerate(k_blocks):
                # Create a copy of the key for the dot product
                key_for_dot = k_block.copy()
                
                # Move it next to the query
                key_for_dot.generate_target()
                key_for_dot.target.next_to(query_for_dot, RIGHT, buff=0.5)
                
                self.play(
                    MoveToTarget(key_for_dot),
                    run_time=0.5
                )
                
                # Create dot product symbol
                dot_symbol = MathTex("\\cdot", font_size=40)
                dot_symbol.move_to(
                    (query_for_dot.get_center() + key_for_dot.get_center()) / 2
                )
                
                # Create equals sign and result
                equals = MathTex("=", font_size=40)
                
                # For visual clarity, let's create fake dot product results
                # In a real implementation, these would be actual vector dot products
                dot_values = [0.2, 0.7, 0.4, 0.1, 0.3, 0.5]
                result = MathTex(f"{dot_values[i]:.1f}", font_size=40)
                
                equals.next_to(key_for_dot, RIGHT, buff=0.3)
                result.next_to(equals, RIGHT, buff=0.3)
                
                dot_product_results.append(result)
                
                # Group the equation
                equation = VGroup(query_for_dot, dot_symbol, key_for_dot, equals, result)
                dot_product_equations.append(equation)
                
                self.play(
                    FadeIn(dot_symbol),
                    FadeIn(equals),
                    FadeIn(result),
                    run_time=0.5
                )
                
                # Return the key to its original position
                self.play(
                    FadeOut(dot_symbol),
                    FadeOut(key_for_dot),
                    run_time=0.3
                )
            
            # Move the query back up
            self.play(
                FadeOut(query_for_dot),
                run_time=0.3
            )
            
            # Create a row to show scaled dot products
            scaled_results = []
            
            # Create scaling factor
            scaling_factor = MathTex("\\frac{1}{\\sqrt{d_k}}", font_size=36)
            scaling_factor.next_to(q_blocks[0], DOWN, buff=1.5)
            
            self.play(
                Write(scaling_factor)
            )
            
            # Show the scaling
            for i, result in enumerate(dot_product_results):
                # Create scaled result
                dot_values = [0.2, 0.7, 0.4, 0.1, 0.3, 0.5]
                scaled_val = dot_values[i] / np.sqrt(64)  # Assuming d_k = 64
                scaled_result = MathTex(f"{scaled_val:.3f}", font_size=36)
                
                # Position in a row
                if i == 0:
                    scaled_result.next_to(scaling_factor, RIGHT, buff=1.0)
                else:
                    scaled_result.next_to(scaled_results[i-1], RIGHT, buff=0.5)
                
                scaled_results.append(scaled_result)
                
                # Animation
                scaling_arrow = Arrow(
                    result.get_bottom(), 
                    scaled_result.get_top(), 
                    buff=0.1
                )
                
                self.play(
                    GrowArrow(scaling_arrow),
                    FadeIn(scaled_result),
                    run_time=0.4
                )
                
                self.play(
                    FadeOut(scaling_arrow),
                    run_time=0.2
                )
            
            # Group scaled results
            scaled_row = VGroup(*scaled_results)
            
            # Softmax
            softmax_label = Text("Softmax", font_size=36, color=self.color_palette["softmax"])
            softmax_label.next_to(scaled_row, DOWN, buff=1.5)
            
            self.play(
                Write(softmax_label)
            )
            
            # Create softmax probabilities
            attention_weights = []
            softmax_values = [0.1, 0.4, 0.2, 0.05, 0.15, 0.1]  # Normalized to sum to 1
            
            for i, value in enumerate(softmax_values):
                weight = MathTex(f"{value:.2f}", font_size=36, color=self.color_palette["attention"])
                
                # Position in a row
                if i == 0:
                    weight.next_to(softmax_label, RIGHT, buff=1.0)
                else:
                    weight.next_to(attention_weights[i-1], RIGHT, buff=0.5)
                
                attention_weights.append(weight)
                
                # Animation
                softmax_arrow = Arrow(
                    scaled_results[i].get_bottom(), 
                    weight.get_top(), 
                    buff=0.1,
                    color=self.color_palette["softmax"]
                )
                
                self.play(
                    GrowArrow(softmax_arrow),
                    FadeIn(weight),
                    run_time=0.4
                )
                
                self.play(
                    FadeOut(softmax_arrow),
                    run_time=0.2
                )
            
            # Group attention weights
            weight_row = VGroup(*attention_weights)
            
            # Final weighted sum of values
            weight_lines = []
            scaled_values = []
            
            for i, (weight, v_block) in enumerate(zip(attention_weights, v_blocks)):
                # Create lines from weights to value blocks
                weight_line = Line(
                    weight.get_center(), 
                    v_block.get_center(),
                    color=self.color_palette["attention"]
                )
                weight_line.set_opacity(softmax_values[i])
                weight_lines.append(weight_line)
                
                # Create scaled value blocks
                scaled_value = v_block.copy()
                scaled_value.set_opacity(softmax_values[i])
                scaled_values.append(scaled_value)
            
            # Show the weight lines connecting to values
            self.play(
                *[Create(line) for line in weight_lines],
                run_time=1
            )
            
            # Create the output vector
            output_vector = self.create_vector_block(
                height=0.8, 
                width=0.6, 
                color=self.color_palette["embedding"]
            )
            output_label = MathTex("Output", font_size=36)
            output_group = VGroup(output_vector, output_label)
            output_group.arrange(DOWN)
            output_group.to_edge(DOWN, buff=1)
            
            # Show the output vector
            self.play(
                FadeIn(output_group)
            )
            
            # Animate weighted values flowing into the output
            value_copies = [v.copy() for v in v_blocks]
            
            for i, (value, weight) in enumerate(zip(value_copies, softmax_values)):
                value.generate_target()
                value.target.scale(weight * 1.5).move_to(output_vector.get_center())
                
                self.play(
                    MoveToTarget(value),
                    run_time=0.3
                )
                
                self.play(
                    FadeOut(value),
                    run_time=0.2
                )
            
            # Highlight the final output
            output_highlight = output_vector.copy()
            output_highlight.set_stroke(self.color_palette["highlight"], width=3)
            
            self.play(
                Transform(output_vector, output_highlight)
            )
            
            self.wait(1) 