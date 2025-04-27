"""
Tools for video generation and management.
"""
import os
import subprocess
from typing import Dict, List, Any
from google.adk.tools import FunctionTool
from robust_manim_agent.agent import generate_manim_animation

def generate_animation(prompt: str, 
                       output_dir: str = "animations") -> Dict[str, Any]:
    """
    Generate a Manim animation using the robust_manim_agent.
    
    Args:
        prompt: Description of the animation to generate
        output_dir: Directory to store the generated animation
        
    Returns:
        Dict with information about the generated animation
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the animation using robust_manim_agent
    result = generate_manim_animation(prompt)
    
    # Save the generated code to a file
    code_path = os.path.join(output_dir, "animation_code.py")
    with open(code_path, "w") as f:
        f.write(result["code"])
    
    return {
        "code_path": code_path,
        "execution_result": result["execution_result"],
        "success": "Error" not in result["execution_result"],
        "video_path": result.get("video_path", None)  # The path to the generated video
    }

def combine_audio_video(video_path: str, 
                        audio_path: str, 
                        output_path: str = "final_video.mp4") -> Dict[str, Any]:
    """
    Combine audio and video using FFmpeg.
    
    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        output_path: Path where the combined video will be saved
        
    Returns:
        Dict with information about the operation
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Combine audio and video using FFmpeg
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        return {
            "output_path": output_path,
            "success": True
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": str(e),
            "stderr": e.stderr.decode('utf-8')
        }

def get_video_tools() -> List[FunctionTool]:
    """
    Get all video tools.
    
    Returns:
        List of video tools
    """
    return [
        FunctionTool(func=generate_animation),
        FunctionTool(func=combine_audio_video)
    ] 