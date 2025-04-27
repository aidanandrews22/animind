import os
import json
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

# Load environment variables from .env file
load_dotenv()

class TransformerBaseScene(VoiceoverScene):
    """Base scene for Transformer video with common utilities and styling."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gtts_service = GTTSService()
        
        # Set up color scheme
        self.color_palette = {
            "background": "#F7F9FB",     # Light blue-gray (background)
            "text": "#333333",            # Dark gray (text)
            "query": "#00B5A3",           # Teal (Q)
            "key": "#FF8F3F",             # Orange (K)
            "value": "#9F7AEA",           # Purple (V) 
            "attention": "#FF5757",       # Red (attention weights)
            "embedding": "#4361EE",       # Blue (embeddings)
            "position": "#48BB78",        # Green (positional encoding)
            "softmax": "#F6AD55",         # Light orange (softmax)
            "vector": "#C2C9D1",          # Light gray (vectors)
            "highlight": "#FFF500"        # Yellow (highlights)
        }
        
        # Commonly used vector dimensions
        self.vector_width = 0.6
        self.vector_height = 3.0
        self.embedding_dim = 512  # Standard transformer embedding dimension
    
    def create_section_title(self, title_text):
        """Create a section title with styling."""
        title = Text(title_text, font_size=60, color=self.color_palette["text"])
        return title
    
    def create_subtitle(self, subtitle_text):
        """Create a subtitle with styling."""
        subtitle = Text(subtitle_text, font_size=36, color=self.color_palette["text"])
        return subtitle
    
    def create_gradient_background(self, color1=None, color2=None):
        """Create a gradient background."""
        if color1 is None:
            color1 = "#EEEEFF"  # Light lavender
        if color2 is None:
            color2 = "#FFFFFF"  # White
            
        # Create a rectangle with a gradient fill
        background = Rectangle(
            width=config.frame_width, 
            height=config.frame_height,
            fill_opacity=1.0
        )
        background.set_color(color=color1)
        
        # Fake a gradient effect using many rectangles with varying opacity
        gradient = VGroup()
        num_stripes = 20
        for i in range(num_stripes):
            stripe = Rectangle(
                width=config.frame_width,
                height=config.frame_height/num_stripes,
                fill_opacity=i/num_stripes,
                stroke_width=0
            )
            stripe.set_color(color2)
            stripe.move_to(
                [0, config.frame_height/2 - (i+0.5)*config.frame_height/num_stripes, 0]
            )
            gradient.add(stripe)
            
        return VGroup(background, gradient)
    
    def create_vector_block(self, height=None, width=None, label="", color=None):
        """Create a colored square block to represent a vector."""
        if height is None:
            height = self.vector_height
        if width is None:
            width = self.vector_width
        if color is None:
            color = self.color_palette["vector"]
            
        block = Rectangle(
            height=height,
            width=width,
            fill_opacity=1.0,
            fill_color=color,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        
        if label:
            text = Text(label, font_size=24)
            text.move_to(block)
            return VGroup(block, text)
        
        return block
    
    def create_word_embedding(self, word, color=None):
        """Create a word with its embedding vector block."""
        if color is None:
            color = self.color_palette["embedding"]
            
        word_text = Text(word, font_size=24)
        embedding = self.create_vector_block(color=color)
        embedding.next_to(word_text, DOWN, buff=0.2)
        
        return VGroup(word_text, embedding)
    
    def create_attention_matrix(self, matrix, cell_size=0.4, with_values=True, normalized=True):
        """Create a visual matrix for attention weights."""
        n_rows, n_cols = matrix.shape
        grid = VGroup()
        
        # Normalize values if requested
        if normalized and np.max(matrix) > 0:
            matrix = matrix / np.max(matrix)
        
        for i in range(n_rows):
            for j in range(n_cols):
                value = matrix[i, j]
                
                # Create cell
                cell = Square(side_length=cell_size)
                cell.set_stroke(WHITE, 1)
                
                # Color based on attention weight
                cell.set_fill(self.color_palette["attention"], opacity=value)
                
                # Position cell
                cell.move_to([j * cell_size - (n_cols - 1) * cell_size / 2, 
                             -i * cell_size + (n_rows - 1) * cell_size / 2, 0])
                
                # Add label for the value if requested
                if with_values:
                    label = Text(f"{value:.2f}", font_size=min(16, cell_size*30), color=WHITE)
                    label.move_to(cell)
                    grid.add(VGroup(cell, label))
                else:
                    grid.add(cell)
        
        return grid
    
    def create_matrix_equation(self, matrix1, matrix2, result_matrix=None, operation="×"):
        """Create a visual equation showing matrix multiplication."""
        eq_group = VGroup()
        
        eq_group.add(matrix1)
        
        # Add operation symbol
        op_symbol = MathTex(operation, font_size=40)
        op_symbol.next_to(matrix1, RIGHT)
        eq_group.add(op_symbol)
        
        # Add second matrix
        matrix2.next_to(op_symbol, RIGHT)
        eq_group.add(matrix2)
        
        # Add equals sign and result if provided
        if result_matrix is not None:
            equals = MathTex("=", font_size=40)
            equals.next_to(matrix2, RIGHT)
            eq_group.add(equals)
            
            result_matrix.next_to(equals, RIGHT)
            eq_group.add(result_matrix)
        
        return eq_group
    
    def create_sinusoidal_wave(self, freq=1, amplitude=1, color=BLUE):
        """Create a sinusoidal wave for positional encoding visualization."""
        axes = Axes(
            x_range=[0, 4*PI, PI/2],
            y_range=[-amplitude*1.2, amplitude*1.2, amplitude/2],
            axis_config={"include_tip": False, "include_numbers": False}
        )
        
        graph = axes.plot(lambda x: amplitude * np.sin(freq * x), color=color)
        
        return VGroup(axes, graph) 