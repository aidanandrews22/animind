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

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

load_dotenv()

ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in your own rag corpus
            # here is a sample rag coprus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model='gemini-2.5-flash-preview-04-17',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        ask_vertex_retrieval,
    ]
)

# Function to query the RAG agent and return both the response and retrieved files
def query_rag_agent(question, rag_corpus_override=None):
    """
    Query the RAG agent and return both the generated response and retrieved files.
    
    Args:
        question (str): The query to send to the RAG agent
        rag_corpus_override (str, optional): Override the RAG corpus with a different one
    
    Returns:
        dict: A dictionary containing the agent's response and the retrieved files
    """
    # Create a copy of the retrieval tool with the correct RAG corpus if override is provided
    if rag_corpus_override:
        retrieval_tool = VertexAiRagRetrieval(
            name='retrieve_rag_documentation',
            description=(
                'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
            ),
            rag_resources=[
                rag.RagResource(
                    rag_corpus=rag_corpus_override
                )
            ],
            similarity_top_k=10,
            vector_distance_threshold=0.6,
        )
        agent = Agent(
            model='gemini-2.5-flash-preview-04-17',
            name='ask_rag_agent',
            instruction=return_instructions_root(),
            tools=[
                retrieval_tool,
            ]
        )
    else:
        # Use the default agent
        agent = root_agent
    
    # Execute the agent with the question
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    # Create a session and runner for the agent
    session_service = InMemorySessionService()
    session_id = f"rag_session_{hash(question)}"
    user_id = "rag_user"
    app_name = "rag_app"
    session = session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    
    # Format the question as content for the runner
    content = types.Content(role='user', parts=[types.Part(text=question)])
    
    # Run the agent and collect events
    events = runner.run(user_id=user_id, session_id=session_id, new_message=content)
    
    # Process the response and tool calls
    response_text = ""
    retrieved_files = []
    
    for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
        elif event.is_tool_call():
            tool_call = event.tool_call
            if tool_call.name == 'retrieve_rag_documentation':
                for chunk in tool_call.output.get('chunks', []):
                    retrieved_files.append({
                        'title': chunk.get('title', ''),
                        'content': chunk.get('content', ''),
                        'uri': chunk.get('uri', ''),
                        'source': chunk.get('source', {})
                    })
    
    return {
        'response': response_text,
        'retrieved_files': retrieved_files
    }
