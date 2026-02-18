from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
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
            image_clip = ImageClip(img_path).set_duration(duration)
            image_clip = image_clip.set_audio(audio_clip)
            
            # Optional: Add fadein for smooth transitions
            image_clip = image_clip.fadein(0.5)
            
            clips.append(image_clip)
            
        if not clips:
            print("No clips created.")
            return None
            
        # Concatenate all clips
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Debug: Check ffmpeg binary
        import imageio_ffmpeg
        print(f"ffmpeg binary found at: {imageio_ffmpeg.get_ffmpeg_exe()}")

        # Write to file (MP4)
        print(f"Writing video to {output_path}...")
        
        # Define temp audio path to avoid permission issues
        temp_audio = "temp_audio_for_video.m4a"
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac', 
            preset='ultrafast', 
            threads=2,  # Reduced for cloud environment
            logger='bar',
            temp_audiofile=temp_audio,
            remove_temp=True
        )
        
        # Clean up clips to free memory
        for clip in clips:
            clip.close()
        final_video.close()
        
        return output_path
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return None
