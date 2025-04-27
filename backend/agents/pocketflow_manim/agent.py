from pocketflow import Flow, Node
from google import genai
import os
import enum
from pydantic import BaseModel
import json
from typing import List, Dict, Any, Optional
import dotenv
import logging
import datetime
from pathlib import Path

dotenv.load_dotenv()

# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"manim_agent_{timestamp}.log"

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("manim_agent")

# Assuming your RAG tool and file tools are already defined elsewhere
# Import them here
from file_tools import create_file as file_create_tool
from file_tools import read_file as file_read_tool
from file_tools import edit_file as file_edit_tool
from code_execution_tools import run_manim_code
# Assuming rag_query tool is defined

# Gemini model configuration
MODEL_NAME = "gemini-2.5-pro-preview-03-25"
TEMPERATURE = 0.2

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Define structured output schemas
class Action(enum.Enum):
    RESEARCH = "research"
    CREATE_FILE = "create_file"
    READ_FILE = "read_file"
    EDIT_FILE = "edit_file"
    FINAL_ANSWER = "final_answer"

class ResearchAction(BaseModel):
    query: str
    reasoning: str

class CreateFileAction(BaseModel):
    content: str
    reasoning: str

class ReadFileAction(BaseModel):
    reasoning: str

class EditFileAction(BaseModel):
    start_line: int
    end_line: int
    content: str
    reasoning: str

class FinalAnswerAction(BaseModel):
    answer: str

# Node for deciding the next action
class DecideActionNode(Node):
    def prep(self, shared):
        # Gather context for decision making
        context = shared.get("context", "")
        prompt = shared.get("prompt", "")
        execution_results = shared.get("execution_results", [])
        
        return {
            "context": context,
            "prompt": prompt,
            "execution_results": execution_results,
            "current_step": shared.get("current_step", 1)
        }
        
    def exec(self, inputs):
        context = inputs["context"]
        prompt = inputs["prompt"]
        execution_results = inputs["execution_results"]
        current_step = inputs["current_step"]
                
        # Construct decision prompt
        decision_prompt = f"""
        You are a Manim video generation agent that creates visually appealing, conceptually accurate animations.
        
        ### Current context:
        {context}
        
        ### Original prompt:
        {prompt}
        
        ### Execution history:
        {json.dumps(execution_results, indent=2) if execution_results else "No executions yet."}
        
        ### Current step: {current_step}
        
        Based on the workflow steps, decide what to do next:
        1. Research (rag_query) if you need more information
        2. Create a file if you're ready to write code
        3. Read the file to check line numbers
        4. Edit the file to fix errors or improve the code
        5. Provide final answer if the task is complete
        
        Decide the most appropriate next action.
        """
        
        logger.info(f"Step {current_step}: Deciding next action")
        logger.debug(f"Decision prompt: {decision_prompt}")
        
        response = client.models.generate_content(
            contents=decision_prompt,
            model=MODEL_NAME,
            config={
                'response_mime_type': 'application/json',
                'response_schema': {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": [a.value for a in Action]},
                        "reasoning": {"type": "string"},
                        "research_query": {"type": "string"},
                        "file_content": {"type": "string"},
                        "start_line": {"type": "integer"},
                        "end_line": {"type": "integer"},
                        "edit_content": {"type": "string"},
                        "final_answer": {"type": "string"}
                    },
                    "required": ["action", "reasoning"]
                }
            }
        )
        
        decision = json.loads(response.text)
        
        # Log decision
        logger.info(f"Decision: {decision['action']}")
        logger.info(f"Reasoning: {decision['reasoning']}")
        print(f"🤔 Agent decided to: {decision['action']}")
        print(f"Reasoning: {decision['reasoning']}")
        
        return decision
    
    def post(self, shared, prep_res, exec_res):
        # Update shared context with decision
        shared["last_decision"] = exec_res
        shared["current_step"] = shared.get("current_step", 1) + 1
        
        # Return action to determine flow path
        return exec_res["action"]

