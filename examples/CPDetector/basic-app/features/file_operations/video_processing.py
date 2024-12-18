"""
This module provides functions to process and convert video files.

It defines functions to convert individual videos and format time differences.

Functions:
    convert_individual_videos: Converts individual video files for a specific day and person.
    convert_videos: Converts a video file based on the specified time window.
    __format_timedelta: Helper function to format a timedelta object into a string.
"""

import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta

import cv2
import numpy as np

from features.modules.participant import read_participant_metadata
from features.modules.time_window import TimeWindow
from utils.parser import ENVParser

env = ENVParser()


def convert_npy_disparity_to_video(npy_file: str, output_file: str, fps: int = 30) -> None:
    # Load the .npy file
    data = np.load(npy_file)
    logging.debug("Numpy file with depth values has been loaded")

    # Get the dimensions of the frames
    num_frames, height, width = data.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID'
    output_video_path = output_file
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height), isColor=True)

    # Write each frame to the video
    logging.debug("Initialized the conversion of depth array to depth video.")
    for i in range(num_frames):
        frame = cv2.normalize(data[i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        map_frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
        video.write(map_frame)

    # Release the video writer object
    video.release()
    logging.debug("Depth video conversion complete.")


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
    input_files = []

    ## Output files
    metadata = read_participant_metadata(day, person)

    ## Input files
    # Collect all video material files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext == ".mp4":
                name = os.path.join(root, file)
                input_files.append(name)

                # Save normpaths
                base, _ = os.path.splitext(name)

                # Create output folder
                if os.path.exists(base):
                    shutil.rmtree(base)
                os.makedirs(base, exist_ok=True)
                logging.debug("Prepared output folder for converted files.")

    logging.debug("All input files have been collected.")

    # Convert all files
    for input_file in input_files:
        for idx, time_window in enumerate(metadata.timestamps.time_windows):
            output_folder = os.path.splitext(os.path.basename(input_file))[0]
            destination_path = os.path.join(input_path, output_folder)
            output_file = os.path.join(destination_path, f"{env.conversion_file_prefix}_{idx}.mp4")
            yield convert_videos(input_file=input_file, output_file=output_file,
                                 time_start=metadata.timestamps.camera_start, time_window=time_window)
    logging.debug("All files have been converted.")


def convert_videos(input_file: str, output_file: str, time_start: datetime, time_window: TimeWindow = None) -> bool:
    """
    Converts a video file based on the specified time window.

    Args:
        input_file (str): The path to the input video file.
        output_file (str): The path to the output video file.
        time_start (datetime): The start time of the video.
        time_window (TimeWindow, optional): The time window for the video conversion. Defaults to None.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    start_time = (time_window.start - time_start) + datetime.combine(datetime.min, env.video_delta_start) - datetime.min
    end_time = (time_window.end - time_window.start) + datetime.combine(datetime.min,
                                                                        env.video_delta_end) - datetime.min

    logging.info(f"Conversion start time: {start_time}; Conversion end time: {end_time}")
    command = [
        "ffmpeg",
        "-framerate", "30",
        "-i", input_file,
        "-ss", __format_timedelta(start_time),
        "-t", __format_timedelta(end_time),
        "-c:v", "libx264",
        output_file
    ]
    subprocess.run(command)
    logging.debug(f"Completed conversion for: {input_file}")
    return True


def __format_timedelta(time_difference: timedelta) -> str:
    """
    Helper function to format a timedelta object into a string.

    Args:
        time_difference (timedelta): The time difference to format.

    Returns:
        str: The formatted string in HH:MM:SS.mmm format.
    """
    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(time_difference.microseconds / 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


if "__main__" == __name__:
    convert_npy_disparity_to_video(
        "/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20241217/DepthFrames.npy",
        "/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20241217/output.mp4")
