# Example usage of the RAG agent with import

from rag import query_rag_agent
import os
from dotenv import load_dotenv

def test_standard_rag():
    """Test the standard RAG agent with default corpus."""
    question = "How can I create a graph animation in Manim?"
    result = query_rag_agent(question)
    
    print("=== RAG Agent Response ===")
    print(result['response'])
    print("\n=== Retrieved Files ===")
    print(f"Total files retrieved: {len(result['retrieved_files'])}")
    
    # Print first file as example
    if result['retrieved_files']:
        first_file = result['retrieved_files'][0]
        print(f"\nTitle: {first_file['title']}")
        print(f"URI: {first_file['uri']}")
        print(f"Content Preview: {first_file['content'][:200]}...")

def test_manim_rag():
    """Test the RAG agent with Manim corpus."""
    # Load environment variables to access MANIM_RAG_CORPUS
    load_dotenv()
    
    question = "How can I create a sine wave animation in Manim?"
    manim_rag_corpus = os.environ.get("MANIM_RAG_CORPUS")
    
    if not manim_rag_corpus:
        print("Error: MANIM_RAG_CORPUS environment variable is not set")
        return
    
    result = query_rag_agent(question, manim_rag_corpus)
    
    print("=== Manim RAG Agent Response ===")
    print(result['response'])
    print("\n=== Retrieved Manim Files ===")
    print(f"Total files retrieved: {len(result['retrieved_files'])}")
    
    # Print first file as example
    if result['retrieved_files']:
        first_file = result['retrieved_files'][0]
        print(f"\nTitle: {first_file['title']}")
        print(f"URI: {first_file['uri']}")
        print(f"Content Preview: {first_file['content'][:200]}...")

if __name__ == "__main__":
    # Test standard RAG agent
    test_standard_rag()
    
    print("\n" + "="*50 + "\n")
    
    # Test Manim-specific RAG agent
    test_manim_rag() 