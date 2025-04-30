import os
import logging
from minLLM.minllm import Node
import yaml
from services.llm import LLM, LLMParams
import uuid
import subprocess
import glob

# Import our tools
from tools.rag_tools import rag_query
from tools.file_tools import create_file, read_file, edit_file
from tools.code_execution_tools import run_python_linter, run_manim_code

# Setup logger
logger = logging.getLogger("manim_agent")

class InitializeAgent(Node):
    """Initialize the agent and parse the initial prompt."""
    
    def prep(self, shared):
        """Prepare the initial context."""
        return shared["prompt"]
        
    def exec(self, prompt):
        """Parse the initial prompt and plan the animation."""
        logger.info(f"Initializing agent with prompt: {prompt}")
        
        llm = LLM()
        params = LLMParams(
            prompt=f"""
### TASK
You are an AI expert in creating Manim animations. You'll help convert a text prompt into a beautiful animation.

### USER PROMPT
{prompt}

### INSTRUCTIONS
Analyze the prompt and determine what kind of animation to create. Plan out your approach step by step.
Return your response in YAML format:

```yaml
thinking: |
    <your step-by-step reasoning process analyzing the prompt>
approach: |
    <outline the overall structure of the animation>
scenes:
    - name: <scene_name_1>
      description: <brief description of scene 1>
    - name: <scene_name_2>
      description: <brief description of scene 2>
next_step: "plan_first_scene"
```
""",
            temperature=0.7
        )
        
        response = llm.call(params)
        
        # Extract YAML content
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        plan = yaml.safe_load(yaml_str)
        
        return plan
    
    def post(self, shared, prep_res, exec_res):
        """Save the plan to shared state."""
        # Store the plan in shared state
        shared["plan"] = exec_res
        shared["scenes"] = exec_res.get("scenes", [])
        shared["current_scene_index"] = 0
        shared["completed_scenes"] = []
        
        # Create a centralized media management system
        project_id = str(uuid.uuid4())
        base_output_dir = shared.get("output_directory", "output")
        project_dir = os.path.join(base_output_dir, project_id)
        
        # Create project directories
        os.makedirs(project_dir, exist_ok=True)
        
        # Create media directory
        media_dir = os.path.join(project_dir, "media")
        os.makedirs(media_dir, exist_ok=True)
        
        # Store paths in shared state
        shared["project_id"] = project_id
        shared["project_dir"] = project_dir
        shared["media_dir"] = media_dir
        shared["scene_files"] = []
        shared["scene_videos"] = []
        
        logger.info(f"Created animation project with ID: {project_id}")
        logger.info(f"Project directory: {project_dir}")
        logger.info(f"Media directory: {media_dir}")
        logger.info(f"Created animation plan with {len(shared['scenes'])} scenes")
        
        # Return the next action from the YAML
        return exec_res.get("next_step", "plan_first_scene")

