import os
import subprocess
import io
from loguru import logger

@logger.catch()
def apply_blur_effect(input_file, output_file, strength, applies):
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
        # Construct the FFmpeg command
        ffmpeg_command = f'ffmpeg -i {input_file} -vf "boxblur={strength}:1" -c:a copy {output_file} -y'

        # Execute the FFmpeg command using subprocess
        subprocess.run(ffmpeg_command, check=True, shell=True)

        # Read the resulting video file data
        with open(output_file, 'rb') as f:
            video_data = f.read()
        os.remove(input_file)
        os.remove(output_file)
        return io.BytesIO(video_data)

    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg command failed with return code {e.returncode}.")
        return None


