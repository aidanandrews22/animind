from manim import *
from utils import TransformerBaseScene
import numpy as np

class PositionalEncodingScene(TransformerBaseScene):
    """Sixth scene: Positional Encoding to add order information."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Number of tokens for demonstration
        num_tokens = 6
        
        # Create input embeddings
        embeddings = []
        for i in range(num_tokens):
            embedding = self.create_vector_block(
                height=1.2, 
                width=0.8, 
                label=f"x_{i+1}", 
                color=self.color_palette["embedding"]
            )
            embeddings.append(embedding)
        
        # Arrange embeddings in a row
        embedding_row = VGroup(*embeddings)
        embedding_row.arrange(RIGHT, buff=0.4)
        embedding_row.to_edge(UP, buff=2)
        
        # Create position indices
        position_indices = []
        for i in range(num_tokens):
            index = Text(f"pos={i}", font_size=24)
            index.next_to(embeddings[i], UP, buff=0.3)
            position_indices.append(index)
        
        position_indices_group = VGroup(*position_indices)
        
        # Animation sequence
        with self.voiceover(
            """Because attention has no inherent notion of order, we inject positional encodings—
            sinusoids of varying frequencies—so the model knows the position of each token in the 
            sequence."""
        ):
            # Show the input embeddings
            self.play(FadeIn(embedding_row))
            self.wait(0.5)
            
            # Show position indices
            self.play(Write(position_indices_group))
            self.wait(0.5)
            
            # Create sinusoidal waves for positional encoding visualization
            sin_waves = []
            cos_waves = []
            wave_axes = []
            
            # Different frequencies for visualization
            frequencies = [1, 2, 4, 8]
            
            for i, freq in enumerate(frequencies):
                # Create small axes for each wave
                axes = Axes(
                    x_range=[0, 8, 1],
                    y_range=[-1.2, 1.2, 0.5],
                    axis_config={"include_tip": False, "include_numbers": False},
                    x_length=4,
                    y_length=1.2
                )
                
                # Create sin and cos graphs
                sin_graph = axes.plot(
                    lambda x: np.sin(freq * x), 
                    color=self.color_palette["position"]
                )
                cos_graph = axes.plot(
                    lambda x: np.cos(freq * x), 
                    color=color_gradient([Color(self.color_palette["position"]), WHITE], 0.3)
                )
                
                # Position the waves
                if i == 0:
                    axes.next_to(embedding_row, DOWN, buff=1)
                else:
                    axes.next_to(wave_axes[i-1], DOWN, buff=0.5)
                
                # Add frequency label
                freq_label = MathTex(f"\\omega = {freq}", font_size=24)
                freq_label.next_to(axes, LEFT, buff=0.5)
                
                wave_axes.append(axes)
                sin_waves.append(sin_graph)
                cos_waves.append(cos_graph)
                
                # Show axes and label
                self.play(
                    Create(axes),
                    Write(freq_label),
                    run_time=0.5
                )
                
                # Show sin and cos waves
                self.play(
                    Create(sin_graph),
                    Create(cos_graph),
                    run_time=1
                )
            
            # Group all wave visualizations
            wave_group = VGroup(*wave_axes, *sin_waves, *cos_waves)
            
            # Create positional encoding blocks
            pos_encodings = []
            for i in range(num_tokens):
                pos_enc = self.create_vector_block(
                    height=1.2, 
                    width=0.8, 
                    color=self.color_palette["position"]
                )
                pos_enc.next_to(embeddings[i], DOWN, buff=1)
                pos_encodings.append(pos_enc)
            
            pos_encoding_row = VGroup(*pos_encodings)
            
            # Move sinusoidal visualization to the side
            self.play(
                wave_group.animate.scale(0.7).to_edge(LEFT, buff=0.5),
                run_time=1
            )
            
            # Show position encodings
            self.play(FadeIn(pos_encoding_row))
            
            # Create plus signs between embeddings and positional encodings
            plus_signs = []
            for i in range(num_tokens):
                plus = MathTex("+", font_size=36)
                plus.move_to((embeddings[i].get_center() + pos_encodings[i].get_center()) / 2)
                plus_signs.append(plus)
            
            plus_signs_group = VGroup(*plus_signs)
            
            # Show addition
            self.play(Write(plus_signs_group))
            
            # Create final embeddings with position information
            final_embeddings = []
            for i in range(num_tokens):
                final_emb = self.create_vector_block(
                    height=1.2, 
                    width=0.8, 
                    color=color_gradient([Color(self.color_palette["embedding"]),
                                        Color(self.color_palette["position"])], 0.3)
                )
                final_emb.next_to(pos_encodings[i], DOWN, buff=1)
                final_embeddings.append(final_emb)
            
            final_embedding_row = VGroup(*final_embeddings)
            
            # Animation for the addition of embeddings and positional encodings
            for i in range(num_tokens):
                # Create copies that will animate
                emb_copy = embeddings[i].copy()
                pos_copy = pos_encodings[i].copy()
                
                # Animate both flowing into the final position
                self.play(
                    emb_copy.animate.move_to(final_embeddings[i].get_center()),
                    pos_copy.animate.move_to(final_embeddings[i].get_center()),
                    run_time=0.5
                )
                
                # Show the result and fade out the copies
                self.play(
                    FadeIn(final_embeddings[i]),
                    FadeOut(emb_copy),
                    FadeOut(pos_copy),
                    run_time=0.3
                )
            
            # Add final label
            final_label = Text("Embeddings + Positional Encoding", font_size=36)
            final_label.next_to(final_embedding_row, DOWN, buff=0.5)
            
            self.play(Write(final_label))
            
            # Fade out the wave visualization
            self.play(FadeOut(wave_group))
            
            # Final highlight
            highlight = SurroundingRectangle(
                final_embedding_row,
                color=self.color_palette["highlight"],
                buff=0.3
            )
            
            self.play(Create(highlight))
            
            self.wait(1) 