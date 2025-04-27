import os
import json
from typing import List, Optional, Dict, Union
from google.adk.tools import FunctionTool
from .code_execution_tools import run_manim_code

# Global variable to store current file path (automatically set when a file is created)
_CURRENT_FILE_PATH = None

# Helper function to run Manim automatically after file operations when applicable
def _auto_run_manim_if_python(filepath: str, result: dict) -> dict:
    """Automatically run Manim code execution if the file is a Python file.
    
    Args:
        filepath: Path to the file that was created or edited
        result: The result dict from the file operation
        
    Returns:
        A dictionary with combined file operation and Manim execution results
    """
    # Only run Manim for Python files
    if filepath.endswith('.py') and result["status"] == "success":
        # Run Manim code execution
        manim_result = run_manim_code(
            filepath=filepath,
            output_dir="auto",  # Use auto-generated directory
            scene_name="",      # Run all scenes
            quality="medium"    # Use medium quality
        )
        
        # Combine results
        combined_result = {
            **result,
            "manim_execution": manim_result
        }
        return combined_result
    
    # Return original result for non-Python files or failed operations
    return result

def create_file(filepath: str, content: str) -> dict:
    """Create a new file with the given content.
    
    Args:
        filepath: Path to the file to create
        content: Content to write to the file
        
    Returns:
        A dictionary with a status message and the file path created
    """
    global _CURRENT_FILE_PATH
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    # Create the file
    with open(filepath, 'w') as f:
        f.write(content)
    
    # Automatically set as current file
    _CURRENT_FILE_PATH = filepath
    
    result = {
        "status": "success",
        "message": f"File created at {filepath}",
        "filepath": filepath
    }
    
    # Automatically run Manim if it's a Python file
    return _auto_run_manim_if_python(filepath, result)
    
create_file_tool = FunctionTool(func=create_file)

def read_file() -> dict:
    """Read the current file with line numbers.
    
    Returns:
        A dictionary with the file content formatted with line numbers or an error message
    """
    global _CURRENT_FILE_PATH
    
    if _CURRENT_FILE_PATH is None:
        return {
            "status": "error",
            "message": "No file has been created yet. Use create_file first."
        }
        
    filepath = _CURRENT_FILE_PATH
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Format content with line numbers
        numbered_content = ""
        for i, line in enumerate(lines, 1):
            numbered_content += f"{i:4d} | {line}"
        
        return {
            "status": "success",
            "content": numbered_content,
            "line_count": len(lines),
            "filepath": filepath
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"File not found: {filepath}\nError: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading file: {str(e)}"
        }
read_file_tool = FunctionTool(func=read_file)

def list_files(directory: str) -> dict:
    """List files in a directory.
    
    Args:
        directory: Path to the directory to list (use "." for current directory)
        
    Returns:
        A dictionary with the list of files
    """
    try:
        files = os.listdir(directory)
        
        return {
            "status": "success",
            "files": files,
            "directory": directory
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing files: {str(e)}"
        }
list_files_tool = FunctionTool(func=list_files)

def edit_file(start_line: int, end_line: int, new_content: str) -> dict:
    """Edit specific lines in the current file.
    
    This function makes it easy to edit a specific part of the current file by replacing 
    a range of lines with new content. Line numbers are 1-indexed (first line is 1).
    
    Args:
        start_line: First line to replace (1-indexed)
        end_line: Last line to replace (1-indexed)
        new_content: The new content to replace the specified lines
        
    Returns:
        A dictionary with a status message
    """
    global _CURRENT_FILE_PATH
    
    if _CURRENT_FILE_PATH is None:
        return {
            "status": "error",
            "message": "No file has been created yet. Use create_file first."
        }
    
    filepath = _CURRENT_FILE_PATH
    
    try:
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": f"File not found: {filepath}"
            }
            
        # Read the file to check line count
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        # Validate line numbers
        if start_line < 1:
            return {
                "status": "error",
                "message": f"Invalid start_line: {start_line}. Line numbers start at 1."
            }
            
        if end_line > len(lines):
            return {
                "status": "error", 
                "message": f"Invalid end_line: {end_line}. File only has {len(lines)} lines."
            }
            
        if start_line > end_line:
            return {
                "status": "error",
                "message": f"start_line ({start_line}) cannot be greater than end_line ({end_line})."
            }
            
        # Convert to 0-indexed for internal processing
        start_idx = start_line - 1
        end_idx = end_line
        
        # Ensure new content ends with newline
        if new_content and not new_content.endswith('\n'):
            new_content = new_content + '\n'
        
        # Replace the lines
        new_lines = new_content.splitlines(True)
        lines[start_idx:end_idx] = new_lines
        
        # Write the file back
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        result = {
            "status": "success", 
            "message": f"Made line edits to {filepath} from line {start_line} to {end_line}"
        }
        
        # Automatically run Manim if it's a Python file
        return _auto_run_manim_if_python(filepath, result)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error editing file: {str(e)}"
        }
edit_file_tool = FunctionTool(func=edit_file)

def get_tools() -> List[FunctionTool]:
    """Get all file operation tools."""
    return [
        create_file_tool, 
        read_file_tool, 
        edit_file_tool, 
        list_files_tool
    ] 