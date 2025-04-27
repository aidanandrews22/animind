import os
import subprocess
import tempfile
import shutil
import logging
import time
import signal
import functools
from typing import List, Dict, Any, Optional, Callable
from google.adk.tools import FunctionTool
from ..monitoring import monitor_tool_execution

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("manim_agent.code_execution")

def run_manim_code(
    filepath: str,
    output_dir: str = "auto",
    scene_name: str = "",
    quality: str = "medium",
) -> Dict[str, Any]:
    """Run a Manim Python file in a controlled environment.
    
    Args:
        filepath: Path to the Python file to execute. Required.
        output_dir: Directory to save the output video (use "auto" for auto-generated directory). 
                    Optional, defaults to "auto".
        scene_name: Name of the scene class to render (use empty string for all scenes).
                    Optional, defaults to "" (all scenes).
        quality: Video quality - can be "low", "medium", or "high".
                 Optional, defaults to "medium".
        
    Returns:
        A dictionary with execution results and output information
    """
    logger.info(f"Starting code execution: {filepath}, scene: {scene_name}, quality: {quality}")
    try:
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return {
                "status": "error",
                "message": f"File not found: {filepath}"
            }
        
        # Prepare the output directory
        if output_dir == "auto" or not output_dir:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(filepath)), "media")
        
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory prepared: {output_dir}")
        
        # Build the command
        cmd = ["python", "-m", "manim"]
        
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
        
        # Add scene name if provided
        if scene_name and scene_name != "":
            cmd.append(scene_name)
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute in a controlled environment with a timeout
        try:
            # Start process with Popen for better control
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            logger.info(f"Process started with PID: {process.pid}")
            
            # Set a timeout (5 minutes)
            max_execution_time = 300  # seconds
            start_time = time.time()
            
            stdout_data = []
            stderr_data = []
            
            # Collect output with polling to avoid blocking
            while process.poll() is None:
                # Check for timeout
                if time.time() - start_time > max_execution_time:
                    logger.warning(f"Process timed out after {max_execution_time} seconds")
                    # Send SIGTERM to process group
                    try:
                        # Try sending signal to the process
                        os.kill(process.pid, signal.SIGTERM)
                        # Give it some time to terminate gracefully
                        time.sleep(2)
                        # Force kill if still running
                        if process.poll() is None:
                            os.kill(process.pid, signal.SIGKILL)
                    except OSError as e:
                        logger.error(f"Error terminating process: {e}")
                    
                    break
                
                # Read output without blocking
                stdout_line = process.stdout.readline()
                if stdout_line:
                    logger.info(f"Process output: {stdout_line.strip()}")
                    stdout_data.append(stdout_line)
                
                stderr_line = process.stderr.readline()
                if stderr_line:
                    logger.warning(f"Process error: {stderr_line.strip()}")
                    stderr_data.append(stderr_line)
                
                # Avoid CPU spinning
                time.sleep(0.1)
            
            # Get any remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_data.append(remaining_stdout)
            if remaining_stderr:
                stderr_data.append(remaining_stderr)
            
            # Combine collected output
            stdout = "".join(stdout_data)
            stderr = "".join(stderr_data)
            return_code = process.returncode
            
            # Log completion
            logger.info(f"Process completed with return code: {return_code}")
            
        except Exception as e:
            logger.error(f"Error during process execution: {str(e)}")
            return {
                "status": "error",
                "message": f"Error during execution: {str(e)}",
                "debug_options": [
                    "1. Rewrite entire file",
                    "2. Rewrite specific lines",
                    "3. Exit (try running as is)"
                ]
            }
        
        if return_code == 0:
            # Success
            logger.info("Code executed successfully")
            return {
                "status": "success",
                "message": "Code executed successfully",
                "stdout": stdout,
                "output_dir": output_dir,
                "scene_name": scene_name or "all scenes"
            }
        else:
            # Error
            logger.error(f"Code execution failed with return code {return_code}")
            return {
                "status": "error",
                "message": "Code execution failed",
                "stderr": stderr,
                "stdout": stdout,
                "returncode": return_code,
                "error_analysis": analyze_manim_error(stderr)
            }
    
    except subprocess.TimeoutExpired:
        logger.error("Execution timed out (exceeded 5 minutes)")
        return {
            "status": "error",
            "message": "Execution timed out (exceeded 5 minutes)"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": f"Error executing code: {str(e)}"
        }

# Create FunctionTool with just the function
run_manim_code_tool = FunctionTool(func=run_manim_code)

def analyze_manim_error(error_message: str) -> Dict[str, Any]:
    """Analyze Manim error messages to provide insights for fixing.
    
    Args:
        error_message: The error output from running Manim
        
    Returns:
        A dictionary with error analysis and suggestions
    """
    logger.info("Analyzing Manim error")
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
    file_name = None
    
    # Try to extract error type
    for err_type in common_errors:
        if err_type in error_message:
            error_type = err_type
            break
    
    # Try to extract line number using common patterns
    import re
    line_match = re.search(r'line (\d+)', error_message)
    if line_match:
        line_number = int(line_match.group(1))
    
    # Try to extract filename
    file_match = re.search(r'File "([^"]+)"', error_message)
    if file_match:
        file_name = file_match.group(1)
    
    logger.info(f"Error analysis - Type: {error_type}, Line: {line_number}, File: {file_name}")
    
    analysis = {
        "error_type": error_type,
        "error_description": common_errors.get(error_type, "Unknown error type"),
        "line_number": line_number,
        "file_name": file_name,
        "suggestions": [
            "Check for syntax errors or typos",
            "Verify that all required modules are imported",
            "Ensure class and method names match Manim conventions",
            "Check for correct indentation and code structure",
            "Verify that file paths and references are correct"
        ]
    }
    
    return {
        "status": "success",
        "analysis": analysis,
        "raw_error": error_message
    }
analyze_manim_error_tool = FunctionTool(func=analyze_manim_error)

# Apply monitoring with a decorator pattern
def with_monitoring(func: Callable) -> Callable:
    """Decorator to add monitoring to a function."""
    @functools.wraps(func)  # Preserve function metadata
    def wrapper(*args, **kwargs):
        return monitor_tool_execution(func, *args, **kwargs)
    return wrapper

# Create monitored versions with decorator
run_manim_code_monitored = with_monitoring(run_manim_code)
analyze_manim_error_monitored = with_monitoring(analyze_manim_error)

# Create monitored tool instances
run_manim_code_tool_monitored = FunctionTool(func=run_manim_code_monitored)
analyze_manim_error_tool_monitored = FunctionTool(func=analyze_manim_error_monitored)

def get_tools() -> List[FunctionTool]:
    """Get all code execution tools."""
    return [
        run_manim_code_tool_monitored,
        analyze_manim_error_tool_monitored
    ] 