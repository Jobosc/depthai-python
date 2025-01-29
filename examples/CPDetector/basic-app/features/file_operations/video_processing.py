"""
This module provides functions to process and convert video files.

It defines functions to convert individual videos and format time differences.

Functions:
    convert_individual_videos: Converts individual video files for a specific day and person.
    convert_videos: Converts a video file based on the specified time window.
    __format_timedelta: Helper function to format a timedelta object into a string.
"""

import os
from datetime import datetime
import logging
import subprocess

import cv2
import numpy as np

from utils.parser import ENVParser

env = ENVParser()


def convert_npy_files_to_video(path_of_frames: str, subfolder: str, output_name: str, depth: bool) -> bool:
    subfolder_path = os.path.join(path_of_frames, subfolder)
    if os.path.isdir(subfolder_path):
        npy_files = [f for f in os.listdir(subfolder_path) if f.endswith('.npy')]
        npy_files.sort(key=lambda x: datetime.strptime(x.split('.')[0], "%Y%m%d_%H%M%S%f"))
        # Calculate FPS from timestamps
        timestamps = [datetime.strptime(f.split('.')[0], "%Y%m%d_%H%M%S%f") for f in npy_files]
        time_diffs = [(timestamps[i] - timestamps[i - 1]).total_seconds() for i in range(1, len(timestamps))]
        avg_time_diff = sum(time_diffs) / len(time_diffs)
        fps = 1 / avg_time_diff if avg_time_diff > 0 else 30  # Default to 30 FPS if avg_time_diff is 0

        print(f"Number of FPS: {fps}")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID'

        # Write each frame to the video
        try:
            path = os.path.join(path_of_frames, "..", f"{output_name}.mp4")
            frame = np.load(os.path.join(subfolder_path, npy_files[0]))
            if depth:
                height, width = frame.shape
                video = cv2.VideoWriter(path, fourcc, fps, (width, height), isColor=True)

                for npy_file in npy_files:
                    frame = np.load(os.path.join(subfolder_path, npy_file))
                    frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                    map_frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
                    video.write(map_frame)
            else:
                height, width, channel = frame.shape
                video = cv2.VideoWriter(path, fourcc, fps, (width, height), isColor=True)

                for npy_file in npy_files:
                    frame = np.load(os.path.join(subfolder_path, npy_file))
                    video.write(frame)

            video.release()
            convert_videos(path, os.path.join(path_of_frames, "..", f"{output_name}_{subfolder}.mp4"))
            os.remove(path)
            print("Video conversions complete.")
        except EOFError:
            pass

    return True

def convert_videos(input_file: str, output_file: str) -> bool:
    """
    Converts a video file based on the specified time window.

    Args:
        input_file (str): The path to the input video file.
        output_file (str): The path to the output video file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """

    command = ["ffmpeg", "-i", input_file, "-c:v", "libx264", output_file, "-y"]
    subprocess.run(command)
    logging.debug(f"Completed conversion for: {input_file}")
    return True


def convert_individual_videos(day, person):
    """
    Converts individual video files for a specific day and person.

    Args:
        day (str): The day of the video files to be converted.
        person (str): The person whose video files are to be converted.

    Yields:
        bool: True if the conversion was successful, False otherwise.
    """
    input_path = str(os.path.join(env.main_path, env.temp_path, day, person))

    # Create videos before conversion
    for subfolder in os.listdir(os.path.join(input_path, "depth_frames")):
        yield convert_npy_files_to_video(os.path.join(input_path, "depth_frames"), subfolder, "depth", True)
    for subfolder in os.listdir(os.path.join(input_path, "rgb_frames")):
        yield convert_npy_files_to_video(os.path.join(input_path, "rgb_frames"), subfolder, "rgb", False)


if "__main__" == __name__:
    convert_npy_files_to_video(
        "/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20250128/depth_frames", "depth",
        True)
    convert_npy_files_to_video(
        "/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20250128/rgb_frames", "rgb", False)
