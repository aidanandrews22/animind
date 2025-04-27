import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("dotenv not installed. Environment variables must be set manually.")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..agent import root_agent

class ManimVideoGenerator:
    """Manim video generation agent that can create, debug, and run Manim code."""
    
    def __init__(self):
        """Initialize the Manim video generator agent with runner and session service."""
        # Setup session service for maintaining state
        self.session_service = InMemorySessionService()
        # Setup runner for executing the agent
        self.runner = Runner(
            agent=root_agent,
            session_service=self.session_service,
            app_name="manim-video-generator"
        )
    
    async def generate_video(
        self,
        prompt: str,
        narration_script: str,
        output_dir: str,
        python_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a Manim video based on the given prompt and narration script.
        
        Args:
            prompt: Detailed description of the video to generate
            narration_script: Script for narration to align the video with
            output_dir: Directory to save the generated video
            python_file_path: Optional path for the generated Python file
                              (default: output_dir/scene.py)
                              
        Returns:
            Dictionary with results of video generation process
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set default Python file path if not provided
        if python_file_path is None:
            python_file_path = os.path.join(output_dir, "scene.py")
        
        # Generate a unique user_id and session_id
        user_id = "manim-user"
        session_id = f"manim_video_gen_{os.path.basename(output_dir)}"
        
        # Create the session explicitly
        try:
            # Following the ADK docs, create a session before using it
            self.session_service.create_session(
                app_name="manim-video-generator",
                user_id=user_id,
                session_id=session_id
            )
            print(f"Session created: {session_id}")
        except Exception as e:
            print(f"Error creating session: {e}")
            return {
                "status": "error",
                "error": f"Error creating session: {e}",
                "output_directory": output_dir,
                "python_file": python_file_path
            }
        
        # Prepare the prompt text
        prompt_text = f"""Generate a Manim video based on the following prompt and narration script.

OUTPUT DIRECTORY: {output_dir}
PYTHON FILE PATH: {python_file_path}

PROMPT:
{prompt}

NARRATION SCRIPT:
{narration_script}

Please follow these steps:
1. Generate initial Manim Python code and save it to {python_file_path}
2. Run the code to check for errors
3. If there are errors, fix them
4. Continue until the code executes successfully

You have full autonomy to decide which actions to take next based on the context.
"""
        
        # Prepare initial prompt with all necessary context - use Content instead of dict
        initial_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)]
        )
        
        # Start the agent with the initial prompt
        # We'll collect the responses manually since we're using an async generator
        responses = []
        try:
            print(f"Running agent with user_id={user_id}, session_id={session_id}")
            async for response in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=initial_message
            ):
                responses.append(response)
                # Print response for debugging
                print(f"Got response: {type(response)}")
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_directory": output_dir,
                "python_file": python_file_path,
                "note": "If you see a PERMISSION_DENIED error about the Generative Language API, please enable it in your Google Cloud console: https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview"
            }
        
        # Return the result with all responses
        return {
            "status": "completed",
            "output_directory": output_dir,
            "python_file": python_file_path,
            "agent_responses": responses
        }

# Function for easier use in synchronous contexts
def generate_manim_video(
    prompt: str,
    narration_script: str,
    output_dir: str,
    python_file_path: Optional[str] = None
) -> Dict[str, Any]:
    """Synchronous wrapper for generating Manim videos."""
    generator = ManimVideoGenerator()
    return asyncio.run(
        generator.generate_video(
            prompt=prompt,
            narration_script=narration_script,
            output_dir=output_dir,
            python_file_path=python_file_path
        )
    )

if __name__ == "__main__":
    # Example usage when run directly
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Manim videos using AI")
    parser.add_argument("--prompt", required=True, help="Prompt describing the video to generate")
    parser.add_argument("--script", required=True, help="Narration script file path")
    parser.add_argument("--output-dir", required=True, help="Output directory for video")
    parser.add_argument("--python-file", help="Path for the generated Python file")
    
    args = parser.parse_args()
    
    # Read narration script from file
    with open(args.script, 'r') as f:
        narration_script = f.read()
    
    # Generate video
    result = generate_manim_video(
        prompt=args.prompt,
        narration_script=narration_script,
        output_dir=args.output_dir,
        python_file_path=args.python_file
    )
    
    print(json.dumps(result, indent=2)) 