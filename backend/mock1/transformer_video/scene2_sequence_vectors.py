from manim import *
from utils import TransformerBaseScene
import numpy as np

class SequenceVectorsScene(TransformerBaseScene):
    """Second scene: Sequence as Vectors showing word embeddings."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Example sentence
        sentence = "The cat sat on the mat"
        words = sentence.split()
        
        # Create word objects
        word_objs = []
        for word in words:
            word_text = Text(word, font_size=36, color=self.color_palette["text"])
            word_objs.append(word_text)
        
        # Arrange words in a row
        word_row = VGroup(*word_objs)
        word_row.arrange(RIGHT, buff=0.5)
        word_row.to_edge(UP, buff=2)
        
        # Create empty array for vector blocks
        vector_blocks = []
        
        # Animation sequence
        with self.voiceover(
            """We start with a sequence of word embeddings—numeric vectors representing each token. 
            These embeddings carry semantic meaning in high-dimensional space."""
        ):
            # Show the sentence
            self.play(Write(word_row))
            self.wait(0.5)
            
            # Transform each word into a vector block
            for i, word_obj in enumerate(word_objs):
                # Create an embedding block
                vector_block = self.create_vector_block(
                    height=1.5, 
                    width=0.8, 
                    label=f"x_{i+1}", 
                    color=self.color_palette["embedding"]
                )
                
                # Position initially at the word
                vector_block.move_to(word_obj.get_center() + DOWN * 1.5)
                
                # Animate transformation
                self.play(
                    FadeIn(vector_block, shift=UP),
                    run_time=0.5
                )
                
                vector_blocks.append(vector_block)
            
            # Arrange vector blocks in a horizontal group
            vector_group = VGroup(*vector_blocks)
            target_positions = vector_group.copy()
            target_positions.arrange(RIGHT, buff=0.3)
            target_positions.next_to(word_row, DOWN, buff=2.5)
            
            # Animate blocks sliding into the horizontal arrangement
            for i, block in enumerate(vector_blocks):
                self.play(
                    block.animate.move_to(target_positions[i].get_center()),
                    run_time=0.3
                )
            
            # Add a brace to label the sequence
            brace = Brace(vector_group, DOWN)
            brace_label = Text("Input Sequence", font_size=28)
            brace_label.next_to(brace, DOWN)
            
            self.play(
                GrowFromCenter(brace),
                Write(brace_label)
            )
            
            self.wait(1) 