# Manim Animation Agent

This agent creates beautiful animations using Manim, a mathematical animation library for Python. 

## Features

- Takes a text prompt describing what animation to create
- Automatically plans and creates multiple animation scenes
- Uses Google's Gemini AI for decision-making
- Handles the entire process from prompt to final animation
- Includes auto-debugging capabilities to fix code errors
- Generates narration scripts for each scene
- Provides a streaming API endpoint for real-time progress updates

## Requirements

- Python 3.8+
- Manim and its dependencies (Cairo, ffmpeg, etc.)
- Google Gemini API key

## Installation

1. Clone this repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Set up the Gemini API key:

```bash
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Command Line

Run the agent with a prompt describing the animation you want to create:

```bash
python main.py --prompt "Create an animation that shows a bouncing ball with realistic physics" --output-dir output --file-name animation
```

#### Command-line Arguments

- `--prompt`: Text prompt describing the animation to create (required)
- `--output-dir`: Directory to store output files (default: "output")
- `--file-name`: Base name for the final animation file (default: "animation")
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR; default: INFO)

### API Server

Start the API server:

```bash
python agent.py
```

This starts a FastAPI server on port 2222 with the following endpoints:

#### Endpoints

- `POST /generate`: Generate a Manim animation
  - Request body:
    ```json
    {
      "prompt": "Create an animation showing a bouncing ball with physics",
      "output_dir": "output",
      "file_name": "animation"
    }
    ```
  - Returns a Server-Sent Events (SSE) stream with real-time progress updates

- `GET /health`: Health check endpoint

#### Example API Usage

Using `curl` to make a request and stream the results:

```bash
curl -N -H "Content-Type: application/json" \
     -d '{"prompt": "Create an animation showing a bouncing ball with physics"}' \
     http://localhost:2222/generate
```

Using JavaScript:

```javascript
const eventSource = new EventSource('/generate');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Close the connection when done
eventSource.addEventListener('complete', () => {
  eventSource.close();
});
```

## How It Works

1. **Initialization**: The agent analyzes the prompt and plans the animation scenes.
2. **Scene Planning**: For each scene, the agent:
   - Plans the scene in detail
   - Researches how to implement it (if needed)
   - Creates Manim code
   - Executes and tests the code
   - Fixes any errors automatically
3. **Final Output**: After all scenes are created, a script is generated to stitch them together.

## Project Structure

- `main.py`: Entry point for the command-line interface
- `agent.py`: FastAPI server for the API interface
- `flow.py`: Defines the workflow using minLLM
- `nodes.py`: Contains the nodes for each step in the process
- `services/llm.py`: Interface to Google's Gemini API
- `tools/`: Various tools used by the agent:
  - `rag_tools.py`: Research tools
  - `file_tools.py`: File manipulation tools
  - `code_execution_tools.py`: Code execution and testing tools

## License

MIT 