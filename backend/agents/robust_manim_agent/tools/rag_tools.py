import os
import traceback
from typing import List
from google.adk.tools import FunctionTool

# Import the rag agent using absolute path
import sys
sys.path.append("/Users/aidan/Documents/Code/Projects/animind/backend/agents")
from rag.agent import query_rag_agent

def rag_query(query: str) -> dict:
    """Query the RAG system for help with Manim-related questions.
    
    Args:
        query: The question to ask the RAG system
        
    Returns:
        A dictionary with the response and retrieved files from the RAG system
    """
    try:
        # Get the Manim RAG corpus from environment variable
        manim_rag_corpus = os.environ.get("MANIM_RAG_CORPUS")
        
        if not manim_rag_corpus:
            return {
                "status": "error",
                "message": "MANIM_RAG_CORPUS environment variable is not set",
                "query": query
            }
        
        # Query the RAG agent with the Manim corpus
        result = query_rag_agent(query, manim_rag_corpus)
        
        # Check if result contains the expected keys
        if not isinstance(result, dict) or 'response' not in result:
            return {
                "status": "error",
                "message": f"Unexpected response format from RAG agent: {str(result)}",
                "query": query
            }
            
        # Format the retrieved files for display
        formatted_files = []
        for file in result.get('retrieved_files', []):
            formatted_files.append({
                "title": file.get('title', ''),
                "content": file.get('content', ''),
                "uri": file.get('uri', '')
            })
        
        return {
            "status": "success",
            "response": result.get('response', ''),
            "retrieved_files": formatted_files,
            "query": query
        }
    except Exception as e:
        # Get the full traceback for better debugging
        error_traceback = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error querying RAG system: {str(e)}",
            "traceback": error_traceback,
            "query": query
        }

rag_query_tool = FunctionTool(func=rag_query)

def get_tools() -> List[FunctionTool]:
    """Get all RAG query tools."""
    return [rag_query_tool] 