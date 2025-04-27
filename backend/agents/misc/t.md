Note that the manim agent should be called exactly the same way that the rag agent is called in the manim agent. This way the agent can be used directly

We need to ensure it actually impliments the video and audio gen. The video generation comes from @manim_agent and audio from @kokoro_voiceover.py. Ensure both are correctly setup. Note that the manim agent is implemented using @google-adk 
docs:@google-adk 

The plan is to impliment this:
I'll create a comprehensive plan for implementing a video agent that utilizes the manim_agent and kokoro_voiceover for synchronized video and audio creation. Let me first explore the relevant components to understand how they work.

Read file: t.md
Now let's understand how the manim_agent works:

Read file: manim_agent/agent.py
Let me check the tools available for the manim agent:

Ran tool
Let's look at the kokoro_voiceover.py file to understand how to generate audio:

Read file: rag_extras/example/manim-video-agent/src/utils/kokoro_voiceover.py
Let me also look at the example usage of the RAG for the manim agent:

Read file: manim_agent/example_rag_usage.py
Now I need to understand how Google ADK works to build this agent:

Ran tool
Let me also understand the Scene structure used in kokoro_voiceover.py:

Search files...
Now I have a good understanding of how the manim_agent and kokoro_voiceover work. Let me search for information about how to build a Google ADK agent:

Ran tool
Let's look at the home automation agent example:

Read file: /Users/aidan/Documents/Code/Projects/animind/backend/agents/google-adk/tests/integration/fixture/home_automation_agent/agent.py
Based on my exploration, I now have a good understanding of how to implement a video agent that utilizes the manim_agent and kokoro_voiceover. Let me create a comprehensive plan for this implementation.

# Video Agent Implementation Plan

## Overview

The Video Agent will be a new agent that manages the entire process of creating videos with synchronized audio. It will utilize the manim_agent for video generation and kokoro_voiceover for audio generation. This agent will communicate with users, plan video content, generate narration scripts, and orchestrate the entire video creation process while maintaining a persistent session for reliable communication with the manim_agent.

## Key Components

1. **Video Agent (Main Agent)**
   - Primary interface for user interaction
   - Responsible for session management with manim_agent
   - Handles planning, narration, audio generation and video creation

2. **Tools**
   - Manim agent as a tool
   - Kokoro voiceover integration for audio generation
   - Video/narration planning
   - File management
   - Session management

3. **Session Management**
   - Maintain a persistent session ID with manim_agent
   - Handle potential premature completion from manim_agent

## Detailed Implementation Plan

### 1. Agent Structure

```
Root Video Agent
  |
  |-- Tools:
       |-- plan_video (generates video plan and narration script)
       |-- generate_audio (using kokoro_voiceover)
       |-- manim_agent_tool (interacts with manim_agent)
       |-- check_video_status (verifies completion)
       |-- combine_audio_video (synchronizes A/V)
       |-- file_management (saves narration, plan, script, outputs)
```

### 2. Data Structures

1. **Scene** (as defined in existing code):
   ```python
   class Scene(BaseModel):
       id: str
       title: str
       duration: float
       narration: str
       animation_plan: Dict[str, Any]
       original_query: str
       original_solution: str
       manim_code: Optional[str] = None
       audio_file: Optional[str] = None
       video_file: Optional[str] = None
   ```

2. **VideoProject**:
   ```python
   class VideoProject(BaseModel):
       id: str
       title: str
       description: str
       scenes: List[Scene]
       output_dir: str
       manim_session_id: str
       status: str  # planning, audio_generation, video_generation, complete
   ```

### 3. Tool Implementations

#### 3.1. Video Planning Tool
```python
def plan_video(topic: str, complexity: str = "medium", duration: str = "medium") -> dict:
    """
    Generate a detailed video plan with scenes and narration script.
    
    Args:
        topic: The subject of the video
        complexity: Level of detail (simple, medium, advanced)
        duration: Target length of video (short, medium, long)
        
    Returns:
        dict: Video plan with scenes and narration scripts
    """
    # Implementation will use LLM to generate plan with:
    # - Overall video title and description
    # - Scene breakdown
    # - Narration script for each scene
    # - Animation plan for each scene
    
    # Return structured plan as dictionary
```

#### 3.2. Audio Generation Tool
```python
def generate_audio_for_scenes(scenes: list[Scene], output_dir: Path) -> list[Scene]:
    """
    Generate audio for all scenes using Kokoro TTS.
    
    Implementation will use the existing kokoro_voiceover.py functionality
    """
```

#### 3.3. Manim Agent Tool
```python
def execute_manim_agent(query: str, narration: str, output_dir: str, session_id: str = None) -> dict:
    """
    Execute the manim agent to generate video based on query and narration.
    
    Args:
        query: Description of the video to generate
        narration: Narration script to accompany the video
        output_dir: Directory to save the output files
        session_id: Optional session ID for continued conversations
        
    Returns:
        dict: Status information and session ID
    """
    # Implementation will handle:
    # - Maintaining session with manim_agent
    # - Monitoring status until completion
    # - Retrying if needed
```

