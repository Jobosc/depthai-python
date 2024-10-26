import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta

from features.modules.participant import read_participant_metadata
from features.modules.time_window import TimeWindow
from utils.parser import ENVParser

env = ENVParser()


def convert_individual_videos(day, person):
    file_extension = [".hevc", ".mp4"]
    input_path = str(os.path.join(env.main_path, env.temp_path, day, person))
    input_files = []
    extensions = []
    file_normpaths = []

    ## Outputfiles
    metadata = read_participant_metadata(day, person)

    ## Inputfiles
    # Collect all video material files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            _, ext = os.path.splitext(file)

            if ext in file_extension:
                name = os.path.join(root, file)

                # Save file parameters
                input_files.append(name)
                extensions.append(ext)

                # Save normpaths
                base, _ = os.path.splitext(name)
                file_normpaths.append(base)

                # Create output folder
                if os.path.exists(base):
                    shutil.rmtree(base)
                os.makedirs(base, exist_ok=True)
                logging.debug("Prepared output folder for converted files.")

    logging.debug("All input files have been collected.")

    # Find all files with existent mp4s which already have a hvec
    list_of_duplicate_mp4s = []
    for idx, file_np in enumerate(file_normpaths):
        index = file_normpaths[idx:].index(file_np)
        # In case of a duplicate file (without extension)
        if index:
            if extensions[index] == ".mp4":
                list_of_duplicate_mp4s.append(index)
            elif extensions[idx] == ".mp4":
                list_of_duplicate_mp4s.append(idx)

    # Remove all MP4s
    for i in sorted(list_of_duplicate_mp4s, reverse=True):
        del input_files[i]

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
    start_time = (time_window.start - time_start) + datetime.combine(datetime.min, env.video_delta_start) - datetime.min
    end_time = (time_window.end - time_window.start) + datetime.combine(datetime.min,
                                                                        env.video_delta_end) - datetime.min
    command = [
        "ffmpeg",
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
    Convert time_difference into a string in the format HH:MM:SS.mmm.

    Args:
    secotime_differenceds (timedelta): The time_difference to format.

    Returns:
    str: The formatted string in HH:MM:SS.mmm format.
    """
    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(time_difference.microseconds / 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
