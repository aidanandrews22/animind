"""
Robust Manim Agent implementation using Google ADK with a loop-based approach.

This agent focuses on generating high-quality Manim animations through an iterative
improvement loop that continues until the code is working correctly.
"""
import os
from typing import Dict, Any
from google.adk.tools import FunctionTool
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from .tools import get_all_tools

# --- Constants ---
APP_NAME = "robust_manim_agent"
USER_ID = "dev_user"
SESSION_ID_BASE = "manim_generation_session"
GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"  # Using a high-capability model

# --- State Keys ---
STATE_CURRENT_CODE = "current_code"
STATE_EXECUTION_RESULT = "execution_result"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "The Manim animation is working correctly."

# --- Tool Definition ---
def exit_loop():
    """Call this function ONLY when the code is working correctly, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered")
    # Create a result with escalate flag that the agent can interpret
    return {"escalate": True}

# Create the exit loop tool
exit_loop_tool = FunctionTool(func=exit_loop)

# --- Agent Definitions ---

# STEP 1: Initial Generator Agent (Runs ONCE at the beginning)
initial_generator_agent = LlmAgent(
    name="InitialGeneratorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Manim Animation Generator tasked with creating the initial Manim Python code.
    
    Based on the user's prompt, create a Manim animation that:
    1. Accurately represents the concept described in the prompt
    2. Uses appropriate colors, positioning, and animations
    3. Follows best practices for Manim code organization
    4. Includes helpful comments explaining your visual choices
    
    Output ONLY the Python code for the Manim animation. Do not include any explanations or introductions.
    The code should be complete and ready to run with the Manim library.
    """,
    description="Generates the initial Manim code based on the user's prompt.",
    output_key=STATE_CURRENT_CODE
)

# STEP 2a: Execution Agent (Inside the Refinement Loop)
execution_agent = LlmAgent(
    name="ExecutionAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Manim Code Executor responsible for setting up and running Manim code.

    Your current Manim code is:
    ```python
    {{current_code}}
    ```

    Execute the following steps:
    1. Create a Python file with this code using the create_file tool. Use a suitable filename (e.g., 'animation.py').
    2. The file_tools will automatically execute the code and include the execution results in its response.
    3. Return the complete tool response, especially the execution_result section.

    Note: You DO NOT need to call the run_manim_code tool separately as execution happens automatically.
    
    Output ONLY the execution results from the create_file tool response. Do not add explanations.
    """,
    description="Creates a file with the current code, which triggers automatic execution, and outputs the results.",
    tools=get_all_tools(),
    output_key=STATE_EXECUTION_RESULT
)

# STEP 2b: Critic Agent (Inside the Refinement Loop)
critic_agent = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    instruction=f"""You are a Manim Code Critic reviewing the execution results of a Manim animation.
    
    Current Manim Code:
    ```python
    {{{{current_code}}}}
    ```
    
    Execution Results:
    ```
    {{{{execution_result}}}}
    ```
    
    Analyze the execution results:
    
    IF the execution_result shows successful execution (contains "status": "success" in the execution_result section):
    Respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else.
    
    ELSE IF there were errors or issues:
    Provide specific, actionable feedback on what needs to be fixed. Be precise about:
    - Line numbers with errors
    - What specifically is wrong
    - How to fix the issues
    
    Output ONLY your critique OR the exact completion phrase. No introductions or explanations.
    """,
    description="Reviews the execution results, providing critique if there are errors, otherwise signals completion.",
    output_key=STATE_CRITICISM
)

# STEP 2c: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    instruction=f"""You are a Manim Code Refiner responsible for improving code based on feedback OR exiting the process.
    
    Current Manim Code:
    ```python
    {{{{current_code}}}}
    ```
    
    Critique/Suggestions:
    ```
    {{{{criticism}}}}
    ```
    
    IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    
    ELSE (the critique contains actionable feedback):
    Improve the code by applying the suggestions. Output ONLY the complete, improved code.
    
    For improvements:
    1. Use the RAG query tool if needed to research Manim solutions
    2. Fix all identified issues
    3. Keep the original intent and structure of the animation
    4. Ensure the code is complete and runnable
    
    Either output the complete improved code OR call the exit_loop function.
    """,
    description="Refines the code based on critique, or calls exit_loop if execution was successful.",
    tools=[exit_loop_tool, *get_all_tools()],
    output_key=STATE_CURRENT_CODE
)

# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order: 1. Execute Code, 2. Critique Results, 3. Refine/Exit
    sub_agents=[
        execution_agent,
        critic_agent,
        refiner_agent,
    ],
    max_iterations=5  # Limit loops to avoid getting stuck
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="RobustManimPipeline",
    sub_agents=[
        initial_generator_agent,  # First generate initial code
        refinement_loop           # Then run the execute/critique/refine loop
    ],
    description="Generates Manim animations and iteratively improves them until they work correctly."
)

# Helper function to run the agent with a user prompt
def generate_manim_animation(prompt: str) -> Dict[str, Any]:
    """Generate a Manim animation from a user prompt.
    
    Args:
        prompt: User's description of the desired animation
        
    Returns:
        Dictionary with the final code and execution results
    """
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    
    # Create session service and session
    session_service = InMemorySessionService()
    session_id = f"{SESSION_ID_BASE}_{hash(prompt)}"
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    
    
    # Create runner and run the agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Run the agent
    runner.run(user_id=USER_ID, session_id=session_id, new_message={"text": prompt})
    
    # Return the final state
    return {
        "code": session.state.get(STATE_CURRENT_CODE, ""),
        "execution_result": session.state.get(STATE_EXECUTION_RESULT, ""),
        "iterations": session.state.get("iterations", 0)
    } 