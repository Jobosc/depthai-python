import os
import shutil

import subprocess

from features.functions import read_participant_metadata
from features.modules.time_window import TimeWindow
from utils.parser import ENVParser
import logging


def convert_individual_videos(day, person):
    env = ENVParser()
    input_path = os.path.join(env.main_path, env.temp_path, day, person)
    input_files = []

    ## Inputfiles
    # Collect all video material files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext == ".hevc":
                input_files.append(os.path.join(root, file))
    logging.debug("All input files have been collected.")

    ## Outputfiles
    metadata = read_participant_metadata(day, person)
    destination_path = os.path.join(input_path, "sessions")
    
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    logging.debug("Prepared output folder for converted files.")

    for idx, input_file in enumerate(input_files):
        for idx2, time_window in enumerate(metadata.timestamps.time_windows):
            output_file = os.path.join(destination_path, f"Gait_Cycle_{idx}_{idx2}.mp4")
            yield convert_videos(input_file=input_file, output_file=output_file, time_window=time_window)
    logging.debug("All files have been converted.")


def convert_videos(input_file: str, output_file: str, time_window: TimeWindow = None):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", str(format_timedelta(time_window.start_seconds)),
        "-t", str(format_timedelta(time_window.end_seconds - time_window.start_seconds)),
        "-c:v", "libx264",
        output_file
    ]
    subprocess.run(command)
    logging.debug(f"Completed conversion for: {input_file}")
    return True

def format_timedelta(seconds: int) -> str:
    """
    Convert seconds into a string in the format HH:MM:SS.

    Args:
    seconds (int): The seconds to format.

    Returns:
    str: The formatted string in HH:MM:SS format.
    """
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"