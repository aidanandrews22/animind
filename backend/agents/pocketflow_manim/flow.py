from minLLM.minllm import Flow
from nodes import (
    InitializeAgent, 
    PlanScene, 
    ResearchStep, 
    CreateCode, 
    ExecuteCode, 
    FixErrors,
    StitchScenes
)

def create_manim_agent_flow():
    """
    Create and connect nodes to form the complete Manim animation agent flow.
    
    The flow works like this:
    1. Initialize agent parses the prompt and plans scenes
    2. For each scene:
       a. Plan the scene details
       b. Optionally do research
       c. Create Manim code
       d. Execute code
       e. Fix any errors
    3. Once all scenes are complete, stitch them together
    
    Returns:
        Flow: A complete Manim animation agent flow
    """
    # Create instances of each node
    initialize = InitializeAgent()
    plan_scene = PlanScene()
    research = ResearchStep()
    create_code = CreateCode()
    execute_code = ExecuteCode()
    fix_errors = FixErrors()
    stitch_scenes = StitchScenes()
    
    # Connect the nodes
    initialize - "plan_first_scene" >> plan_scene
    
    # Research path
    plan_scene - "research" >> research
    research - "create_code" >> create_code
    
    # Direct to code path
    plan_scene - "create_code" >> create_code
    
    # Code execution and error fixing path
    create_code - "execute_code" >> execute_code
    execute_code - "fix_errors" >> fix_errors
    fix_errors - "execute_code" >> execute_code
    
    # Next scene path
    execute_code - "plan_next_scene" >> plan_scene
    
    # Final stitching path
    execute_code - "stitch_scenes" >> stitch_scenes
    plan_scene - "stitch_scenes" >> stitch_scenes
    
    # Create the flow
    return Flow(start=initialize) 