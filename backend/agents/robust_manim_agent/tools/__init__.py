"""
Tools for the robust manim agent.
"""
from typing import List

from google.adk.tools import FunctionTool

from .file_tools import get_tools as get_file_tools
from .code_execution_tools import get_tools as get_code_execution_tools, run_manim_code
from .rag_tools import get_tools as get_rag_tools

def get_all_tools() -> List[FunctionTool]:
    """Get all tools for the robust manim agent."""
    return [
        *get_file_tools(),
        # Code execution tools are not directly exposed as they're called automatically
        # by the file tools after file creation/editing
        *get_rag_tools()
    ] 