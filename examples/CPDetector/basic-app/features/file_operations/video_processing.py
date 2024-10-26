import logging
import os
import shutil
import subprocess

from features.modules.participant import read_participant_metadata
from features.modules.time_window import TimeWindow
from utils.parser import ENVParser


def convert_individual_videos(day, person):
    env = ENVParser()
    file_extension = [".hevc", ".mp4"]
    input_path = str(os.path.join(env.main_path, env.temp_path, day, person))
    input_files = []
    extensions = []
    file_normpaths = []

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


    ## Outputfiles
    metadata = read_participant_metadata(day, person)
    destination_path = os.path.join(input_path, "sessions")

    # Prepare output folder
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    logging.debug("Prepared output folder for converted files.")

    # Convert all files
    for idx, input_file in enumerate(input_files):
        for idx2, time_window in enumerate(metadata.timestamps.time_windows):
            output_file = os.path.join(destination_path, f"Gait_Cycle_{idx}_{idx2}.mp4")
            yield convert_videos(input_file=input_file, output_file=output_file, time_window=time_window)
    logging.debug("All files have been converted.")


def convert_videos(input_file: str, output_file: str, time_window: TimeWindow = None):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", str(__format_timedelta(time_window.start_seconds)),
        "-t", str(__format_timedelta(time_window.end_seconds - time_window.start_seconds)),
        "-c:v", "libx264",
        output_file
    ]
    subprocess.run(command)
    logging.debug(f"Completed conversion for: {input_file}")
    return True


def __format_timedelta(seconds: int) -> str:
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
