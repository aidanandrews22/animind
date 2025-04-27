import logging
import time
import threading
from typing import Any, Dict, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("manim_agent.monitoring")

def monitor_tool_execution(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Monitor tool execution with timeouts and logging.
    
    This wrapper helps track long-running tools and ensures they return.
    
    Args:
        func: The function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The result of the function or an error dictionary
    """
    func_name = func.__name__ if hasattr(func, "__name__") else str(func)
    logger.info(f"Starting tool execution: {func_name}")
    start_time = time.time()
    
    try:
        # Execute the tool function
        result = None
        execution_timeout = 600  # 10 minutes max for any tool
        
        # Function to execute with timeout monitoring
        def execute_with_timeout():
            nonlocal result
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing {func_name}: {str(e)}")
                result = {"status": "error", "message": f"Error: {str(e)}"}
        
        # Start execution in a new thread
        thread = threading.Thread(target=execute_with_timeout)
        thread.daemon = True  # Allow the thread to be terminated when main program exits
        thread.start()
        
        # Wait for completion with timeout
        elapsed = 0
        check_interval = 1  # Check every second
        while thread.is_alive() and elapsed < execution_timeout:
            thread.join(timeout=check_interval)
            elapsed = time.time() - start_time
            if elapsed > 30 and elapsed % 30 < 1:  # Log progress every 30 seconds
                logger.info(f"Tool {func_name} still running after {elapsed:.1f} seconds")
        
        # Check if execution timed out
        if thread.is_alive():
            logger.error(f"Tool execution timed out after {elapsed:.1f} seconds: {func_name}")
            return {"status": "error", "message": f"Execution timed out after {execution_timeout} seconds"}
        
        # Log completion
        duration = time.time() - start_time
        logger.info(f"Tool execution completed: {func_name} in {duration:.2f} seconds")
        
        return result
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Exception in tool execution: {func_name} after {duration:.2f} seconds: {str(e)}")
        return {"status": "error", "message": f"Exception: {str(e)}"} 