import logging
import os
import sys
import dotenv
from flow import create_manim_agent_flow

# Load environment variables from .env file
dotenv.load_dotenv()

def setup_logging(log_level, output_dir):
    """Configure logging for the agent."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(output_dir, "agent.log"), mode='w')
        ]
    )
    
    # Set all loggers to the specified level to capture everything
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Create a specialized logger for manim_agent
    logger = logging.getLogger("manim_agent")
    logger.setLevel(getattr(logging, log_level))
    
    # Add a custom handler to also log errors to a separate file
    error_handler = logging.FileHandler(os.path.join(output_dir, "agent_errors.log"), mode='w')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(error_handler)
    
    return logger

def main():
    """Run the Manim animation agent."""
    # Check for required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("WARNING: GEMINI_API_KEY environment variable is not set")
        print("OpenAI-compatible endpoint with Google Gemini requires an API key")
        return 1
    
    # Simple argument parsing
    prompt = "Create an animation showing a bouncing ball with physics" 
    output_dir = "output"
    file_name = "animation"
    log_level = "DEBUG"  # Set default to DEBUG to capture all messages
    
    # Override defaults with command-line args if provided
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--prompt" and i+1 < len(args):
            prompt = args[i+1]
        elif arg == "--output-dir" and i+1 < len(args):
            output_dir = args[i+1]
        elif arg == "--file-name" and i+1 < len(args):
            file_name = args[i+1]
        elif arg == "--log-level" and i+1 < len(args):
            log_level = args[i+1]
    
    # Setup logging
    logger = setup_logging(log_level, output_dir)
    logger.info(f"Starting Manim Agent with prompt: {prompt}")
    
    # Create the agent flow
    agent_flow = create_manim_agent_flow()
    
    # Initialize shared state
    shared = {
        "prompt": prompt,
        "output_directory": output_dir,
        "file_name": file_name
    }
    
    # Execute the flow
    try:
        logger.info("Running animation generation flow")
        agent_flow.run(shared)
        
        # Log the final result
        if "final_result" in shared:
            logger.info(f"Final result: {shared['final_result']}")
            print(f"\nAnimation generation complete!")
            print(f"Scenes created: {shared['final_result']['scene_count']}")
            print(f"Stitching script: {shared['final_result']['stitch_file']}")
        else:
            logger.warning("Flow completed but no final result was found")
        
        return 0
    except Exception as e:
        # Log the exception with traceback
        logger.exception(f"Critical error during animation generation: {str(e)}")
        print(f"\nError: {str(e)}")
        
        # Check if we have any partial results
        if "current_scene_index" in shared:
            print(f"Failed at scene: {shared.get('current_scene_index', 0) + 1}")
        if "current_scene_file" in shared:
            print(f"Last file being processed: {shared.get('current_scene_file', '')}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 