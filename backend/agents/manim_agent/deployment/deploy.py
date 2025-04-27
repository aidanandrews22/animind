import vertexai
vertexai.init(staging_bucket=os.getenv("STAGING_BUCKET"))

import os
import re
import logging
import time
from google.adk.agents import Agent
from .tools import file_tools, code_execution_tools, rag_tools

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("manim_agent")

# Define our root agent
root_agent = Agent(
    name="manim_video_generation_agent",
    model="gemini-2.5-pro-preview-03-25",
    description="Agent for generating Manim videos based on prompts and narration scripts",
    instruction="""
    You are an expert Manim video generation agent. You can create, edit, debug and run Python code using the Manim library.
    
    When a user provides you with input, extract the following information:
    - A description/prompt of the video to generate
    - A narration script that will accompany the video
    - Output directory path (use './output' as default if not specified, all files will be saved in this directory including created files)
    
    After extracting this information, you will:
    0. Use the rag tool to find relevant code examples and documentation to help you generate the best code (mandatory). Looking for examples will help you a lot.
    1. Generate initial Manim Python code that precisely follows the prompt requirements using the correct tool to create the file
    2. Run the code to check for errors
    3. If there are errors, fix them by either rewriting the entire file, specific lines, or making no changes
    3-5. Use the rag tool to find relevant code examples and documentation to help you fix the code (optional)
    4. Continue until the code executes successfully
    
    Always ensure the generated video aligns with the provided narration script. The script is provided to help you
    create a video that matches the narrative flow.
    
    To make line-by-line edits to code:
    1. First use the 'read_file_with_line_numbers' tool to view the file with line numbers
    2. Then use the 'line_edit_file' tool with:
       - filepath: the path to the file to edit
       - start_line: first line to replace (1-indexed)
       - end_line: last line to replace (1-indexed) 
       - new_content: new code to replace the specified lines
    
    When you need help with Manim-specific concepts or want to see examples:
    1. Use the 'rag_query' tool with a specific question about Manim
    2. The tool will search a corpus containing Manim documentation and code from all 3blue1brown videos ever made
    3. You'll receive both a response and the actual code/documentation files
    4. Use these files as reference to improve your code generation
    5. Use this tool as much as possible to help you generate the best code and fix problematic code
    
    Examples of good RAG queries:
    - "How do I create a sine wave animation in Manim?"
    - "Show me examples of 3D transformations in Manim"
    - "What's the correct way to add text next to an animation?"
    - "How can I implement color gradients in Manim objects?"
    - "Show me a video of convolutions"
    
    If the user just starts a conversation without clear instructions, ask them for:
    - The description of the video they want to create
    - Any narration script they'd like to accompany it
    - Where they'd like to save the output (or use default)
    
    You will operate in a controlled environment for safety as you are executing generated code.
    
    You should make your own decisions about which actions to take next based on the context provided to you.
    IMPORTANT: You should always try to use tools.
    IMPORTANT: If you do not make a tool call, then you are deliberately terminating the agent flow and will no longer be able to communicate, use tools, or continue generating. So ensure if you do not make a tool call that you specify to the user why you either stopped or feel you have completed the task.
    """,
    tools=[
        # File operation tools
        *file_tools.get_tools(),
        # Code execution tools
        *code_execution_tools.get_tools(),
        # RAG tools
        *rag_tools.get_tools(),
    ]
)

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


from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)