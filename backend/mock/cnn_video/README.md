# CNN Video Tutorial with Manim

This project creates a comprehensive tutorial on Convolutional Neural Networks (CNNs) using the Manim animation library and Google Text-to-Speech for narration.

## Overview

The tutorial consists of 9 scenes that explain the key components of CNN architecture and operation:

1. **Title & Motivation** (Scene 1): Introduction to CNNs
2. **From Image to Matrix** (Scene 2): How images are represented as matrices
3. **Convolution Operation** (Scene 3): The core operation of CNNs
4. **Multiple Filters & Feature Maps** (Scene 4): Using different filters for feature detection
5. **Non-linearity & Activation** (Scene 5): Adding non-linearity with ReLU
6. **Pooling** (Scene 6): Downsampling with max pooling
7. **Stacking Layers** (Scene 7): Creating deep CNNs with multiple layers
8. **Flatten & Fully Connected** (Scene 8): Connecting to classification layers
9. **Training & Backprop** (Scene 9): How CNNs learn through backpropagation

## Requirements

- Python 3.7+
- Manim (Community Edition)
- manim-voiceover
- Google Cloud Text-to-Speech API
- FFmpeg (for combining videos)

## Setup

1. Make sure you have the required Python packages installed:
   ```
   pip install manim manim-voiceover google-cloud-texttospeech
   ```

2. Set up your Google Cloud credentials for Text-to-Speech:
   - The `.env` file should contain your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Rendering the Scenes

Each scene can be rendered individually:

```bash
# Render Scene 1
manim -pqh cnn_video/scene1_title.py TitleScene

# Or render all scenes
for i in {1..9}; do
    manim -pqh cnn_video/scene${i}_*.py
done
```

## Combining All Scenes

After rendering all scenes, you can combine them into a single video:

```bash
# Ensure the file_list.txt is generated
python cnn_video/main.py

# Combine all scenes using FFmpeg
ffmpeg -f concat -safe 0 -i cnn_video/file_list.txt -c copy cnn_video/full_cnn_video.mp4
```

## Customizing the Tutorial

- Each scene is defined in its own Python file, making it easy to modify or extend
- The `utils.py` file contains common functions and the base scene class
- You can adjust colors, timings, and animations in each scene file

## License

This project is open source and available under the MIT License. 