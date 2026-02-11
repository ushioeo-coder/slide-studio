from moviepy import *
from PIL import Image
import os

def create_video(slides_data, output_path="output_video.mp4"):
    """
    Creates a video from a list of slides (image + audio).
    
    Args:
        slides_data (list): List of dicts, each containing:
            - 'image_path': path to the slide image (png/jpg)
            - 'audio_path': path to the narration audio (mp3)
        output_path (str): Path to save the final video.
        
    Returns:
        str: Path to the generated video file, or None if failed.
    """
    try:
        clips = []
        
        for slide in slides_data:
            img_path = slide['image_path']
            audio_path = slide['audio_path']
            
            if not os.path.exists(img_path) or not os.path.exists(audio_path):
                print(f"Missing asset for slide: {slide}")
                continue
                
            # Create Audio Clip
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create Image Clip with same duration
            # Resize logic can be added here if needed, but we assume 1920x1080
            image_clip = ImageClip(img_path).with_duration(duration)
            image_clip = image_clip.with_audio(audio_clip)
            
            # Optional: Add fadein/fadeout for smooth transitions
            image_clip = image_clip.with_effects([vfx.FadeIn(0.5)])
            
            clips.append(image_clip)
            
        if not clips:
            print("No clips created.")
            return None
            
        # Concatenate all clips
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Write to file (MP4)
        # Using 'ultrafast' preset for speed during generation
        # audio_codec='aac' is standard, but if it hangs, we can try leaving it or using 'libmp3lame'
        # temp_audiofile is required on some Windows systems to avoid permission errors
        # Write to file (MP4)
        print(f"Writing video to {output_path}...")
        
        # Using settings that were verified to work in debug script
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac', 
            preset='ultrafast', 
            threads=4,
            logger='bar'
        )
        
        return output_path
        
        return output_path
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return None
