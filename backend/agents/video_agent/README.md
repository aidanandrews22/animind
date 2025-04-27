# Video Agent

A Google ADK agent that generates animated educational videos with narration using Google Cloud Text-to-Speech and Manim animations.

## Overview

This agent follows a simple 3-step process to create complete videos:

1. **Generate Plan**: Creates a detailed scene-by-scene plan with titles, descriptions, animation instructions, and narration scripts.
2. **Generate Video/Audio**: For each scene, generates Manim animations and TTS audio separately.
3. **Stitch Together**: Combines all scenes into a final video with synchronized audio.

## Requirements

- Python 3.8+
- Google Cloud credentials (for Text-to-Speech API)
- FFmpeg (for video processing)
- Manim (for animations)
- robust_manim_agent (included)

## Installation

```bash
# Install required Python packages
pip install google-cloud-texttospeech google-adk ffmpeg-python

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## Usage

```python
from video_agent.agent import generate_video

# Generate a video about a topic
result = generate_video(
    prompt="Create an educational video explaining how photosynthesis works.",
    output_dir="output_folder"
)

# The result contains paths to all generated files
print(f"Final video: {result['final_output']}")
```

For a complete example, see `example_usage.py`.

## Animation Plan Format

The agent generates structured animation plans like:

```
SCENE 1: Introduction to Photosynthesis
Description: Overview of the process and its importance.
Animation Plan: 
- Start with title "Photosynthesis" centered on screen
- Zoom out to show a plant with sunlight rays
- Use arrows to show inputs (sunlight, water, CO2) and outputs (glucose, oxygen)

Narration: 
Welcome to our exploration of photosynthesis, the remarkable process that powers plant life on Earth. Photosynthesis converts sunlight, water, and carbon dioxide into glucose and oxygen, providing energy for plants and oxygen for animals.
```

## Technical Implementation

- Uses Google ADK's agent framework for a robust pipeline
- Implements LLM-based agents for each step of the process
- Leverages robust_manim_agent for reliable animation generation
- Uses Google Cloud TTS for high-quality narration
- Combines everything with FFmpeg for the final output 