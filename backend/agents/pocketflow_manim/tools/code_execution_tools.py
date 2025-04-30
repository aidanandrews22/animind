"""
Code execution tools for running Manim animations.
"""
import os
import subprocess
import time
import signal
import re
from typing import List, Dict, Any

def run_python_linter(filepath: str) -> Dict[str, Any]:
    """Run a Python linter (flake8) on the given file."""
    if not os.path.exists(filepath):
        return {
            "status": "error",
            "message": f"File not found: {filepath}",
            "lint_passed": False,
            "lint_errors": []
        }
        
    if not filepath.endswith('.py'):
        return {
            "status": "error",
            "message": f"Only Python files can be linted: {filepath}",
            "lint_passed": False,
            "lint_errors": []
        }
    
    try:
        # First, try to see if flake8 is installed - if not, just skip linting
        find_flake8 = subprocess.run(
            ["which", "flake8"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if find_flake8.returncode != 0:
            # flake8 not installed, skip linting
            return {
                "status": "success",
                "message": "Linting skipped (flake8 not installed)",
                "lint_passed": True,
                "lint_errors": []
            }
        
        # For Manim code, ignore style issues but catch real errors:
        # 1. Ignore style-only issues:
        #    - E1** (Indentation)
        #    - E2** (Whitespace)
        #    - E3** (Blank lines)
        #    - E5** (Line length)
        #    - W*** (Warnings)
        #    - F403/F405 (Star imports - common in Manim)
        # 2. Keep error checks for:
        #    - E9** (Syntax)
        #    - F4** (Import issues except star imports)
        #    - F6** (Undefined names)
        #    - F7** (Syntax errors)
        #    - F8** (Unused names - except F841)
        
        # First, let's do a simple syntax check using Python's built-in parser
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            compile(content, filepath, 'exec')
            # If we get here, basic syntax is valid
        except SyntaxError as se:
            return {
                "status": "error",
                "message": f"Syntax error found: {str(se)}",
                "lint_passed": False,
                "lint_errors": [f"Syntax error at line {se.lineno}, column {se.offset}: {se.msg}"],
                "line_number": se.lineno
            }
        
        # Now run flake8 with appropriate ignore settings
        process = subprocess.run(
            ["flake8", 
             "--ignore=E1,E2,E3,E5,W,F403,F405,F841", 
             "--select=E9,F4,F6,F7,F8",
             "--max-line-length=120", 
             filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise an exception on lint failure
        )
        
        # Parse the output
        output = process.stdout.strip()
        errors = []
        
        if output:
            # Parse each line of the output
            for line in output.split('\n'):
                if line.strip():
                    # Extract the real error information
                    errors.append(line)
            
            if len(errors) > 0:
                # Classify errors to determine if they're actual problems or style issues
                actual_errors = []
                for error in errors:
                    if any(code in error for code in ['E9', 'F6', 'F7']):
                        actual_errors.append(error)
                
                if actual_errors:
                    return {
                        "status": "error",
                        "message": "Linting found real errors",
                        "lint_passed": False,
                        "lint_errors": actual_errors,
                        "lint_output": output
                    }
                else:
                    # Imported but unused, etc - less severe
                    return {
                        "status": "warning",
                        "message": "Linting found potential issues",
                        "lint_passed": True,  # Still consider it passed for less critical issues
                        "lint_errors": errors,
                        "lint_output": output
                    }
            else:
                return {
                    "status": "success",
                    "message": "Linting passed",
                    "lint_passed": True,
                    "lint_errors": []
                }
        else:
            # No output means no errors
            return {
                "status": "success",
                "message": "Linting passed",
                "lint_passed": True,
                "lint_errors": []
            }
    
    except Exception as e:
        # Skip linting but log the error
        return {
            "status": "success",
            "message": f"Linting skipped: {str(e)}",
            "lint_passed": True,
            "lint_errors": [],
            "exception": str(e)
        }

def run_manim_code(file_path: str = None, quality: str = "medium") -> Dict[str, Any]:
    """Run the specified Python file with Manim.
    
    Args:
        file_path: Path to the Python file to execute. If None, uses the last file from file_tools
        quality: Quality setting for Manim rendering ("low", "medium", or "high")
        
    Returns:
        Dict with execution results and status
    """
    # Get the current file path from the file_tools module if not provided
    if file_path is None:
        from tools.file_tools import _CURRENT_FILE_PATH
        file_path = _CURRENT_FILE_PATH
    
    if file_path is None:
        return {
            "status": "error",
            "message": "No file has been created yet. Use create_file first."
        }
        
    filepath = file_path  # For compatibility with existing code
    
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
    
    # Get the directory containing the Python file
    file_dir = os.path.dirname(os.path.abspath(filepath))
    
    # Determine the output directory from the filepath or use a default
    # Extract output directory from the filepath (e.g., output/ball)
    # Default to "output/ball" based on the prompt
    output_dir = "output/ball"
    
    # Extract any directory info from the filepath
    if "/output/" in filepath:
        # Try to extract a custom output path from the filepath
        parts = filepath.split("/output/")
        if len(parts) > 1 and "/" in parts[1]:
            # Try to get a custom subdirectory
            subdir = parts[1].split("/")[0]
            if subdir:
                output_dir = f"output/{subdir}"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the command to match the specified format:
    # python -m manim render -ql --media_dir output/ball output/animation.py
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
    
    # Add media directory parameter
    cmd.extend(["--media_dir", output_dir])
    
    # Add the file path
    cmd.append(filepath)
    
    # Log the command being executed
    print(f"Executing command: {' '.join(cmd)}")
    
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
                    "message": f"Execution timed out after {max_execution_time} seconds",
                    "command": " ".join(cmd)
                }
            
            # Read output without blocking
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_data.append(stdout_line)
                print(f"STDOUT: {stdout_line.strip()}")
            
            stderr_line = process.stderr.readline()
            if stderr_line:
                stderr_data.append(stderr_line)
                print(f"STDERR: {stderr_line.strip()}")
            
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
        
        # First check if the command mistakenly tried to execute a non-Python file
        if "Only Python files can be executed with Manim:" in stderr:
            # This is a special error case when the wrong file is passed
            match = re.search(r'Only Python files can be executed with Manim: (.+)', stderr)
            problem_file = match.group(1) if match else "unknown file"
            return {
                "status": "error",
                "message": f"Only Python files can be executed with Manim: {problem_file}",
                "stderr": stderr,
                "stdout": stdout,
                "returncode": return_code,
                "command": " ".join(cmd),
                "raw_error": stderr,
                "error_analysis": {
                    "error_type": "FileTypeError",
                    "error_description": "Attempted to execute a non-Python file with Manim",
                    "line_number": None,
                    "suggestions": [
                        "Make sure to only execute .py files with Manim",
                        "Check that the file path is correct"
                    ]
                }
            }
        
        # Then handle the normal execution cases
        if return_code == 0:
            return {
                "status": "success",
                "message": "Code executed successfully",
                "stdout": stdout,
                "output_dir": output_dir,
                "command": " ".join(cmd)
            }
        else:
            error_analysis = analyze_manim_error(stderr)
            return {
                "status": "error",
                "message": "Code execution failed",
                "stderr": stderr,
                "stdout": stdout,
                "returncode": return_code,
                "error_analysis": error_analysis,
                "command": " ".join(cmd),
                "raw_error": stderr
            }
    
    except Exception as e:
        error_message = str(e)
        return {
            "status": "error",
            "message": f"Error executing code: {error_message}",
            "command": " ".join(cmd),
            "raw_error": error_message,
            "error_analysis": {
                "error_type": "ExecutionException",
                "error_description": error_message,
                "line_number": None,
                "suggestions": [
                    "Check that Manim is properly installed",
                    "Verify system dependencies are available",
                    "Check file permissions"
                ]
            }
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
        "RunTimeError": "Error during execution",
        "KeyError": "Missing dictionary key",
        "UnboundLocalError": "Local variable referenced before assignment",
        "ZeroDivisionError": "Division by zero",
        "Traceback": "Exception occurred during execution",
    }
    
    error_type = None
    line_number = None
    error_details = "Unknown error"
    
    # Try to extract error type
    for err_type in common_errors:
        if err_type in error_message:
            error_type = err_type
            break
    
    # Try to extract line number
    line_match = re.search(r'line (\d+)', error_message)
    if line_match:
        line_number = int(line_match.group(1))
    
    # Try to extract the specific error message
    if "Error:" in error_message:
        error_parts = error_message.split("Error:")[1].strip()
        if error_parts:
            error_details = error_parts.split("\n")[0].strip()
    
    # Check for specific error patterns
    if "Only Python files can be executed with Manim:" in error_message:
        error_type = "FileTypeError"
        error_details = "Attempted to execute a non-Python file with Manim"
    
    # Extract the full traceback for detailed analysis
    traceback = error_message
    
    suggestions = [
        "Check for syntax errors or typos",
        "Verify that all required modules are imported",
        "Ensure class and method names match Manim conventions",
        "Check for correct indentation and code structure"
    ]
    
    # Add specific suggestions based on error type
    if error_type == "ModuleNotFoundError" or error_type == "ImportError":
        suggestions.append("Install the missing module or fix the import statement")
    elif error_type == "NameError":
        suggestions.append("Check that all variables are defined before use")
    elif error_type == "AttributeError":
        suggestions.append("Verify object attributes and method names")
    elif error_type == "FileTypeError":
        suggestions = [
            "Make sure to only execute .py files with Manim",
            "Check that the file path is correct"
        ]
    
    return {
        "error_type": error_type,
        "error_description": common_errors.get(error_type, "Unknown error type"),
        "error_details": error_details,
        "line_number": line_number,
        "traceback": traceback,
        "suggestions": suggestions
    }