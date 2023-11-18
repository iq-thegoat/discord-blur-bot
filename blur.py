import os
import subprocess
import io
from loguru import logger
import re
from PIL import Image, ImageFilter


def calculate_percentage(frame, total_frames):
    return (frame / total_frames) * 100


from moviepy.editor import VideoFileClip

def get_total_frames(input_file):
    try:
        # Open the video file
        clip = VideoFileClip(input_file)

        # Get the total number of frames
        total_frames = int(clip.fps * clip.duration)

        # Close the video clip
        clip.close()
        print(str("TOTALFRAMES " + str(total_frames)))
        return total_frames

    except Exception as e:
        raise ValueError(f"Unable to get total frames from the input video. Error: {e}")




def apply_blur_effect(input_file, output_file, strength):

    """
    Apply a blur effect to a video file using FFmpeg.

    Parameters:
    - input_file (str): Path to the input video file.
    - output_file (str): Path to the output video file.
    - strength (int): Strength of the blur effect.
    - applies (int): Number of times the blur effect is applied.

    Returns:
    - str: Data of the resulting video file.
    """

    try:
        total_frames = get_total_frames(input_file)
        # Construct the FFmpeg command
        ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"gblur=sigma={strength}",
        "-c:a", "copy",
        output_file,
        "-y"
        ]

        # Execute the FFmpeg command using subprocess
        process= subprocess.Popen(ffmpeg_command,stderr=subprocess.PIPE,universal_newlines=True)

        # Regular expression to extract progress information
        progress_regex = re.compile(r"frame=\s*(\d+)\s*fps=\s*([\d.]+)\s*q=\s*([\d.]+)\s*L?size=\s*([\d.]+[kKmMgG]?)\s*")

        while True:
            line = process.stderr.readline()
            if not line:
                break
            match = progress_regex.search(line)
            if match:
                frame = int(match.group(1))
                percentage = calculate_percentage(frame,total_frames=total_frames)
                yield percentage

        # Wait for the process to complete
        process.wait()

        # Read the resulting video file data
        with open(output_file, 'rb') as f:
            video_data = f.read()
        os.remove(input_file)
        os.remove(output_file)
        yield io.BytesIO(video_data)

    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg command failed with return code {e.returncode}.")
        return None



def apply_blur_effect_img(input_path,radius=2):
    # Open the image file
    img = Image.open(input_path)

    # Convert the image to RGB mode if it's in RGBA mode
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Apply Gaussian blur
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius))

    output_bytesio = io.BytesIO()
    blurred_img.save(output_bytesio, format='JPEG')

    # Set the file pointer to the beginning of the BytesIO object
    output_bytesio.seek(0)

    return output_bytesio
