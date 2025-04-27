"""
Example usage of the robust_manim_agent.

This script demonstrates how to generate Manim animations
using the robust_manim_agent with a simple prompt.
"""
import os
import logging
from dotenv import load_dotenv
from agent import generate_manim_animation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("robust_manim_example")

# Load environment variables
load_dotenv()

# Ensure the MANIM_RAG_CORPUS environment variable is set
if not os.environ.get("MANIM_RAG_CORPUS"):
    logger.warning("MANIM_RAG_CORPUS environment variable is not set! RAG functionality will not work properly.")
    logger.warning("Please set MANIM_RAG_CORPUS to your Manim RAG corpus ID.")

def main():
    """Run the example."""
    # Simple prompt for testing
    prompt = """
    Create an animation that demonstrates the concept of a binary search algorithm.
    Show how it efficiently finds a value in a sorted array by dividing the search interval in half.
    Use distinct colors to highlight the current search range and target value.
    """
    
    logger.info("Generating Manim animation for prompt: %s", prompt)
    
    # Generate the animation
    result = generate_manim_animation(prompt)
    
    logger.info("Animation generation complete!")
    logger.info("Final code length: %d characters", len(result["code"]))
    
    # Output the final code to a separate file for reference
    output_file = "generated_manim_code.py"
    with open(output_file, "w") as f:
        f.write(result["code"])
    
    logger.info("Final code saved to: %s", output_file)

if __name__ == "__main__":
    main() 