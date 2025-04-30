"""
Code execution tools for running Manim animations.
"""
import os
import subprocess
import time
import signal
import re
from typing import List, Dict, Any
from google.adk.tools import FunctionTool

def run_manim_code(filepath: str, quality: str = "medium") -> Dict[str, Any]:
    """Run the current Python file with Manim."""
    # Get the current file path from the file_tools module
    from .file import get
    
    if filepath is None:
        return {
            "status": "error",
            "message": "No file has been created yet. Use create_file first."
        }
            
    if not os.path.exists(filepath):
        return {
            "status": "error",
            "message": f"File not found: {filepath}"
        }
    
    if not filepath.endswith('.py'):
        return {
            "status": "error",
            "message": f"Only Python files can be executed with Manim: {filepath}"
        }
    
    # Prepare the output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(filepath)), "media")
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the command
    cmd = ["python", "-m", "manim", "render"]
    
    # Add quality flag
    if quality.lower() == "low":
        cmd.append("-ql")
    elif quality.lower() == "medium":
        cmd.append("-qm")
    elif quality.lower() == "high":
        cmd.append("-qh")
    else:
        cmd.append("-ql")  # Default to low quality
    
    # Add output directory
    cmd.extend(["--media_dir", output_dir])
    
    # Add the file path
    cmd.append(filepath)
    
    try:
        # Execute command with timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Set timeout (2 minutes)
        max_execution_time = 120
        start_time = time.time()
        
        stdout_data = []
        stderr_data = []
        
        while process.poll() is None:
            # Check for timeout
            if time.time() - start_time > max_execution_time:
                try:
                    os.kill(process.pid, signal.SIGTERM)
                    time.sleep(2)
                    if process.poll() is None:
                        os.kill(process.pid, signal.SIGKILL)
                except OSError:
                    pass
                
                return {
                    "status": "error",
                    "message": f"Execution timed out after {max_execution_time} seconds"
                }
            
            # Read output without blocking
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_data.append(stdout_line)
            
            stderr_line = process.stderr.readline()
            if stderr_line:
                stderr_data.append(stderr_line)
            
            time.sleep(0.1)
        
        # Get any remaining output
        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            stdout_data.append(remaining_stdout)
        if remaining_stderr:
            stderr_data.append(remaining_stderr)
        
        stdout = "".join(stdout_data)
        stderr = "".join(stderr_data)
        return_code = process.returncode
        
        if return_code == 0:
            return {
                "status": "success",
                "message": "Code executed successfully",
                "stdout": stdout,
                "output_dir": output_dir
            }
        else:
            error_analysis = analyze_manim_error(stderr)
            return {
                "status": "error",
                "message": "Code execution failed",
                "stderr": stderr,
                "stdout": stdout,
                "returncode": return_code,
                "error_analysis": error_analysis
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing code: {str(e)}"
        }

def analyze_manim_error(error_message: str) -> Dict[str, Any]:
    """Analyze Manim error messages to provide insights for fixing."""
    common_errors = {
        "ModuleNotFoundError": "Missing Python module",
        "ImportError": "Issue importing a module",
        "NameError": "Undefined variable or reference",
        "SyntaxError": "Python syntax error",
        "TypeError": "Operation applied to incorrect type",
        "ValueError": "Operation received incorrect value",
        "AttributeError": "Undefined attribute or method",
        "IndentationError": "Issue with code indentation",
        "FileNotFoundError": "Missing file reference",
    }
    
    error_type = None
    line_number = None
    
    # Try to extract error type
    for err_type in common_errors:
        if err_type in error_message:
            error_type = err_type
            break
    
    # Try to extract line number
    line_match = re.search(r'line (\d+)', error_message)
    if line_match:
        line_number = int(line_match.group(1))
    
    return {
        "error_type": error_type,
        "error_description": common_errors.get(error_type, "Unknown error type"),
        "line_number": line_number,
        "suggestions": [
            "Check for syntax errors or typos",
            "Verify that all required modules are imported",
            "Ensure class and method names match Manim conventions",
            "Check for correct indentation and code structure"
        ]
    }

# Create the tools
run_manim_code_tool = FunctionTool(func=run_manim_code)

def get_tools() -> List[FunctionTool]:
    """Get all code execution tools."""
    return [run_manim_code_tool] 