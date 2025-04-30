"""
File tools for the robust manim agent.
"""
import os
from typing import List, Dict, Any

# Global variable to store current file path
_CURRENT_FILE_PATH = None

def create_file(filepath: str, content: str) -> Dict[str, Any]:
    """Create a new file with the given content."""
    global _CURRENT_FILE_PATH
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    # Create the file
    with open(filepath, 'w') as f:
        f.write(content)
    
    # Set as current file
    _CURRENT_FILE_PATH = filepath
    
    result = {
        "status": "success",
        "message": f"File created at {filepath}",
        "filepath": filepath
    }
    
    # Run linter if it's a Python file
    if filepath.endswith('.py'):
        try:
            from code_execution_tools import run_python_linter
            lint_result = run_python_linter(filepath)
            result["lint_result"] = lint_result
            
            if lint_result.get("lint_passed", False) is False:
                result["lint_warnings"] = True
                result["lint_errors"] = lint_result.get("lint_errors", [])
        except ImportError:
            # If linter is not available, continue without it
            result["lint_result"] = {"status": "error", "message": "Linter not available"}
    
    # Return success message with optional lint results
    return result

def read_file(file_path: str = None) -> Dict[str, Any]:
    """Read a file with line numbers.
    
    Args:
        file_path: Optional path to the file to read. If None, uses the last created file
        
    Returns:
        Dict with file content and status
    """
    global _CURRENT_FILE_PATH
    
    # Use provided path or fall back to current path
    filepath = file_path if file_path is not None else _CURRENT_FILE_PATH
    
    if filepath is None:
        return {
            "status": "error",
            "message": "No file has been specified and no file has been created yet."
        }
        
    try:
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": f"File not found: {filepath}"
            }
            
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Format content with line numbers
        numbered_content = ""
        for i, line in enumerate(lines, 1):
            numbered_content += f"{i:4d} | {line}"
        
        return {
            "status": "success",
            "content": numbered_content,
            "raw_content": "".join(lines),
            "line_count": len(lines),
            "filepath": filepath
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading file: {str(e)}"
        }

def edit_file(start_line: int, end_line: int, new_content: str) -> Dict[str, Any]:
    """Edit specific lines in the current file."""
    global _CURRENT_FILE_PATH
    
    if _CURRENT_FILE_PATH is None:
        return {
            "status": "error",
            "message": "No file has been created yet. Use create_file first."
        }
    
    filepath = _CURRENT_FILE_PATH
    
    try:
        # Read the file
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        # Validate line numbers
        if start_line < 1 or start_line > len(lines) + 1:
            return {
                "status": "error",
                "message": f"Invalid start_line: {start_line}. Valid range is 1 to {len(lines) + 1}."
            }
            
        if end_line < start_line or end_line > len(lines) + 1:
            return {
                "status": "error", 
                "message": f"Invalid end_line: {end_line}. Must be between {start_line} and {len(lines) + 1}."
            }
            
        # Convert to 0-indexed
        start_idx = start_line - 1
        end_idx = end_line - 1
        
        # Ensure new content ends with newline
        if new_content and not new_content.endswith('\n'):
            new_content = new_content + '\n'
        
        # Replace the lines
        new_lines = new_content.splitlines(True)
        lines[start_idx:end_idx+1] = new_lines
        
        # Write the file back
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        result = {
            "status": "success", 
            "message": f"Edited {filepath} from line {start_line} to {end_line}"
        }
        
        # Run linter if it's a Python file
        if filepath.endswith('.py'):
            try:
                from code_execution_tools import run_python_linter
                lint_result = run_python_linter(filepath)
                result["lint_result"] = lint_result
                
                if lint_result.get("lint_passed", False) is False:
                    result["lint_warnings"] = True
                    result["lint_errors"] = lint_result.get("lint_errors", [])
            except ImportError:
                # If linter is not available, continue without it
                result["lint_result"] = {"status": "error", "message": "Linter not available"}
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error editing file: {str(e)}"
        }