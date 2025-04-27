"""
Tools for the video agent.
"""
from .tts_tools import get_tts_tools
from .video_tools import get_video_tools

def get_all_tools():
    """
    Get all tools used by the video agent.
    
    Returns:
        List of all tools
    """
    return [
        *get_tts_tools(),
        *get_video_tools(),
    ] 