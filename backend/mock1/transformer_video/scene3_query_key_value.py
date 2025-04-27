from manim import *
from utils import TransformerBaseScene
import numpy as np

class QueryKeyValueScene(TransformerBaseScene):
    """Third scene: Query, Key, Value projections."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create input sequence (reusing from previous scene)
        num_tokens = 6
        input_blocks = []
        
        for i in range(num_tokens):
            block = self.create_vector_block(
                height=1.5, 
                width=0.8, 
                label=f"x_{i+1}", 
                color=self.color_palette["embedding"]
            )
            input_blocks.append(block)
        
        input_row = VGroup(*input_blocks)
        input_row.arrange(RIGHT, buff=0.3)
        input_row.to_edge(UP, buff=1.5)
        
        # Create labels for Q, K, V rows
        q_label = MathTex("Q", font_size=40, color=self.color_palette["query"])
        k_label = MathTex("K", font_size=40, color=self.color_palette["key"])
        v_label = MathTex("V", font_size=40, color=self.color_palette["value"])
        
        # Position labels to the left of where the rows will be
        q_label.to_edge(LEFT, buff=1)
        k_label.next_to(q_label, DOWN, buff=2)
        v_label.next_to(k_label, DOWN, buff=2)
        
        # Create empty lists for Q, K, V blocks
        q_blocks = []
        k_blocks = []
        v_blocks = []
        
        # Animation sequence
        with self.voiceover(
            """Each embedding is projected into three spaces—queries, keys, and values. 
            Queries ask questions, keys store content, and values hold the information 
            we'll ultimately aggregate."""
        ):
            # Show the input sequence
            self.play(FadeIn(input_row))
            self.wait(0.5)
            
            # Show the Q, K, V labels
            self.play(
                Write(q_label),
                Write(k_label),
                Write(v_label)
            )
            
            # For each input block, create Q, K, V projections
            for i, input_block in enumerate(input_blocks):
                # Create Q, K, V blocks
                q_block = self.create_vector_block(
                    height=1.5, 
                    width=0.8, 
                    color=self.color_palette["query"]
                )
                k_block = self.create_vector_block(
                    height=1.5, 
                    width=0.8, 
                    color=self.color_palette["key"]
                )
                v_block = self.create_vector_block(
                    height=1.5, 
                    width=0.8, 
                    color=self.color_palette["value"]
                )
                
                # Set initial positions aligned with input block
                q_block.next_to(q_label, RIGHT, buff=1 + i*1.1)
                k_block.next_to(k_label, RIGHT, buff=1 + i*1.1)
                v_block.next_to(v_label, RIGHT, buff=1 + i*1.1)
                
                # Create projection arrows
                q_arrow = Arrow(
                    input_block.get_bottom(), 
                    q_block.get_top(), 
                    color=self.color_palette["query"],
                    buff=0.1
                )
                k_arrow = Arrow(
                    input_block.get_bottom(), 
                    k_block.get_top(), 
                    color=self.color_palette["key"],
                    buff=0.1
                )
                v_arrow = Arrow(
                    input_block.get_bottom(), 
                    v_block.get_top(),
                    color=self.color_palette["value"],
                    buff=0.1
                )
                
                # Animate the projections
                self.play(
                    GrowArrow(q_arrow),
                    GrowArrow(k_arrow),
                    GrowArrow(v_arrow),
                    run_time=0.5
                )
                
                self.play(
                    FadeIn(q_block),
                    FadeIn(k_block),
                    FadeIn(v_block),
                    run_time=0.5
                )
                
                # Add to lists
                q_blocks.append(q_block)
                k_blocks.append(k_block)
                v_blocks.append(v_block)
                
                # Fade out arrows for clarity
                self.play(
                    FadeOut(q_arrow),
                    FadeOut(k_arrow),
                    FadeOut(v_arrow),
                    run_time=0.3
                )
            
            # Group the blocks for easier reference
            q_row = VGroup(*q_blocks)
            k_row = VGroup(*k_blocks)
            v_row = VGroup(*v_blocks)
            
            # Add matrix weight labels
            w_q = MathTex("W^Q", font_size=36)
            w_k = MathTex("W^K", font_size=36)
            w_v = MathTex("W^V", font_size=36)
            
            # Position weight labels
            w_q.next_to(q_label, LEFT, buff=0.5)
            w_k.next_to(k_label, LEFT, buff=0.5)
            w_v.next_to(v_label, LEFT, buff=0.5)
            
            # Show weight labels
            self.play(
                Write(w_q),
                Write(w_k),
                Write(w_v)
            )
            
            # Highlight the three rows simultaneously to emphasize their parallel nature
            self.play(
                q_row.animate.set_stroke(self.color_palette["query"], width=3, opacity=1),
                k_row.animate.set_stroke(self.color_palette["key"], width=3, opacity=1),
                v_row.animate.set_stroke(self.color_palette["value"], width=3, opacity=1),
                run_time=1
            )
            
            self.wait(1)
            
            # Reset stroke
            self.play(
                q_row.animate.set_stroke(WHITE, width=1.5, opacity=1),
                k_row.animate.set_stroke(WHITE, width=1.5, opacity=1),
                v_row.animate.set_stroke(WHITE, width=1.5, opacity=1),
                run_time=0.5
            )
            
            self.wait(1) 