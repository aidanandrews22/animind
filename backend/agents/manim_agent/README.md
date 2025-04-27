# Manim Video Generation Agent

This agent uses Google's Agent Development Kit (ADK) to generate, debug, and run Manim animation code based on prompts and narration scripts.

## Features

- Generates Manim Python code based on detailed prompts and narration scripts
- Executes the code in a controlled environment
- Automatically fixes errors by rewriting or editing specific lines
- Aligns animations with provided narration scripts
- Utilizes the Gemini 2.5 Pro model for high-quality code generation

## Requirements

- Python 3.9+
- Google ADK (`pip install google-adk`)
- Manim animation library (`pip install manim`)
- Google Generative AI SDK (`pip install google-generativeai`)

## Usage

### Using ADK Commands

You can run the agent using the following ADK commands:

```bash
# Run the agent in interactive CLI mode
adk run manim

# Run the agent using the ADK Web UI
adk web
```

When using the ADK Web UI, select "manim" from the dropdown menu in the top-left corner.

#### Input Format

When interacting with the agent through ADK commands, you can provide your input in the following format:

```
Prompt: <description of the video to create>
Narration: <narration script for the video>
Output: <output directory path>
Python: <optional path for the Python file>
```

Example:
```
Prompt: Create a scene that demonstrates a circle morphing into a square.
Narration: First, we see a blue circle. Then, it gradually transforms into a red square.
Output: ./output/morphing_demo
```

### As a Python Module

```python
from manim.main import generate_manim_video

# Generate a video
result = generate_manim_video(
    prompt="Create a scene that demonstrates a circle morphing into a square.",
    narration_script="First, we see a blue circle. Then, it gradually transforms into a red square.",
    output_dir="./output/morphing_demo",
    python_file_path="./output/morphing_demo/scene.py"  # Optional
)

print(result)
```

### From Command Line

```bash
python -m manim.main \
  --prompt "Create a scene that demonstrates a circle morphing into a square." \
  --script narration.txt \
  --output-dir ./output/morphing_demo \
  --python-file ./output/morphing_demo/scene.py  # Optional
```

## How It Works

1. The agent receives a prompt and narration script
2. It generates initial Manim Python code and saves it to a file
3. It runs the code to check for errors
4. If there are errors, it fixes them by either:
   - Rewriting the entire file
   - Rewriting specific lines
   - Exiting (when no changes are needed)
5. It continues until the code executes successfully

## Configuration

The agent uses the Gemini 2.5 Pro model by default. To use your own API key, set the `GOOGLE_API_KEY` environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Future Enhancements

- RAG-based tool for retrieving Manim documentation and examples (coming soon)
- Support for audio generation to match narration scripts
- Enhanced error analysis and debugging capabilities 