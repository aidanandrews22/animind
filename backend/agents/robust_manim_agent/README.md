# Robust Manim Agent

A robust agent for generating high-quality Manim animations using Google's Agent Development Kit (ADK).

## Overview

This agent uses a loop-based approach to iteratively refine Manim code until it produces a working animation. The workflow follows these steps:

1. Generate initial Manim code based on a user prompt
2. Execute the code and capture the results
3. Critique the execution results to identify errors
4. Refine the code based on critique
5. Repeat steps 2-4 until the code works correctly

The loop stops when either:
- The code runs successfully without errors
- The maximum number of iterations is reached (default: 5)

## Architecture

The agent is built using ADK's workflow agents:

- `SequentialAgent`: Coordinates the overall process
- `LoopAgent`: Manages the iterative refinement process
- `LlmAgent`: Individual components handling generation, execution, critique, and refinement

## Setup

### Prerequisites

- Python 3.9 or higher
- Manim animation library
- Google ADK

### Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
export MANIM_RAG_CORPUS="your-rag-corpus-id"
```

## Usage

```python
from robust_manim_agent.agent import generate_manim_animation

# Generate a Manim animation from a prompt
result = generate_manim_animation(
    prompt="Create an animation that demonstrates a sine wave transforming into a cosine wave."
)

# The result contains the final code and execution details
final_code = result["code"]
execution_result = result["execution_result"]
iteration_count = result["iterations"]

# Save the final code to a file
with open("output.py", "w") as f:
    f.write(final_code)
```

See `example_usage.py` for a complete example.

## Tools

The agent provides several tools:

- **File Tools**: Create, read, and edit files
- **Code Execution Tools**: Run Manim code and analyze execution results
- **RAG Tools**: Query a retrieval-augmented generation system for Manim documentation and examples

## Customization

You can customize the agent by:

- Changing the `GEMINI_MODEL` to use different LLM capabilities
- Modifying the `max_iterations` in the `LoopAgent` to allow more refinement cycles
- Adjusting the agent instructions to prioritize different aspects of animation quality

## License

This project is licensed under the terms specified in the parent project.

## Acknowledgments

- Google Agent Development Kit (ADK)
- Manim animation library
- RAG system for Manim documentation retrieval 