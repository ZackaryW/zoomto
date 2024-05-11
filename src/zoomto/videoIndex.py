from functools import cache
import os
from moviepy.editor import VideoFileClip

def create_thumbnail(video_path, output_path, time_sec = 1):
    """
    Creates a thumbnail for a video at the specified time.

    Args:
    video_path (str): Path to the video file.
    time_sec (float): Time in seconds to extract the thumbnail.
    output_path (str): Path to save the thumbnail image.
    """
    # Load the video file
    clip = VideoFileClip(video_path)

    # Get the frame at the specified time
    frame = clip.get_frame(time_sec)

    # Save the frame as an image
    from PIL import Image
    image = Image.fromarray(frame)
    image.save(output_path)


def generate_thumbnails():
    
    os.makedirs("thumbnails", exist_ok=True)
    for file in os.listdir(os.getcwd()):
        if os.path.splitext(file)[1] not in [".mp4", ".mkv", ".mov", ".avi", ".webm"]:
            continue
        
        if os.path.exists(os.path.join("thumbnails", file + ".jpg")):
            continue
        create_thumbnail(file, os.path.join("thumbnails", file + ".jpg"))

@cache
def get_videos():
    ret = []
    for i, file in enumerate(os.listdir(os.getcwd())):
        if os.path.splitext(file)[1] in [".mp4", ".mkv", ".mov", ".avi", ".webm"]:
            ret.append({
                "id": i,
                "title": file,
                # resize
                "thumbnail": f"local/thumbnails/{ file + ".jpg"}",
            })

    return ret

