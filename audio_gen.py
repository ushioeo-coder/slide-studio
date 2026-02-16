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
        # Streamlit runs its own event loop, so asyncio.run() may fail.
        # Use a new event loop in a thread-safe manner instead.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside an existing event loop (Streamlit Cloud)
            # Create a new loop in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(asyncio.run, _generate_audio_async(text, output_path, voice)).result()
        else:
            # No running loop, safe to use asyncio.run()
            asyncio.run(_generate_audio_async(text, output_path, voice))
        
        return os.path.exists(output_path)
    except Exception as e:
        print(f"Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False
