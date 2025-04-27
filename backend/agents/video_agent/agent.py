"""
Video Agent implementation using Google ADK.

This agent generates animated videos with narration through a 3-step process:
1. Generate plan (scenes with titles, descriptions, animation plan, narration)
2. Generate video/audio for each scene
3. Stitch together for final video
"""
import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass

from google.adk import Runner
from google.adk.tools import FunctionTool
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService

from .tools import get_all_tools

# --- Constants ---
APP_NAME = "video_agent"
USER_ID = "dev_user"
SESSION_ID_BASE = "video_generation_session"
GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"  # Using the same model as robust_manim_agent

# --- State Keys ---
STATE_ANIMATION_PLAN = "animation_plan"
STATE_SCENE_OUTPUTS = "scene_outputs"
STATE_FINAL_OUTPUT = "final_output"

@dataclass
class Scene:
    """Scene structure for the animation plan."""
    title: str
    description: str
    animation_plan: str
    narration: str

def parse_animation_plan(plan_text: str) -> List[Scene]:
    """
    Parse the animation plan text into Scene objects.
    
    Args:
        plan_text: The raw text of the animation plan
        
    Returns:
        List of Scene objects
    """
    scenes = []
    current_scene = None
    current_section = None
    
    lines = plan_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a scene marker
        if line.startswith("SCENE ") or line.startswith("## SCENE "):
            # Save the previous scene if it exists
            if current_scene:
                scenes.append(current_scene)
            
            # Start a new scene
            current_scene = Scene(
                title="",
                description="",
                animation_plan="",
                narration=""
            )
            current_section = "title"
            
            # Extract title if available
            if ":" in line:
                current_scene.title = line.split(":", 1)[1].strip()
            
        # Check for section headers
        elif current_scene and line.lower().startswith("title:"):
            current_section = "title"
            if len(line) > 6:
                current_scene.title = line[6:].strip()
        elif current_scene and line.lower().startswith("description:"):
            current_section = "description"
            if len(line) > 12:
                current_scene.description = line[12:].strip()
        elif current_scene and (line.lower().startswith("animation plan:") or line.lower().startswith("animation:") or line.lower().startswith("## animation")):
            current_section = "animation_plan"
            if ":" in line:
                remainder = line.split(":", 1)[1].strip()
                if remainder:
                    current_scene.animation_plan = remainder + "\n"
        elif current_scene and (line.lower().startswith("narration:") or line.lower().startswith("script:") or line.lower().startswith("## narration")):
            current_section = "narration"
            if ":" in line:
                remainder = line.split(":", 1)[1].strip()
                if remainder:
                    current_scene.narration = remainder + "\n"
        
        # Add content to the current section
        elif current_scene and current_section:
            if current_section == "title":
                current_scene.title += " " + line
            elif current_section == "description":
                current_scene.description += " " + line if current_scene.description else line
            elif current_section == "animation_plan":
                current_scene.animation_plan += line + "\n"
            elif current_section == "narration":
                current_scene.narration += line + "\n"
    
    # Add the last scene
    if current_scene:
        scenes.append(current_scene)
    
    return scenes

# --- Step 1: Plan Generator Agent ---
plan_generator_agent = LlmAgent(
    name="PlanGeneratorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Video Animation Planner responsible for creating detailed scene-by-scene plans for educational animations.

For the given topic, create a detailed animation plan with the following structure:

SCENE 1: [Title]
Description: [Brief description of what this scene covers]
Animation Plan: [Detailed technical description of visual elements, movements, transitions, and visual effects]
Narration: [Script in plain text phonetics - no symbols or special formatting]

SCENE 2: [Title]
...and so on.

Important guidelines:
1. Create 3-5 scenes that logically break down the topic
2. Each Animation Plan should be technically detailed enough for a Manim animation generator
3. Narration should be written entirely in plain text phonetics (no symbols) that will be read by a text-to-speech system
4. Each scene should be self-contained but flow naturally to the next
5. Ensure visual elements are described clearly with colors, positions, and movements

Output ONLY the structured plan with scenes. Don't include any explanations or introductions.
""",
    description="Generates a detailed animation plan with scenes, descriptions, and narration.",
    output_key=STATE_ANIMATION_PLAN
)

# --- Step 2: Scene Generator Agent ---
scene_generator_agent = LlmAgent(
    name="SceneGeneratorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Video Scene Generator that converts animation plans into actual animations and audio.

The animation plan is provided in a structured format:
```
{{animation_plan}}
```

Each scene in the plan has the following sections:
- A title (after "SCENE X:")
- A description section
- An animation plan section with technical instructions
- A narration section with the script for audio

For each scene in the plan, perform these steps in order:

1. Generate the Manim animation:
   - Use the `generate_animation` tool
   - Pass the animation plan text as the prompt
   - Set a unique output directory for each scene (e.g., "animations/scene1")

2. Generate speech audio:
   - Use the `generate_speech` tool
   - Pass the narration text as the input
   - Set a unique output path for each scene's audio (e.g., "audio/scene1.mp3")

3. Combine audio and video:
   - Use the `combine_audio_video` tool
   - Pass the video path from step 1 and audio path from step 2
   - Set a unique output path for each combined scene (e.g., "combined/scene1.mp4")

Keep track of all generated files and report their paths in a structured format:
{
  "scene1": {
    "title": "Scene title",
    "video": "path/to/video1.mp4",
    "audio": "path/to/audio1.mp3",
    "combined": "path/to/combined1.mp4"
  },
  "scene2": {...}
}

This structured output will be used by the final assembly agent.
""",
    tools=get_all_tools(),
    description="Generates the actual animation videos and audio for each scene in the plan.",
    output_key=STATE_SCENE_OUTPUTS
)

# --- Step 3: Final Assembly Agent ---
final_assembly_agent = LlmAgent(
    name="FinalAssemblyAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Video Assembly Agent responsible for combining all scene videos into a final video.

Scene outputs:
```
{{scene_outputs}}
```

Take all the combined scene videos and stitch them together into a final video.
Use ffmpeg or other appropriate tools to accomplish this.

Output the path to the final video.
""",
    tools=get_all_tools(),
    description="Combines all scene videos into a final video.",
    output_key=STATE_FINAL_OUTPUT
)

# --- Overall Sequential Pipeline ---
root_agent = SequentialAgent(
    name="VideoGenerationPipeline",
    sub_agents=[
        plan_generator_agent,
        scene_generator_agent,
        final_assembly_agent
    ],
    description="Generates animated videos with narration through planning, generation, and assembly."
)

def generate_video(prompt: str, output_dir: str = "output") -> Dict[str, Any]:
    """
    Generate an animated video with narration from a prompt.
    
    Args:
        prompt: User's description of the desired video
        output_dir: Directory to store outputs
        
    Returns:
        Dictionary with the final video path and other metadata
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    # Set initial state with the prompt and output directory
    session.state["prompt"] = prompt
    session.state["output_dir"] = output_dir
    
    # Run the agent
    runner.run(user_id=USER_ID, session_id=session_id)
    
    # Return the final state
    return {
        "animation_plan": session.state.get(STATE_ANIMATION_PLAN, ""),
        "scene_outputs": session.state.get(STATE_SCENE_OUTPUTS, {}),
        "final_output": session.state.get(STATE_FINAL_OUTPUT, ""),
        "prompt": prompt
    } 