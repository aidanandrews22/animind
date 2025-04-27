import os
import re
import logging
import time
import json
from google.adk.agents import Agent, RunConfig
from google.adk.planners import PlanReActPlanner
from google.genai import types
from .tools import file_tools, rag_tools

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("manim_agent")

# Create PlanReActPlanner - this doesn't accept parameters in the current API
optimized_planner = PlanReActPlanner()

# Create run configuration to limit the number of LLM calls
run_config = RunConfig(
    # Limit total number of LLM calls for a given run (similar to max_steps)
    max_llm_calls=25
)

# Helper function to fix common malformed function calls in text responses
def fix_malformed_function_calls(response):
    """
    Attempts to fix malformed function calls in a response by extracting valid JSON
    from text parts and converting them into proper function call parts.
    
    Args:
        response: The agent response object
        
    Returns:
        True if a function call was fixed, False otherwise
    """
    # Only process if there are no valid function calls already
    if response.get_function_calls():
        return False
    
    fixed = False
    action_tag = "/*ACTION*/"
    
    # Look for text parts that might contain malformed function calls
    for part in response.parts:
        if not part.text or not action_tag in part.text:
            continue
            
        # Extract the text after the ACTION tag
        action_split = part.text.split(action_tag)
        if len(action_split) < 2:
            continue
            
        potential_json_text = action_split[1].strip()
        
        # If there's a stray "*/" right at the beginning, remove it
        if potential_json_text.startswith("*/"):
            potential_json_text = potential_json_text[2:].strip()
        
        # Try to extract a JSON object
        try:
            # Find the first { and the matching closing }
            start_idx = potential_json_text.find("{")
            if start_idx == -1:
                continue
                
            # Basic JSON extraction - this could be improved with a proper JSON parser
            json_str = potential_json_text[start_idx:]
            
            # Try to parse it
            function_data = json.loads(json_str)
            
            if "name" in function_data and isinstance(function_data["name"], str):
                # Create a new function call part
                logger.info(f"Fixed malformed function call: {function_data['name']}")
                
                # Create a new function call
                func_call = types.FunctionCall(
                    name=function_data["name"],
                    args=function_data.get("args", {})
                )
                
                # Add the function call to the response
                part.function_call = func_call
                fixed = True
                break
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to fix malformed function call: {str(e)}")
            continue
    
    return fixed


# Define our root agent
root_agent = Agent(
    name="manim_video_generation_agent",
    model="gemini-2.5-pro-preview-03-25",
    description="Agent specialized in generating visually appealing, conceptually accurate Manim videos from user prompts and narration scripts.",
    instruction="""
    - You'll work with only one Python file at a time so no need to specify the filepath.

    ### Workflow Steps (Always follow in order):

    **Step 1: Comprehensive Research (Mandatory)**
    - Use the `rag_query` tool to retrieve relevant Manim documentation and code examples from the corpus (including 3blue1brown's videos).
    - Example queries:
        - "Examples of creating visual metaphors for mathematical concepts in Manim?"
        - "How to spatially separate objects clearly in Manim animations?"
        - "Best practices for matching visuals to a narration script in Manim?"

    **Step 2: Generate Robust Manim Code**
    - Precisely follow user prompts and integrate intentional visual decisions (positioning, colors, animations).
    - Clearly document the code with detailed comments explicitly explaining each visual decision (e.g., why a particular position, color, animation style was chosen to reinforce the narrative).
    - Use the `create_file` tool to create the Python file, which will automatically be set as the active file.

    **Step 3: Execute and Debug the Code**
    - When you create or edit the Python file, it will automatically run with Manim. You'll get the execution results directly in the tool response.
    - If errors occur:
        - First use `rag_query` tool again to find solutions from documentation or relevant examples.
        - Read the file with `read_file` (no parameters needed) to see line numbers.
        - Fix errors with `edit_file` specifying start_line, end_line, and the new code.
    - Continue editing until the Python code runs successfully.

    **Step 4: Validate Alignment with Narration**
    - Double-check that visuals clearly match the provided narration script.
    - Ensure the animation pacing, scene transitions, and object placements directly enhance narrative comprehension.

    ### Tool Usage Guidelines:
    - Always utilize provided tools extensively.
    - Every step **must** end with a function call unless the entire workflow is complete.
    - Prioritize safety and controlled execution.

    ### Intentional Design Requirements:
    - **Spatial Clarity:** Intentionally position all elements to avoid overlap unless explicitly required by the narrative.
    - **Color and Animation Choices:** Deliberately choose colors and animation styles that reinforce the conceptual understanding.
    - **Documentation:** Every visual decision (e.g., location, transitions, colors) must be justified clearly in the code comments to ensure intentionality.

    ### User Interaction:
    - If initial instructions are vague, proactively request clarification for:
        1. The conceptual visual description of the desired video.
        2. The narration script (if available).
        3. Preferred output directory (defaulting to './output' if unspecified).

    Your goal is to consistently deliver high-quality, visually appealing, and robust Manim animations explicitly tailored to user requests, enhancing viewer comprehension through deliberate, justified visual decisions.

    """,
    # Configure content generation settings
    generate_content_config=types.GenerateContentConfig(
        # Set temperature to control randomness (lower = more deterministic)
        temperature=0.2
    ),
    tools=[
        # File operation tools
        *file_tools.get_tools(),
        # RAG tools
        *rag_tools.get_tools(),
    ],
    planner=optimized_planner
)


