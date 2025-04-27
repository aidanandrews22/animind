#!/usr/bin/env python3
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

from google.auth import default
import vertexai
from vertexai.preview import rag
import os
import glob
from dotenv import load_dotenv, set_key
import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )

# Configure corpus name and description
CORPUS_DISPLAY_NAME = "Manim_Documentation_Corpus"
CORPUS_DESCRIPTION = "Corpus containing Manim documentation and plugin documentation"

# Path to data directory (relative to this script)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

# Path to .env file
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.pdf', '.md', '.txt', '.py', '.html', '.ipynb', '.rst', '.json']


# --- Start of the script ---
def initialize_vertex_ai():
    """Initialize Vertex AI with project and location."""
    credentials, _ = default()
    vertexai.init(
        project=PROJECT_ID, location=LOCATION, credentials=credentials
    )


def delete_existing_corpus():
    """Delete existing corpus with the same display name if it exists."""
    print(f"Checking for existing corpus with display name '{CORPUS_DISPLAY_NAME}'...")
    existing_corpora = rag.list_corpora()
    for corpus in existing_corpora:
        if corpus.display_name == CORPUS_DISPLAY_NAME:
            print(f"Found existing corpus '{CORPUS_DISPLAY_NAME}' with ID '{corpus.name}'. Deleting...")
            try:
                corpus.delete()
                print(f"Successfully deleted corpus '{CORPUS_DISPLAY_NAME}'")
            except Exception as e:
                print(f"Error deleting corpus: {e}")
            break


def create_new_corpus():
    """Creates a new corpus."""
    print(f"Creating new corpus '{CORPUS_DISPLAY_NAME}'...")
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )
    
    try:
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config,
        )
        print(f"Successfully created corpus '{CORPUS_DISPLAY_NAME}' with ID '{corpus.name}'")
        return corpus
    except Exception as e:
        print(f"Error creating corpus: {e}")
        return None


def find_all_files(directory, extensions=None):
    """Find all files in directory with given extensions."""
    all_files = []
    
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS
    
    for ext in extensions:
        # Use recursive glob to find all files with the extension
        pattern = os.path.join(directory, '**', f'*{ext}')
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
    
    # Filter out hidden files and directories (starting with .)
    all_files = [f for f in all_files if not any(part.startswith('.') for part in f.split(os.sep))]
    
    print(f"Found {len(all_files)} files with extensions {extensions}")
    return all_files


def upload_file_to_corpus(corpus_name, file_path, display_name=None, description=None):
    """Uploads a file to the specified corpus."""
    if display_name is None:
        display_name = os.path.basename(file_path)
    
    if description is None:
        relative_path = os.path.relpath(file_path, DATA_DIR)
        description = f"File from {relative_path}"
    
    print(f"Uploading {display_name} to corpus...")
    try:
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=file_path,
            display_name=display_name,
            description=description,
        )
        print(f"Successfully uploaded {display_name} to corpus")
        return rag_file
    except Exception as e:
        print(f"Error uploading file {display_name}: {e}")
        return None


def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")


def list_corpus_files(corpus_name):
    """Lists files in the specified corpus."""
    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"Total files in corpus: {len(files)}")
    for file in files:
        print(f"File: {file.display_name} - {file.name}")


def main():
    print(f"Data directory: {DATA_DIR}")
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Delete existing corpus if it exists
    delete_existing_corpus()
    
    # Create a new corpus
    corpus = create_new_corpus()
    if corpus is None:
        print("Failed to create corpus. Exiting.")
        return
    
    # Update the .env file with the corpus name
    update_env_file(corpus.name, ENV_FILE_PATH)
    
    # Find all files in the data directory
    all_files = find_all_files(DATA_DIR)
    
    # Upload all files to the corpus
    successful_uploads = 0
    failed_uploads = 0
    
    for file_path in all_files:
        relative_path = os.path.relpath(file_path, DATA_DIR)
        display_name = os.path.basename(file_path)
        description = f"File from {relative_path}"
        
        result = upload_file_to_corpus(
            corpus_name=corpus.name,
            file_path=file_path,
            display_name=display_name,
            description=description
        )
        
        if result:
            successful_uploads += 1
        else:
            failed_uploads += 1
    
    print(f"Upload summary: {successful_uploads} successful, {failed_uploads} failed")
    
    # List all files in the corpus
    list_corpus_files(corpus_name=corpus.name)


if __name__ == "__main__":
    main() 