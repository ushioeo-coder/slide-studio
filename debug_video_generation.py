from moviepy import *
from PIL import Image, ImageDraw
from gtts import gTTS
import os
import time

def create_debug_assets():
    print("Creating dummy assets...")
    # Create dummy image
    img = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((100,100), "Debug Video", fill=(255,255,0))
    img.save("debug_img.png")
    
    # Create dummy audio
    tts = gTTS("これはテストです。動画生成のテストを行っています。", lang='ja')
    tts.save("debug_audio.mp3")
    print("Assets created: debug_img.png, debug_audio.mp3")

def run_test():
    try:
        if not os.path.exists("debug_img.png"):
            create_debug_assets()
            
        print("Initializing MoviePy clips...")
        audio_clip = AudioFileClip("debug_audio.mp3")
        duration = audio_clip.duration
        print(f"Audio duration: {duration}s")
        
        image_clip = ImageClip("debug_img.png").with_duration(duration)
        image_clip = image_clip.with_audio(audio_clip)
        
        output_path = "debug_output.mp4"
        print(f"Writing video to {output_path}...")
        
        start_time = time.time()
        image_clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac', 
            preset='ultrafast', 
            threads=4,
            logger='bar' 
        )
        end_time = time.time()
        
        print(f"Video generated successfully in {end_time - start_time:.2f} seconds!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