# Add validation wrapper for the agent's run function
async def run_agent_with_validation(agent, event):
    """
    Wrapper for running the agent with validation to ensure proper function call execution.
    Rejects responses without function calls and retries with corrective messaging.
    Always enforces function calls regardless of whether the response is marked as final.
    """
    from google.adk.runners import Runner
    
    # Create runner and context for agent execution
    runner = Runner(agent)
    ctx = await runner.create_context()
    
    # Add initial user message
    ctx.add_user_message(event.get('user_input', ''))
    
    # Main execution loop with validation
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        
        # Run the agent step
        response = await runner.run_async(ctx, run_config=run_config)
        
        # Try to fix any malformed function calls
        fixed = fix_malformed_function_calls(response)
        
        # If we fixed something or have valid function calls, break the loop
        if fixed or response.get_function_calls():
            logger.info(f"Valid function call detected after {attempts} attempts")
            break
            
        # Check if response lacks function calls
        if not response.get_function_calls():
            # Log the issue
            logger.warning(f"Response has no function calls (attempt {attempts}/{max_attempts})")
            
            # Add corrective system message with more explicit formatting guidance
            ctx.add_system_message(
                "Your last reply did not include a proper function call. "
                "Make sure to format your response with the ACTION block as follows:\n"
                "/*ACTION*/\n"
                "{\"name\": \"tool_name\", \"args\": {\"param\": \"value\"}}\n\n"
                "Do not add any characters before or after the JSON object. "
                "The JSON must appear exactly after the /*ACTION*/ tag."
            )
            # Continue loop to retry unless we've hit max attempts
            if attempts >= max_attempts:
                logger.error("Max attempts reached without a valid function call")
    
    return response


def parse_user_input(text):
    """Parse user input to extract prompt, narration script, and output dir."""
    # Default values
    prompt = ""
    narration_script = ""
    output_dir = "./output"
    python_file_path = None
    
    # Log the parsing operation
    logger.info("Parsing user input")
    
    # Try to extract prompt using patterns
    prompt_match = re.search(r'(?:prompt|description):\s*(.*?)(?:narration|script|output|$)', 
                             text, re.IGNORECASE | re.DOTALL)
    if prompt_match:
        prompt = prompt_match.group(1).strip()
    else:
        # If no labeled prompt, use the entire text as prompt
        prompt = text.strip()
    
    # Try to extract narration script
    script_match = re.search(r'(?:narration|script):\s*(.*?)(?:output|$)', 
                            text, re.IGNORECASE | re.DOTALL)
    if script_match:
        narration_script = script_match.group(1).strip()
    
    # Try to extract output directory
    output_match = re.search(r'output(?:\s+dir|\s+directory)?:\s*(.*?)(?:python|$)', 
                            text, re.IGNORECASE | re.DOTALL)
    if output_match:
        output_dir = output_match.group(1).strip()
    
    # Try to extract python file path
    python_match = re.search(r'python(?:\s+file)?(?:\s+path)?:\s*(.*?)$', 
                           text, re.IGNORECASE | re.DOTALL)
    if python_match:
        python_file_path = python_match.group(1).strip()
    
    logger.info(f"Extracted prompt length: {len(prompt)}, output_dir: {output_dir}")
    
    return {
        "prompt": prompt,
        "narration_script": narration_script,
        "output_dir": output_dir,
        "python_file_path": python_file_path
    } 
