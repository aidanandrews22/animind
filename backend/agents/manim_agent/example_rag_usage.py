#!/usr/bin/env python3
"""
Example script demonstrating how to use the RAG query tool within the manim agent.
This shows how to programmatically query the RAG system for Manim-related information.
"""

import os
from dotenv import load_dotenv
from tools.rag_tools import rag_query

# Load environment variables (including MANIM_RAG_CORPUS)
load_dotenv()

def test_rag_query():
    """Test the RAG query tool with various Manim-related questions."""
    questions = [
        "How do I create a sine wave animation in Manim?",
        "Show me examples of 3D transformations in Manim",
        "How can I implement color gradients in Manim objects?",
        "What's the correct way to add text next to an animation?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}\n[Query {i}] {question}\n{'='*80}")
        
        # Call the RAG query tool
        result = rag_query(question)
        
        if result["status"] == "success":
            print("\n--- Response ---")
            print(result["response"])
            
            print(f"\n--- Retrieved {len(result['retrieved_files'])} Files ---")
            for j, file in enumerate(result["retrieved_files"][:2], 1):  # Show first 2 files only
                print(f"\n[File {j}] {file['title']}")
                print(f"URI: {file['uri']}")
                
                # Show a preview of the content (first 300 chars)
                content_preview = file["content"][:300] + "..." if len(file["content"]) > 300 else file["content"]
                print(f"\nContent Preview:\n{content_preview}")
        else:
            print(f"Error: {result['message']}")

if __name__ == "__main__":
    # Check if MANIM_RAG_CORPUS is set
    if not os.environ.get("MANIM_RAG_CORPUS"):
        print("Warning: MANIM_RAG_CORPUS environment variable is not set.")
        print("Please set this variable in the .env file before running this script.")
        exit(1)
    
    test_rag_query() 