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
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root
from google.adk.tools import FunctionTool

from .tools.file import create_file, read_file, edit_file
from .tools.rag import rag_query

load_dotenv()

root_agent = Agent(
    model='gemini-2.5-pro-preview-03-25',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        FunctionTool(
            func=rag_query,
        ),
        FunctionTool(
            func=create_file,
        ),
        FunctionTool(
            func=read_file,
        ),
        FunctionTool(
            func=edit_file,
        )
    ]
)