# backend/video_generator.py

import os
import logging
from moviepy import *
async def generate_video(article_id, character_attire, input_language, output_language, summary):
    """Generate a video from the summary text."""
    try:
        # Example: Create a simple video with the summary text
        # Customize this function based on your video generation requirements

        # Create a text clip
        txt_clip = TextClip(summary, fontsize=24, color='white', size=(1280, 720), method='caption')
        txt_clip = txt_clip.set_duration(10)  # 10 seconds

        # Create a background clip (e.g., solid color)
        background = TextClip(" ", fontsize=24, color='white', size=(1280, 720), bg_color='black').set_duration(10)

        # Composite the text over the background
        video = CompositeVideoClip([background, txt_clip])

        # Define video path
        video_dir = "backend/static/videos"
        os.makedirs(video_dir, exist_ok=True)
        video_filename = f"video_{article_id}.mp4"
        video_path = os.path.join(video_dir, video_filename)

        # Write the video file
        video.write_videofile(video_path, fps=24, codec='libx264')

        return video_filename
    except Exception as e:
        logging.error(f"Video generation failed: {e}")
        raise e