class PlanScene(Node):
    """Plan a single scene of the animation."""
    
    def prep(self, shared):
        """Prepare the scene planning context."""
        scenes = shared.get("scenes", [])
        current_index = shared.get("current_scene_index", 0)
        
        if current_index >= len(scenes):
            logger.warning("No more scenes to plan")
            return None
        
        current_scene = scenes[current_index]
        original_prompt = shared.get("prompt", "")
        
        return {
            "scene": current_scene,
            "prompt": original_prompt,
            "scene_index": current_index,
            "total_scenes": len(scenes)
        }
        
    def exec(self, context):
        """Plan the details for the current scene."""
        if not context:
            return {"status": "complete", "message": "No more scenes to plan"}
            
        scene = context["scene"]
        prompt = context["prompt"]
        scene_index = context["scene_index"]
        
        logger.info(f"Planning scene {scene_index+1}: {scene['name']}")
        
        # Get information about Manim from RAG
        rag_result = rag_query(f"How to create a Manim animation for {scene['description']}?")
        
        llm = LLM()
        params = LLMParams(
            prompt=f"""
### TASK
Plan a detailed Manim animation scene.

### SCENE INFORMATION
Scene: {scene['name']}
Description: {scene['description']}
Overall animation prompt: {prompt}
Scene number: {scene_index+1} of {context['total_scenes']}

### RESEARCH INFORMATION
{rag_result.get('response', 'No information found.')}

### INSTRUCTIONS
Plan how to implement this scene with Manim. Be specific about the objects, transitions, and effects.
Return your response in YAML format:

```yaml
thinking: |
    <your detailed reasoning about how to implement this scene>
scene_plan: |
    <detailed description of the scene implementation>
code_structure: |
    <outline the structure of the Python code needed>
narration: |
    <narration script that would accompany this scene>
requires_research: true/false
research_query: <additional research needed if any>
next_step: "research" or "create_code"
```
""",
            temperature=0.7
        )
        
        response = llm.call(params)
        
        # Extract YAML content
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        plan = yaml.safe_load(yaml_str)
        
        return {
            "scene_index": scene_index,
            "scene_name": scene["name"],
            "scene_plan": plan
        }
    
    def post(self, shared, prep_res, exec_res):
        """Save the scene plan and determine next step."""
        if exec_res.get("status") == "complete":
            logger.info("All scenes have been planned")
            return "stitch_scenes"
            
        scene_index = exec_res["scene_index"]
        scene_plan = exec_res["scene_plan"]
        
        # Update the scene information with the detailed plan
        shared["scenes"][scene_index]["detailed_plan"] = scene_plan
        shared["current_scene"] = shared["scenes"][scene_index]
        
        logger.info(f"Completed planning for scene: {exec_res['scene_name']}")
        
        # Determine the next step based on the plan
        next_step = scene_plan.get("next_step", "create_code")
        
        if next_step == "research" and scene_plan.get("requires_research", False):
            shared["research_query"] = scene_plan.get("research_query", f"How to create a Manim animation for {shared['current_scene']['description']}?")
            return "research"
        else:
            return "create_code"

class ResearchStep(Node):
    """Perform additional research using RAG."""
    
    def prep(self, shared):
        """Prepare the research query."""
        return shared.get("research_query", "")
        
    def exec(self, query):
        """Query the RAG system for more information."""
        logger.info(f"Researching: {query}")
        
        result = rag_query(query)
        
        return {
            "status": result.get("status", "error"),
            "response": result.get("response", "No information found."),
            "retrieved_files": result.get("retrieved_files", [])
        }
    
    def post(self, shared, prep_res, exec_res):
        """Save the research results and move to code creation."""
        # Store the research results
        shared["research_results"] = exec_res
        
        logger.info(f"Research completed with status: {exec_res['status']}")
        
        # After research, always proceed to create code
        return "create_code"

