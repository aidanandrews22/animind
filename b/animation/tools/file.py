# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.tools import ToolContext
from google.genai import types
from .exec_code import run_manim_code
from typing import Dict, Any

import os


def create_file(filename: str, content: str, tool_context: ToolContext) -> Dict[str, Any]:
  """Create a file.

  Args:
    filename(str): The filename to create.
    content(str): The content of the file.
    tool_context(ToolContext): The function context.

  Returns:
    str: The search result displayed in a webpage.
  """
  # Store filename in the persistent state
  tool_context.state[f"{tool_context.state.APP_PREFIX}current_filename"] = filename
  os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
  with open(filename, "w") as f:
      f.write(content)

  execution_result = {}
  if filename.endswith('.py'):
    execution_result = run_manim_code(filename)
  
  # Return success message with execution results if available
  result = {
      "status": "success",
      "message": f"File created at {filename}",
      "filename": filename
  }
  
  # Include execution results if available
  if execution_result:
      result["execution_result"] = execution_result
  
  return result

def read_file(tool_context: ToolContext) -> Dict[str, Any]:
  """Read a file.

  Args:
    tool_context(ToolContext): The function context.

  Returns:
    str: The content of the file.
  """

  filename = tool_context.state.get(f"{tool_context.state.APP_PREFIX}current_filename")
  if filename is None:
    return {
        "status": "error",
        "message": "No file has been created yet. Use create_file first."
    }
  
  try:
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Format content with line numbers
    numbered_content = ""
    for i, line in enumerate(lines, 1):
        numbered_content += f"{i:4d} | {line}"
    
    return {
        "status": "success",
        "content": numbered_content,
        "line_count": len(lines),
        "filepath": filename
    }
  except Exception as e:
    return {
      "status": "error",
      "message": f"Error reading file: {str(e)}"
    }

def edit_file(start_line: int, end_line: int, content: str, tool_context: ToolContext) -> str:
  """Edit a file using line numbers.

  Args:
    start_line(int): The start line to edit.
    end_line(int): The end line to edit.
    content(str): The content to edit the file with.
    tool_context(ToolContext): The function context.

  Returns:
    str: The content of the file.
  """
  filename = tool_context.state.get(f"{tool_context.state.APP_PREFIX}current_filename")
  if filename is None:
    return {
      "status": "error",
      "message": "No file has been created yet. Use create_file first."
    }
    
  filepath = filename
  
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
    
    # Automatically run Manim code if it's a Python file
    execution_result = {}
    if filepath.endswith('.py'):
      execution_result = run_manim_code(filepath)
    
    # Prepare the result
    result = {
      "status": "success", 
      "message": f"Edited {filepath} from line {start_line} to {end_line}"
    }
    
    # Include execution results if available
    if execution_result:
      result["execution_result"] = execution_result
        
    return result
      
  except Exception as e:
    return {
      "status": "error",
      "message": f"Error editing file: {str(e)}"
    }
