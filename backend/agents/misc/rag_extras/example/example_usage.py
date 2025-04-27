#!/usr/bin/env python3
"""
Example usage of the Manim video generation agent.
This script demonstrates how to use the agent to generate a simple animation.
"""

import os
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the manim module
sys.path.append(str(Path(__file__).parent.parent.parent))

from manim_agent.local.main import generate_manim_video

# Example prompt for a simple animation
PROMPT = """
Create a Manim animation that demonstrates the Pythagorean theorem.
The animation should:
1. Start with a right-angled triangle with sides a, b, and hypotenuse c
2. Construct squares on each side of the triangle
3. Show that the area of the square on the hypotenuse equals the sum of areas of squares on the other two sides
4. Use bright colors and smooth animations
5. Include appropriate mathematical text labels

Use a = 3, b = 4, and c = 5 for the triangle dimensions.
"""

# Example narration script
NARRATION_SCRIPT = """
The Pythagorean theorem is one of the most famous theorems in mathematics.
It states that in a right-angled triangle, the square of the length of the hypotenuse equals the sum of squares of the other two sides.
Let's visualize this with a triangle where a = 3, b = 4, and c = 5.
First, we draw the triangle.
Then, we construct squares on each side.
The area of the square on side a is a² = 9.
The area of the square on side b is b² = 16.
The area of the square on the hypotenuse c is c² = 25.
We can see that a² + b² = c², or 9 + 16 = 25.
This visual proof shows why the Pythagorean theorem works.
"""

def main():
    """Run the example to generate a Manim video."""
    # Set up output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "pythagorean")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the video
    print(f"Generating Manim video in {output_dir}...")
    result = generate_manim_video(
        prompt=PROMPT,
        narration_script=NARRATION_SCRIPT,
        output_dir=output_dir
    )
    
    # Print the result
    print("\nGeneration completed!")
    print(json.dumps(result, indent=2))
    
    print(f"\nCheck {output_dir} for the generated video and code.")

if __name__ == "__main__":
    main() 