# Node for performing research using RAG
class ResearchNode(Node):
    def prep(self, shared):
        decision = shared.get("last_decision", {})
        return decision.get("research_query", "")
        
    def exec(self, query):
        # Call the RAG tool
        logger.info(f"Researching: {query}")
        print(f"🔍 Researching: {query}")
        # Assuming rag_query function is defined elsewhere
        results = rag_query(query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        # Add results to context
        current_context = shared.get("context", "")
        shared["context"] = current_context + f"\n\nRESEARCH QUERY: {prep_res}\nRESEARCH RESULTS: {exec_res}\n\n"
        
        # Add to execution history
        execution_results = shared.get("execution_results", [])
        execution_results.append({
            "action": "research",
            "query": prep_res,
            "results": exec_res
        })
        shared["execution_results"] = execution_results
        
        # Always go back to decision node
        return "decide"

# Node for creating a file
class CreateFileNode(Node):
    def prep(self, shared):
        decision = shared.get("last_decision", {})
        file_name = shared.get("file_name", "animation.py")
        output_dir = shared.get("output_dir", "./output")
        
        return {
            "content": decision.get("file_content", ""),
            "file_path": os.path.join(output_dir, file_name)
        }
        
    def exec(self, inputs):
        file_path = inputs["file_path"]
        content = inputs["content"]
        
        logger.info(f"Creating file: {file_path}")
        print(f"📝 Creating file: {file_path}")
        
        # Log the file content being created
        logger.debug(f"File content:\n{content}")
        
        result = file_create_tool(file_path, content)
        
        # Check if linting has warnings/errors
        if result.get("lint_warnings", False):
            logger.warning(f"Linting issues found in created file")
            logger.warning(f"Lint errors: {result.get('lint_errors', [])}")
            print(f"⚠️ Linting issues found. Will need to fix.")
            
            # Don't execute code with lint errors, set a flag to fix first
            shared = {}  # This will be populated in post
            shared["needs_lint_fix"] = True
            shared["lint_errors"] = result.get("lint_errors", [])
            return {
                "file_result": result,
                "execution_result": {
                    "status": "pending",
                    "message": "Fixing lint errors before execution"
                },
                "needs_lint_fix": True
            }
        
        # Automatically run the code if no lint errors
        logger.info("Executing Manim code")
        execution_result = run_manim_code()
        
        # Log execution results
        if execution_result['status'] == 'success':
            logger.info("Execution successful")
        else:
            logger.error(f"Execution failed: {execution_result.get('stderr', '')}")
            logger.error(f"Error analysis: {execution_result.get('error_analysis', {})}")
            logger.error(f"Raw error: {execution_result.get('raw_error', '')}")
        
        # Log stdout and stderr
        logger.debug(f"STDOUT:\n{execution_result.get('stdout', '')}")
        logger.debug(f"STDERR:\n{execution_result.get('stderr', '')}")
        logger.debug(f"Command executed: {execution_result.get('command', '')}")
        
        return {
            "file_result": result,
            "execution_result": execution_result,
            "needs_lint_fix": False
        }
    
    def post(self, shared, prep_res, exec_res):
        # Add results to context
        file_result = exec_res["file_result"]
        execution_result = exec_res["execution_result"]
        needs_lint_fix = exec_res.get("needs_lint_fix", False)
        
        # Update context with file creation and execution results
        current_context = shared.get("context", "")
        shared["context"] = current_context + f"\n\nFILE CREATION: {file_result['message']}\n"
        
        if needs_lint_fix:
            shared["context"] += f"LINTING ISSUES: {file_result.get('lint_errors', [])}\n"
            shared["context"] += f"ACTION: Need to fix linting issues before execution.\n"
            shared["needs_lint_fix"] = True
            shared["lint_errors"] = file_result.get("lint_errors", [])
            
            # Add lint errors to the context for the LLM to fix
            lint_context = "LINT ERRORS:\n"
            for error in file_result.get("lint_errors", []):
                lint_context += f"- {error}\n"
            shared["context"] += lint_context
            
        else:
            shared["context"] += f"EXECUTION: {execution_result['status']}\n"
            
            if execution_result['status'] == 'error':
                shared["context"] += f"ERROR: {execution_result.get('error_analysis', {}).get('error_description', '')}\n"
                shared["context"] += f"LINE NUMBER: {execution_result.get('error_analysis', {}).get('line_number', 'Unknown')}\n"
                shared["context"] += f"ERROR MESSAGE: {execution_result.get('stderr', '')}\n"
                shared["context"] += f"RAW ERROR: {execution_result.get('raw_error', '')}\n"
        
        # Add to execution history
        execution_results = shared.get("execution_results", [])
        execution_results.append({
            "action": "create_file",
            "file_path": prep_res["file_path"],
            "result": file_result,
            "execution": execution_result if not needs_lint_fix else {"status": "pending", "message": "Fixing lint errors"}
        })
        shared["execution_results"] = execution_results
        
        # If there are lint issues, our next action should be to edit the file
        if needs_lint_fix:
            # Return 'edit_file' to fix lint issues instead of going to decide node
            return "edit_file"
        
        # Always go back to decision node if no lint issues
        return "decide"

# Node for reading a file
class ReadFileNode(Node):
    def prep(self, shared):
        return {}
        
    def exec(self, inputs):
        logger.info("Reading file")
        print(f"📖 Reading file")
        result = file_read_tool()
        
        # Log the file content being read
        logger.debug(f"File content:\n{result.get('content', '')}")
        
        return result
    
    def post(self, shared, prep_res, exec_res):
        # Add results to context
        current_context = shared.get("context", "")
        shared["context"] = current_context + f"\n\nFILE CONTENT:\n{exec_res.get('content', '')}\n"
        
        # Add to execution history
        execution_results = shared.get("execution_results", [])
        execution_results.append({
            "action": "read_file",
            "result": exec_res
        })
        shared["execution_results"] = execution_results
        
        # Always go back to decision node
        return "decide"

# Node for editing a file
class EditFileNode(Node):
    def prep(self, shared):
        # If we're editing to fix lint errors, prepare differently
        if shared.get("needs_lint_fix", False):
            # Get the current file content to fix
            from file_tools import read_file
            read_result = read_file()
            
            if read_result["status"] == "success":
                file_content = read_result["content"]
                line_count = read_result["line_count"]
                
                return {
                    "start_line": 1,
                    "end_line": line_count,
                    "content": None,  # Will be generated during exec
                    "lint_errors": shared.get("lint_errors", []),
                    "file_content": file_content,
                    "fix_lint": True
                }
            else:
                # Something went wrong with reading the file
                return {
                    "error": "Could not read file for lint fixing",
                    "read_error": read_result["message"]
                }
        
        # Otherwise, use the normal decision-based editing
        decision = shared.get("last_decision", {})
        
        return {
            "start_line": decision.get("start_line", 1),
            "end_line": decision.get("end_line", 1),
            "content": decision.get("edit_content", ""),
            "fix_lint": False
        }
        
    def exec(self, inputs):
        # Check if we're fixing lint errors
        if inputs.get("fix_lint", False):
            # Generate fix based on lint errors
            start_line = inputs["start_line"]
            end_line = inputs["end_line"]
            lint_errors = inputs["lint_errors"]
            file_content = inputs["file_content"]
            
            # Use Gemini to generate a fixed version of the file
            prompt = f"""
            You are a code linting assistant. Fix the following Python file to address these linting issues:
            
            LINT ERRORS:
            {json.dumps(lint_errors, indent=2)}
            
            CURRENT FILE CONTENT:
            {file_content}
            
            Return only the fixed Python code with no explanations or markdown formatting.
            """
            
            logger.info("Generating linting fixes")
            print(f"🔧 Fixing lint errors automatically")
            
            response = client.models.generate_content(
                contents=prompt,
                model=MODEL_NAME,
                config={"temperature": 0.2}
            )
            
            fixed_content = response.text.strip()
            
            # Make the edit
            logger.info(f"Applying lint fixes to the entire file")
            result = file_edit_tool(start_line, end_line, fixed_content)
            
            # Run the code after fixing
            logger.info("Executing Manim code after lint fixes")
            execution_result = run_manim_code()
            
            # Log execution results
            if execution_result['status'] == 'success':
                logger.info("Execution successful after lint fixes")
            else:
                logger.error(f"Execution failed after lint fixes: {execution_result.get('stderr', '')}")
                logger.error(f"Error analysis: {execution_result.get('error_analysis', {})}")
                logger.error(f"Raw error: {execution_result.get('raw_error', '')}")
            
            return {
                "edit_result": result,
                "execution_result": execution_result,
                "was_lint_fix": True
            }
        
        # Regular edit path
        start_line = inputs["start_line"]
        end_line = inputs["end_line"]
        content = inputs["content"]
        
        logger.info(f"Editing file from line {start_line} to {end_line}")
        print(f"✏️ Editing file from line {start_line} to {end_line}")
        
        # Log the edit content
        logger.debug(f"Edit content:\n{content}")
        
        result = file_edit_tool(start_line, end_line, content)
        
        # Check if linting has warnings/errors
        if result.get("lint_warnings", False):
            logger.warning(f"Linting issues found in edited file")
            logger.warning(f"Lint errors: {result.get('lint_errors', [])}")
            print(f"⚠️ Linting issues found after edit. Will need to fix.")
            
            # Don't execute code with lint errors, return to prepare for another edit
            return {
                "edit_result": result,
                "execution_result": {
                    "status": "pending",
                    "message": "Fixing lint errors before execution"
                },
                "needs_lint_fix": True,
                "lint_errors": result.get("lint_errors", [])
            }
        
        # Automatically run the code
        logger.info("Executing Manim code after edit")
        execution_result = run_manim_code()
        
        # Log execution results
        if execution_result['status'] == 'success':
            logger.info("Execution successful")
        else:
            logger.error(f"Execution failed: {execution_result.get('stderr', '')}")
            logger.error(f"Error analysis: {execution_result.get('error_analysis', {})}")
            logger.error(f"Raw error: {execution_result.get('raw_error', '')}")
        
        # Log stdout and stderr
        logger.debug(f"STDOUT:\n{execution_result.get('stdout', '')}")
        logger.debug(f"STDERR:\n{execution_result.get('stderr', '')}")
        logger.debug(f"Command executed: {execution_result.get('command', '')}")
        
        return {
            "edit_result": result,
            "execution_result": execution_result,
            "was_lint_fix": False,
            "needs_lint_fix": False
        }
    
    def post(self, shared, prep_res, exec_res):
        # Add results to context
        edit_result = exec_res["edit_result"]
        execution_result = exec_res["execution_result"]
        was_lint_fix = exec_res.get("was_lint_fix", False)
        needs_lint_fix = exec_res.get("needs_lint_fix", False)
        
        # Update context with edit and execution results
        current_context = shared.get("context", "")
        
        if was_lint_fix:
            shared["context"] = current_context + f"\n\nLINT FIX: {edit_result['message']}\nEXECUTION: {execution_result['status']}\n"
        else:
            shared["context"] = current_context + f"\n\nFILE EDIT: {edit_result['message']}\n"
            
            if needs_lint_fix:
                shared["context"] += f"LINTING ISSUES: {exec_res.get('lint_errors', [])}\n"
                shared["context"] += f"ACTION: Need to fix linting issues before execution.\n"
                shared["needs_lint_fix"] = True
                shared["lint_errors"] = exec_res.get("lint_errors", [])
                
                # Add lint errors to the context for the LLM to fix
                lint_context = "LINT ERRORS:\n"
                for error in exec_res.get("lint_errors", []):
                    lint_context += f"- {error}\n"
                shared["context"] += lint_context
            else:
                shared["context"] += f"EXECUTION: {execution_result['status']}\n"
        
        if execution_result['status'] == 'error':
            shared["context"] += f"ERROR: {execution_result.get('error_analysis', {}).get('error_description', '')}\n"
            shared["context"] += f"LINE NUMBER: {execution_result.get('error_analysis', {}).get('line_number', 'Unknown')}\n"
            shared["context"] += f"ERROR MESSAGE: {execution_result.get('stderr', '')}\n"
            shared["context"] += f"RAW ERROR: {execution_result.get('raw_error', '')}\n"
        
        # Add to execution history
        execution_results = shared.get("execution_results", [])
        execution_results.append({
            "action": "edit_file",
            "start_line": prep_res.get("start_line", 1),
            "end_line": prep_res.get("end_line", 1),
            "result": edit_result,
            "execution": execution_result,
            "was_lint_fix": was_lint_fix
        })
        shared["execution_results"] = execution_results
        
        # Clear the needs_lint_fix flag if we just fixed it
        if was_lint_fix or (not needs_lint_fix):
            shared.pop("needs_lint_fix", None)
            shared.pop("lint_errors", None)
        
        # If we still need to fix lint errors, stay in the edit mode
        if needs_lint_fix:
            return "edit_file"
            
        # Always go back to decision node
        return "decide"

# Node for providing the final answer
class FinalAnswerNode(Node):
    def prep(self, shared):
        decision = shared.get("last_decision", {})
        return decision.get("final_answer", "")
        
    def exec(self, final_answer):
        logger.info("Task completed")
        print(f"✅ Task completed")
        return final_answer
    
    def post(self, shared, prep_res, exec_res):
        # Save final answer
        shared["final_answer"] = exec_res
        
        # No next step needed
        return "done"

def create_manim_agent_flow():
    """
    Create and connect the nodes to form a complete Manim video generation agent flow.
    """
    # Create instances of each node
    decide = DecideActionNode()
    research = ResearchNode()
    create_file = CreateFileNode()
    read_file = ReadFileNode()
    edit_file = EditFileNode()
    final_answer = FinalAnswerNode()
    
    # Connect the nodes with conditional transitions
    decide - "research" >> research
    decide - "create_file" >> create_file
    decide - "read_file" >> read_file
    decide - "edit_file" >> edit_file
    decide - "final_answer" >> final_answer
    
    # All nodes except final_answer go back to decide node
    research - "decide" >> decide
    create_file - "decide" >> decide
    create_file - "edit_file" >> edit_file  # New path for lint fix
    read_file - "decide" >> decide
    edit_file - "decide" >> decide
    edit_file - "edit_file" >> edit_file  # Self-loop for lint fix
    
    # Create and return the flow, starting with the decide node
    return Flow(start=decide)

def rag_query(query):
    """
    Placeholder for RAG implementation.
    In a real implementation, this would use vector search to find relevant documents.
    """
    # This is just a placeholder - you mentioned the RAG tool is already defined
    logger.info(f"RAG query: {query}")
    return f"Results for query: {query}"

def run_manim_agent(output_dir="./output", file_name="animation.py", prompt=""):
    """
    Run the Manim video generation agent with the given parameters.
    
    Args:
        output_dir (str): Directory to save the output files
        file_name (str): Name of the Python file to create
        prompt (str): User prompt describing the desired Manim animation
    
    Returns:
        dict: The final state of the agent, including the generated code and results
    """
    # Create a specific log file for this run
    run_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_file = logs_dir / f"run_{run_timestamp}.log"
    run_logger = logging.getLogger(f"manim_agent_run_{run_timestamp}")
    file_handler = logging.FileHandler(run_log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    run_logger.addHandler(file_handler)
    run_logger.setLevel(logging.DEBUG)
    
    # Save the output directory and prompt to the log
    run_logger.info(f"Output directory: {output_dir}")
    run_logger.info(f"File name: {file_name}")
    run_logger.info(f"Prompt: {prompt}")
    
    # Create the agent flow
    agent_flow = create_manim_agent_flow()
    
    # Initialize shared state
    shared = {
        "output_dir": output_dir,
        "file_name": file_name,
        "prompt": prompt,
        "context": f"INITIAL PROMPT: {prompt}\n",
        "current_step": 1,
        "execution_results": [],
        "logger": run_logger
    }
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the agent
    logger.info(f"Starting Manim video generation agent with prompt: {prompt}")
    print(f"🚀 Starting Manim video generation agent with prompt: {prompt}")
    
    try:
        agent_flow.run(shared)
        logger.info("Agent flow completed successfully")
    except Exception as e:
        logger.exception("Error in agent flow execution")
        run_logger.exception("Error in agent flow execution")
        print(f"❌ Error in agent flow execution: {str(e)}")
    
    # Save the final state to a JSON file
    result_file = logs_dir / f"result_{run_timestamp}.json"
    with open(result_file, 'w') as f:
        # Create a serializable copy of shared
        serializable_shared = {k: v for k, v in shared.items() if k != 'logger'}
        json.dump(serializable_shared, f, indent=2)
    
    logger.info(f"Results saved to {result_file}")
    
    # Return the final state
    return shared

# Example usage
if __name__ == "__main__":
    import sys
    
    # Default values
    output_dir = "./output"
    file_name = "animation.py"
    prompt = "create a physics video of a ball rolling down a hill. output dir: ./output/ball. Be creative. Complexity: a more advanced explanation involving energy conservation make sure to show vectors, rate of change, derviations, etc. Duration: 1-3 mins (medium)"
    
    logger.info("Starting Manim agent script")
    
    # Get values from command line if provided
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    if len(sys.argv) > 2:
        file_name = sys.argv[2]
    if len(sys.argv) > 3:
        output_dir = sys.argv[3]
    
    logger.info(f"Command line arguments: prompt='{prompt}', file_name='{file_name}', output_dir='{output_dir}'")
    
    # Run the agent
    result = run_manim_agent(output_dir, file_name, prompt)
    
    # Print final answer
    print("\n🎬 Final Result:")
    print(result.get("final_answer", "No final answer provided"))
    logger.info("Script execution completed")