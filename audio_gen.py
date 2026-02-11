import edge_tts
import asyncio
import os

async def _generate_audio_async(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_audio(text, output_path, voice="ja-JP-NanamiNeural"):
    """
    Generates audio from text using Microsoft Edge TTS (high quality neural voices).
    
    Args:
        text (str): script text to speak
        output_path (str): path to save the .mp3 file
        voice (str): Voice ID (e.g. "ja-JP-NanamiNeural", "ja-JP-KeitaNeural")
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        asyncio.run(_generate_audio_async(text, output_path, voice))
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False