#### 3.4. Check Video Status Tool
```python
def check_video_status(session_id: str) -> dict:
    """
    Check if the manim agent has completed video generation.
    
    Args:
        session_id: The session ID to check
        
    Returns:
        dict: Status information including completion status
    """
    # Implementation will:
    # - Check if video generation is complete
    # - Return status and any error information
```

#### 3.5. Combine Audio/Video Tool
```python
def combine_audio_video(video_file: str, audio_file: str, output_file: str) -> str:
    """
    Combine the generated video with the audio file.
    
    Args:
        video_file: Path to video file
        audio_file: Path to audio file
        output_file: Path for the combined output
        
    Returns:
        str: Path to the combined video file
    """
    # Implementation will:
    # - Use ffmpeg or similar to combine audio and video
    # - Ensure synchronization
    # - Handle timing adjustments if needed
```

#### 3.6. File Management Tool
```python
def save_project_files(project: VideoProject) -> dict:
    """
    Save all project files to the output directory.
    
    Args:
        project: The VideoProject object with all data
        
    Returns:
        dict: Paths to all saved files
    """
    # Implementation will:
    # - Save narration scripts
    # - Save animation plans
    # - Save project metadata
    # - Create directory structure
```

### 4. Session Management Strategy

1. **Initialize Session**:
   - Create a unique session ID when starting a new video project
   - Store session ID in state using the ADK state management system

2. **Handle Incomplete Operations**:
   - Implement a polling mechanism to check manim_agent status
   - Detect when manim_agent returns 200 but is not actually complete
   - Re-engage the manim_agent with the same session ID to continue

3. **Error Recovery**:
   - Implement retry logic for manim_agent failures
   - Save intermediate results to allow resuming from failure points

### 5. Video Creation Workflow

1. **User Interaction**:
   - User describes the desired video
   - Agent clarifies requirements and gathers details

2. **Planning Phase**:
   - Generate overall video plan and narration script
   - Break down into scenes

3. **Audio Generation**:
   - Generate audio for each scene using Kokoro TTS
   - Save audio files to output directory

4. **Video Generation**:
   - For each scene:
     - Call manim_agent with scene description and narration
     - Monitor until complete
     - Handle potential premature completion
     - Save generated video

5. **Synchronization**:
   - Combine audio and video for each scene
   - Merge scenes into final video if needed

6. **Completion**:
   - Present final video to user
   - Save all project files for future reference

## Agent Instructions (Prompt)

```
You are a Video Creation Agent that helps users create educational videos using Manim animations with narration. You manage the entire process from planning to final video creation.

Your capabilities:
1. Generate detailed video plans with narration scripts based on user requests
2. Create audio narration using Kokoro TTS
3. Generate mathematical animations using the Manim Agent
4. Synchronize audio and video into a final product

Process:
1. When a user provides a request, clarify requirements if needed (topic, complexity, duration)
2. Use the plan_video tool to create a detailed video plan with scenes and narration
3. Generate audio for the narration using generate_audio_for_scenes
4. For each scene, use the manim_agent_tool to create animations
   - IMPORTANT: The manim_agent may return success (200) before actually completing
   - Always use check_video_status to verify completion
   - If incomplete, continue the session with the same session_id
5. Combine audio and video using combine_audio_video
6. Save all project files using save_project_files

Remember to:
- Maintain a persistent session with the manim_agent using session_id
- Save all intermediate files (narration scripts, plans, audio) to the output directory
- Provide clear updates to the user throughout the process
- Ensure audio and video are properly synchronized
```

## Required Functionality for ADK Implementation

1. **Import and Setup**:
   ```python
   from google.adk.agents import Agent
   from google.adk.tools import FunctionTool
   
   video_agent = Agent(
       name="video_creation_agent",
       model="gemini-2.5-pro-preview-03-25",  # Use appropriate model
       description="Agent for creating educational videos with Manim animations and narration",
       instruction="...",  # Detailed instructions as outlined above
       tools=[
           FunctionTool(func=plan_video),
           FunctionTool(func=generate_audio_for_scenes),
           FunctionTool(func=execute_manim_agent),
           FunctionTool(func=check_video_status),
           FunctionTool(func=combine_audio_video),
           FunctionTool(func=save_project_files)
       ]
   )
   ```

2. **Custom Session Management**:
   - Implement session state tracking using ADK's state management system
   - Store manim_agent session ID and status in state

3. **Tool Context Utilization**:
   - Use `tool_context` parameter to access and update session state
   - Track progress in state for resilience

## Conclusion

This video agent will provide a seamless end-to-end experience for creating educational videos with mathematical animations and synchronized narration. By effectively managing the communication with the manim_agent and integrating the kokoro_voiceover system, it will produce high-quality videos that precisely match the user's requirements.

The implementation focuses on:
1. Robust session management to handle the manim_agent's behavior
2. Proper planning and structuring before generation
3. Synchronized audio and video creation
4. Comprehensive file management
5. Clear user communication throughout the process

This design ensures the agent can reliably create complex educational videos with proper narration timing, even considering the challenges of working with the manim_agent's completion status behavior.
