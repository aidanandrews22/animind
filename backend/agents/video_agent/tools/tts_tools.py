"""
Tools for Google Text-to-Speech functionality.
"""
import os
from typing import Dict, List, Any
from google.cloud import texttospeech
from google.adk.tools import FunctionTool

def generate_speech(text: str, 
                    output_path: str = "output.mp3", 
                    language_code: str = "en-US", 
                    voice_gender: str = "MALE",
                    audio_format: str = "MP3") -> Dict[str, Any]:
    """
    Generate speech from text using Google Cloud Text-to-Speech.
    
    Args:
        text: The text to convert to speech
        output_path: Path where the audio file will be saved
        language_code: Language code like "en-US"
        voice_gender: Voice gender (MALE, FEMALE, or NEUTRAL)
        audio_format: Audio format (MP3 or WAV)
        
    Returns:
        Dict with path to the generated audio file
    """
    # Map string parameters to enum values
    gender_map = {
        "MALE": texttospeech.SsmlVoiceGender.MALE,
        "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
        "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL
    }
    
    format_map = {
        "MP3": texttospeech.AudioEncoding.MP3,
        "WAV": texttospeech.AudioEncoding.LINEAR16
    }
    
    # Instantiate a client
    client = texttospeech.TextToSpeechClient()
    
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=gender_map.get(voice_gender, texttospeech.SsmlVoiceGender.NEUTRAL)
    )
    
    # Select the type of audio file
    audio_config = texttospeech.AudioConfig(
        audio_encoding=format_map.get(audio_format, texttospeech.AudioEncoding.MP3)
    )
    
    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # The response's audio_content is binary
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    
    return {
        "output_path": output_path,
        "duration_seconds": len(response.audio_content) / 1024.0 / 16.0,  # Rough estimate
        "success": True
    }

def get_tts_tools() -> List[FunctionTool]:
    """
    Get all TTS tools.
    
    Returns:
        List of TTS tools
    """
    return [
        FunctionTool(func=generate_speech)
    ] 