class CreateCode(Node):
    """Create Manim code for the current scene."""
    
    def prep(self, shared):
        """Prepare the context for code creation."""
        current_scene = shared.get("current_scene", {})
        research_results = shared.get("research_results", {"response": "No additional research."})
        
        # Get paths from shared state
        project_dir = shared.get("project_dir")
        media_dir = shared.get("media_dir")
        
        # Create scene-specific directory
        scene_index = shared.get("current_scene_index", 0)
        scene_name = current_scene.get("name", f"scene_{scene_index}")
        
        # Sanitize scene name for file system
        sanitized_name = scene_name.lower().replace(" ", "_").replace("-", "_")
        scene_dir = os.path.join(project_dir, f"scene_{scene_index}_{sanitized_name}")
        os.makedirs(scene_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(scene_dir, f"{sanitized_name}.py")
        
        return {
            "scene": current_scene,
            "research": research_results.get("response", ""),
            "file_path": file_path,
            "scene_dir": scene_dir,
            "media_dir": media_dir
        }
        
    def exec(self, context):
        """Generate the Manim code."""
        scene = context["scene"]
        research = context["research"]
        file_path = context["file_path"]
        media_dir = context["media_dir"]
        
        logger.info(f"Creating code for scene: {scene.get('name', '')}")
        
        # Get the detailed plan
        detailed_plan = scene.get("detailed_plan", {})
        
        llm = LLM()
        params = LLMParams(
            prompt=f"""
### TASK
Create a complete, executable Manim animation code.

### SCENE INFORMATION
Scene: {scene.get('name', '')}
Description: {scene.get('description', '')}
Detailed plan: {detailed_plan.get('scene_plan', '')}

### RESEARCH INFORMATION
{research}

### INSTRUCTIONS
Write complete, working Manim animation code that implements the described scene. Include all necessary imports and make sure the code is fully executable.
The code should be self-contained and define a single Manim scene class.

Some key requirements:
1. Include all necessary imports (including from manim)
2. Create a complete scene class that inherits from Scene
3. Implement the construct method
4. Use appropriate objects, animations, and timing
5. Make sure the code follows Manim's conventions
6. The scene should have a descriptive name ending with "Scene" (e.g., "CircleTransformationScene")

Return your response in YAML format:

```yaml
thinking: |
    <your reasoning about the code implementation>
code: |
    # Complete Manim code here
    from manim import *
    
    class ExampleScene(Scene):
        def construct(self):
            # Your implementation here
            pass
narration: |
    <narration script for this scene>
```
""",
            temperature=0.2,  # Lower temperature for more precise code generation
            max_tokens=2048   # Allow more tokens for code generation
        )
        
        response = llm.call(params)
        
        # Extract YAML content
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        code_result = yaml.safe_load(yaml_str)
        
        # Get code and narration
        code = code_result.get("code", "")
        narration = code_result.get("narration", "")
        
        # Create the file
        file_result = create_file(file_path, code)
        
        # Create a narration file
        narration_path = file_path.replace(".py", "_narration.txt")
        create_file(narration_path, narration)
        
        return {
            "file_path": file_path,
            "narration_path": narration_path,
            "file_result": file_result,
            "code": code,
            "narration": narration,
            "media_dir": media_dir
        }
    
    def post(self, shared, prep_res, exec_res):
        """Save the code and proceed to testing."""
        # Save file information
        shared["current_scene_file"] = exec_res["file_path"]
        shared["current_scene_narration"] = exec_res["narration_path"]
        
        logger.info(f"Created code file: {exec_res['file_path']}")
        logger.info(f"Created narration file: {exec_res['narration_path']}")
        
        # Check if linting had warnings/errors
        lint_result = exec_res.get("file_result", {}).get("lint_result", {})
        if lint_result.get("lint_passed", True) is False:
            logger.warning(f"Linting issues detected: {lint_result.get('lint_errors', [])}")
        
        # Proceed to execute the code
        return "execute_code"

class ExecuteCode(Node):
    """Execute the Manim code and process the results."""
    
    def prep(self, shared):
        """Prepare the execution context."""
        return {
            "file_path": shared.get("current_scene_file", ""),
            "media_dir": shared.get("media_dir", "")
        }
        
    def exec(self, context):
        """Run the Manim code."""
        file_path = context["file_path"]
        media_dir = context["media_dir"]
        
        logger.info(f"Executing Manim code: {file_path}")
        logger.info(f"Using media directory: {media_dir}")
        
        # First, read the file for context
        file_content = read_file(file_path)
        
        # Validate the file before execution
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return {
                "file_path": file_path,
                "execution_result": {
                    "status": "error",
                    "message": error_msg,
                    "raw_error": error_msg,
                    "error_analysis": {
                        "error_type": "FileNotFoundError",
                        "error_description": "File could not be found",
                        "line_number": None
                    }
                },
                "file_content": file_content.get("content", "")
            }
        
        # Verify the file is a Python file
        if not file_path.endswith('.py'):
            error_msg = f"Only Python files can be executed with Manim: {file_path}"
            logger.error(error_msg)
            return {
                "file_path": file_path,
                "execution_result": {
                    "status": "error",
                    "message": error_msg,
                    "raw_error": error_msg,
                    "error_analysis": {
                        "error_type": "FileTypeError",
                        "error_description": "Attempted to execute a non-Python file with Manim",
                        "line_number": None
                    }
                },
                "file_content": file_content.get("content", "")
            }
        
        # Extract the class name from the file
        content = file_content.get("content", "")
        class_lines = [line for line in content.split("\n") if "class " in line and "(Scene)" in line]
        class_name = None
        
        if class_lines:
            # Extract the class name from the first match
            class_line = class_lines[0]
            class_name = class_line.split("class ")[1].split("(")[0].strip()
            logger.info(f"Detected scene class: {class_name}")
        else:
            logger.warning("Could not find scene class in the file")
            # Default to rendering the entire file
        
        # Run manim with explicit media directory and quality settings
        cmd = ["python", "-m", "manim", "render"]
        
        # Add quality flag (medium quality)
        cmd.extend(["-qm"])
        
        # Add media directory flag
        cmd.extend(["--media_dir", media_dir])
        
        # Add the file path
        cmd.append(file_path)
        
        # Add class name if found
        if class_name:
            cmd.append(class_name)
            
        cmd_str = " ".join(cmd)
        logger.info(f"Executing command: {cmd_str}")
            
        try:
            # Run the command and capture output
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            stdout = process.stdout
            stderr = process.stderr
            
            logger.info(f"STDOUT: {stdout}")
            if stderr:
                logger.info(f"STDERR: {stderr}")
                
            # Look for the generated video file
            video_file = None
            video_quality = "720p30"  # This matches the medium quality (-qm flag)
            
            # Construct the expected video path pattern
            if class_name:
                # Get the scene file name without extension
                scene_file_name = os.path.basename(file_path).replace(".py", "")
                video_pattern = os.path.join(media_dir, "videos", scene_file_name, video_quality, f"{class_name}.mp4")
                video_files = glob.glob(video_pattern)
                
                if video_files:
                    video_file = video_files[0]
                    logger.info(f"Found video file: {video_file}")
                else:
                    # Try a more general search if the specific pattern didn't work
                    logger.info(f"Video not found at expected path, trying general search")
                    video_pattern = os.path.join(media_dir, "videos", "**", "*.mp4")
                    video_files = glob.glob(video_pattern, recursive=True)
                    
                    if video_files:
                        # Get the most recently created video file
                        video_file = max(video_files, key=os.path.getctime)
                        logger.info(f"Found video file: {video_file}")
            
            return {
                "file_path": file_path,
                "execution_result": {
                    "status": "success",
                    "message": "Code executed successfully",
                    "stdout": stdout,
                    "stderr": stderr
                },
                "video_file": video_file
            }
        except subprocess.CalledProcessError as e:
            # Execution failed
            logger.error(f"Execution failed: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            
            # Analyze the error
            error_analysis = {
                "error_type": "ExecutionError",
                "error_description": "Failed to execute Manim code",
                "line_number": None,
                "error_details": e.stderr
            }
            
            # Try to extract line number from error
            error_lines = e.stderr.split("\n")
            for line in error_lines:
                if file_path in line and ", line " in line:
                    try:
                        line_num = line.split(", line ")[1].split(",")[0]
                        error_analysis["line_number"] = int(line_num)
                    except (IndexError, ValueError):
                        pass
            
            return {
                "file_path": file_path,
                "execution_result": {
                    "status": "error",
                    "message": f"Execution failed: {e}",
                    "raw_error": f"{e.stdout}\n{e.stderr}",
                    "error_analysis": error_analysis
                },
                "file_content": content
            }
    
    def post(self, shared, prep_res, exec_res):
        """Process execution results and determine next steps."""
        execution_result = exec_res.get("execution_result", {})
        status = execution_result.get("status", "error")
        
        if status == "success":
            logger.info("Code execution successful")
            
            # Get the video file path
            video_file = exec_res.get("video_file")
            if video_file:
                logger.info(f"Generated video: {video_file}")
                
                # Track the video file
                shared["scene_videos"].append(video_file)
            else:
                logger.warning("No video file found after execution")
            
            # Add to completed scenes
            current_index = shared.get("current_scene_index", 0)
            current_scene_file = exec_res.get("file_path", "")
            
            shared["completed_scenes"].append({
                "index": current_index,
                "scene": shared.get("current_scene", {}),
                "file_path": current_scene_file,
                "narration_path": shared.get("current_scene_narration", ""),
                "video_file": video_file
            })
            
            # Track scene file
            shared["scene_files"].append(current_scene_file)
            
            # Move to the next scene
            shared["current_scene_index"] = current_index + 1
            
            # Check if we've completed all scenes
            if shared["current_scene_index"] >= len(shared["scenes"]):
                logger.info("All scenes completed")
                return "stitch_scenes"
            else:
                logger.info(f"Moving to scene {shared['current_scene_index']+1}")
                return "plan_next_scene"
        else:
            # Code execution failed, we need to fix errors
            logger.error(f"Code execution failed: {execution_result.get('message', '')}")
            
            # Store error information for fixing
            shared["execution_error"] = execution_result
            shared["file_content"] = exec_res.get("file_content", "")
            
            return "fix_errors"

class FixErrors(Node):
    """Fix errors in the Manim code."""
    
    def prep(self, shared):
        """Prepare the context for error fixing."""
        return {
            "file_path": shared.get("current_scene_file", ""),
            "error": shared.get("execution_error", {}),
            "file_content": shared.get("file_content", ""),
            "scene": shared.get("current_scene", {})
        }
        
    def exec(self, context):
        """Generate fixed code based on the error."""
        file_path = context["file_path"]
        error = context["error"]
        file_content = context["file_content"]
        scene = context["scene"]
        
        logger.info(f"Fixing errors for: {file_path}")
        
        # Error analysis from the execution result
        error_analysis = error.get("error_analysis", {})
        raw_error = error.get("raw_error", "Unknown error")
        error_type = error_analysis.get("error_type", "Unknown")
        error_desc = error_analysis.get("error_description", "No description available")
        error_line = error_analysis.get("line_number", "Unknown")
        
        # Log detailed error information for better tracking
        logger.error(f"Error type: {error_type}")
        logger.error(f"Error description: {error_desc}")
        logger.error(f"Line number: {error_line}")
        logger.error(f"Raw error: {raw_error}")
        
        # Special handling for common errors
        special_instructions = ""
        if error_type == "FileTypeError":
            # Handle attempt to execute non-Python file
            logger.error("Detected attempt to execute non-Python file")
            if "narration" in file_path:
                # This is likely a case where it's trying to execute the narration file
                # We need to modify the correct Python file instead
                py_file_path = file_path.replace("_narration.txt", ".py")
                if os.path.exists(py_file_path):
                    logger.info(f"Switching to fix the Python file instead: {py_file_path}")
                    file_path = py_file_path
                    # Read the Python file content
                    py_file_content = read_file(py_file_path)
                    file_content = py_file_content.get("content", "")
                    special_instructions = "Note: The system mistakenly tried to execute the narration file instead of the Python file. Please ensure your code is complete and valid."
        
        llm = LLM()
        params = LLMParams(
            prompt=f"""
### TASK
Fix errors in Manim animation code.

### CODE
{file_content}

### ERROR INFORMATION
Raw Error: 
{raw_error}

Error Type: {error_analysis.get('error_type', 'Unknown')}
Error Description: {error_analysis.get('error_description', 'No description')}
Line Number: {error_analysis.get('line_number', 'Unknown')}

{special_instructions}

### SCENE INFORMATION
Scene: {scene.get('name', '')}
Description: {scene.get('description', '')}

### INSTRUCTIONS
Fix the errors in the Manim code. Focus on the specific errors reported, but also check for any other potential issues.
Be particularly careful with imports, class definitions, and Manim-specific syntax.
Return your response in YAML format:

```yaml
thinking: |
    <your analysis of the errors and how to fix them>
fixed_code: |
    # Complete fixed Manim code
    from manim import *
    
    class ExampleScene(Scene):
        def construct(self):
            # Your implementation here
            pass
changes: |
    <summary of changes made to fix the errors>
```
""",
            temperature=0.3  # Lower temperature for precise fixes
        )
        
        response = llm.call(params)
        
        # Extract YAML content
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        fix_result = yaml.safe_load(yaml_str)
        
        # Update the file with fixed code
        fixed_code = fix_result.get("fixed_code", "")
        
        # Create or update the file with the fixed code
        file_result = create_file(file_path, fixed_code)
        
        return {
            "file_path": file_path,
            "file_result": file_result,
            "changes": fix_result.get("changes", ""),
            "fixed_code": fixed_code
        }
    
    def post(self, shared, prep_res, exec_res):
        """Save the fixed code and retry execution."""
        logger.info(f"Applied fixes to: {exec_res['file_path']}")
        logger.info(f"Changes made: {exec_res['changes']}")
        
        # Reset the execution error
        shared.pop("execution_error", None)
        
        # Try executing the code again
        return "execute_code"

class StitchScenes(Node):
    """Combine all scenes into the final animation."""
    
    def prep(self, shared):
        """Prepare the stitching context."""
        return {
            "completed_scenes": shared.get("completed_scenes", []),
            "scene_videos": shared.get("scene_videos", []),
            "project_dir": shared.get("project_dir", ""),
            "file_name": shared.get("file_name", "animation")
        }
        
    def exec(self, context):
        """Generate and execute ffmpeg command to stitch videos."""
        completed_scenes = context["completed_scenes"]
        scene_videos = context["scene_videos"]
        project_dir = context["project_dir"]
        file_name = context["file_name"]
        
        logger.info(f"Stitching {len(completed_scenes)} scenes together")
        
        # Create final output directory
        final_dir = os.path.join(project_dir, "final")
        os.makedirs(final_dir, exist_ok=True)
        
        # Path for the final combined video
        final_video_path = os.path.join(final_dir, f"{file_name}.mp4")
        
        if not scene_videos:
            logger.warning("No scene videos to stitch")
            return {
                "status": "warning",
                "message": "No scene videos to stitch",
                "final_video_path": None
            }
            
        # If there's only one video, just copy it
        if len(scene_videos) == 1:
            video_path = scene_videos[0]
            logger.info(f"Only one scene video, copying to final location: {video_path}")
            
            try:
                import shutil
                shutil.copy2(video_path, final_video_path)
                logger.info(f"Copied video to: {final_video_path}")
                
                return {
                    "status": "success",
                    "message": "Single video copied successfully",
                    "final_video_path": final_video_path,
                    "scene_count": 1
                }
            except Exception as e:
                logger.error(f"Error copying video: {e}")
                return {
                    "status": "error",
                    "message": f"Error copying video: {e}",
                    "final_video_path": None
                }
        
        # For multiple videos, create a concat file
        concat_list_path = os.path.join(project_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for video_path in scene_videos:
                # Use file protocol and escape the path for compatibility
                f.write(f"file '{video_path}'\n")
        
        logger.info(f"Created concat list with {len(scene_videos)} videos: {concat_list_path}")
        
        # Use ffmpeg to concatenate the videos
        try:
            # First try with copy codec (fast)
            concat_cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
                "-i", concat_list_path, "-c", "copy", final_video_path
            ]
            logger.info(f"Running ffmpeg concat command: {' '.join(concat_cmd)}")
            
            subprocess.run(concat_cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully concatenated videos to: {final_video_path}")
            
            return {
                "status": "success",
                "message": "Videos concatenated successfully",
                "final_video_path": final_video_path,
                "scene_count": len(scene_videos)
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error concatenating videos with copy codec: {e}")
            logger.error(f"STDERR: {e.stderr}")
            logger.error(f"STDOUT: {e.stdout}")
            
            try:
                # Try again with re-encoding
                logger.info("Trying with re-encoding approach")
                reecode_cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
                    "-i", concat_list_path, "-c:v", "libx264", "-crf", "23", 
                    "-preset", "medium", final_video_path
                ]
                logger.info(f"Running ffmpeg re-encode command: {' '.join(reecode_cmd)}")
                
                subprocess.run(reecode_cmd, check=True, capture_output=True, text=True)
                logger.info(f"Successfully re-encoded and concatenated videos to: {final_video_path}")
                
                return {
                    "status": "success",
                    "message": "Videos re-encoded and concatenated successfully",
                    "final_video_path": final_video_path,
                    "scene_count": len(scene_videos)
                }
            except subprocess.CalledProcessError as e2:
                logger.error(f"Error re-encoding and concatenating videos: {e2}")
                logger.error(f"STDERR: {e2.stderr}")
                logger.error(f"STDOUT: {e2.stdout}")
                
                return {
                    "status": "error",
                    "message": f"Failed to concatenate videos: {e2}",
                    "final_video_path": None
                }
    
    def post(self, shared, prep_res, exec_res):
        """Finalize the animation project."""
        status = exec_res.get("status")
        
        if status == "success":
            logger.info(f"Animation project completed with {exec_res.get('scene_count')} scenes")
            logger.info(f"Final video: {exec_res.get('final_video_path')}")
            
            # Store the final result
            shared["final_result"] = {
                "status": "success",
                "final_video_path": exec_res.get("final_video_path"),
                "scene_count": exec_res.get("scene_count"),
                "completed_scenes": shared.get("completed_scenes", [])
            }
        else:
            logger.warning(f"Stitching completed with status: {status}")
            logger.warning(f"Message: {exec_res.get('message')}")
            
            # Store the result
            shared["final_result"] = {
                "status": status,
                "message": exec_res.get("message"),
                "scene_count": len(shared.get("completed_scenes", [])),
                "completed_scenes": shared.get("completed_scenes", [])
            }
            
        return "complete" 