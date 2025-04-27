"""
Example usage of the video_agent.

This script demonstrates how to generate animated educational
videos with narration using the video_agent.
"""
import os
import logging
from dotenv import load_dotenv
from agent import generate_video

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("video_agent_example")

# Load environment variables
load_dotenv()

# Ensure required environment variables are set
required_envs = [
    "GOOGLE_APPLICATION_CREDENTIALS"  # Required for Google Cloud TTS
]

for env in required_envs:
    if not os.environ.get(env):
        logger.warning(f"{env} environment variable is not set! Functionality may be limited.")

def main():
    """Run the example."""
    # Example prompt
    prompt = """
    Create an educational video explaining how photosynthesis works.
    Focus on the process of converting sunlight, water, and carbon dioxide into glucose and oxygen.
    Include visuals of a plant cell, chloroplasts, and the chemical reactions involved.
    """
    
    logger.info("Generating animated video for prompt: %s", prompt)
    
    # Generate the video
    output_dir = "example_output"
    result = generate_video(prompt, output_dir=output_dir)
    
    logger.info("Video generation complete!")
    logger.info("Animation plan length: %d characters", len(result["animation_plan"]))
    logger.info("Final video path: %s", result["final_output"])
    
    # Save the animation plan to a file
    plan_path = os.path.join(output_dir, "animation_plan.txt")
    with open(plan_path, "w") as f:
        f.write(result["animation_plan"])
    
    logger.info("Animation plan saved to: %s", plan_path)

if __name__ == "__main__":
    main() 