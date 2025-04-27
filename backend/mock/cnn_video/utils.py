import os
import json
from pathlib import Path
from google.cloud import texttospeech
from dotenv import load_dotenv
import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

# Load environment variables from .env file
load_dotenv()

# Print to help with debugging
print(f"Google API Key: {os.environ.get('GOOGLE_API_KEY', 'Not found')[:10]}...")

def get_google_tts_client():
    """Get a Google Text-to-Speech client."""
    return texttospeech.TextToSpeechClient()

def text_to_speech(text, output_file, language_code="en-US", voice_name="en-US-Neural2-F"):
    """Convert text to speech using Google Cloud TTS.
    
    Args:
        text: The text to convert to speech.
        output_file: The path to the output file.
        language_code: The language code.
        voice_name: The voice name.
    """
    client = get_google_tts_client()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # Make sure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the response to the output file.
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    return output_file

class CNNBaseScene(VoiceoverScene):
    """Base scene for CNN video with common utilities and styling."""
    
    CONFIG = {
        "camera_config": {"background_color": "#FFFFFF"},  # White background
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gtts_service = GTTSService()
        
        # Set up color scheme
        self.color_palette = {
            "background": "#F7F9FB",  # Light blue-gray
            "text": "#333333",        # Dark gray
            "accent1": "#3B80FF",     # Blue
            "accent2": "#FF6B6B",     # Red
            "accent3": "#48BB78",     # Green
            "accent4": "#9F7AEA",     # Purple
            "accent5": "#F6AD55"      # Orange
        }

    def create_section_title(self, title_text):
        """Create a section title with styling."""
        title = Text(title_text, font_size=48, color=self.color_palette["text"])
        return title
    
    def create_subtitle(self, subtitle_text):
        """Create a subtitle with styling."""
        subtitle = Text(subtitle_text, font_size=36, color=self.color_palette["text"])
        return subtitle
        
    def create_matrix_from_array(self, arr, color_map=True, cell_size=0.5):
        """Create a matrix visualization from a numpy array.
        
        Args:
            arr: The array to visualize.
            color_map: Whether to color map the values.
            cell_size: The size of each cell.
        """
        n_rows, n_cols = arr.shape
        grid = VGroup()
        
        for i in range(n_rows):
            for j in range(n_cols):
                value = arr[i, j]
                cell = Square(side_length=cell_size)
                cell.set_stroke(WHITE, 1)
                
                if color_map:
                    # Map the value to a color (assuming values are normalized between 0 and 1)
                    alpha = (value - arr.min()) / (arr.max() - arr.min()) if arr.max() != arr.min() else 0
                    cell.set_fill(color=interpolate_color(BLACK, WHITE, alpha), opacity=1)
                else:
                    cell.set_fill(WHITE, opacity=value)
                
                # Position the cell
                cell.move_to([j * cell_size - (n_cols - 1) * cell_size / 2, 
                             -i * cell_size + (n_rows - 1) * cell_size / 2, 0])
                
                # Add a text label if the grid is not too large
                if max(n_rows, n_cols) <= 10:
                    label = Text(f"{value:.1f}", font_size=min(16, cell_size*20))
                    label.move_to(cell)
                    grid.add(VGroup(cell, label))
                else:
                    grid.add(cell)
        
        return grid
    
    def create_conv_kernel(self, kernel_values, color=BLUE):
        """Create a visualization of a convolution kernel."""
        kernel_array = np.array(kernel_values)
        n_rows, n_cols = kernel_array.shape
        grid = VGroup()
        
        # Normalize the kernel values for color mapping
        if np.max(np.abs(kernel_array)) > 0:
            normalized = kernel_array / np.max(np.abs(kernel_array))
        else:
            normalized = kernel_array
            
        for i in range(n_rows):
            for j in range(n_cols):
                value = kernel_array[i, j]
                normalized_value = normalized[i, j]
                
                # Create cell
                cell = Square(side_length=0.5)
                cell.set_stroke(WHITE, 1)
                
                # Color based on value (positive: blue, negative: red)
                if value >= 0:
                    cell.set_fill(BLUE, opacity=abs(normalized_value))
                else:
                    cell.set_fill(RED, opacity=abs(normalized_value))
                
                # Position
                cell.move_to([j * 0.5 - (n_cols - 1) * 0.5 / 2, 
                             -i * 0.5 + (n_rows - 1) * 0.5 / 2, 0])
                
                # Add label
                label = Text(f"{value:.1f}", font_size=16)
                label.move_to(cell)
                
                grid.add(VGroup(cell, label))
        
        # Add a surrounding rectangle to highlight the kernel
        rect = SurroundingRectangle(grid, color=YELLOW, buff=0.1)
        return VGroup(grid, rect) 