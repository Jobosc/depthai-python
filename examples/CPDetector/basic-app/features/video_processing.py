import os
import shutil

import ffmpeg

from features.functions import read_participant_metadata
from features.modules.time_window import TimeWindow
from utils.parser import ENVParser


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

    ## Outputfiles
    metadata = read_participant_metadata(day, person)
    destination_path = os.path.join(input_path, "sessions")
    
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    for idx, input_file in enumerate(input_files):
        for idx2, time_window in enumerate(metadata.timestamps.time_windows):
            output_file = os.path.join(destination_path, f"Gait_Cycle_{idx}_{idx2}.mp4")
            yield convert_videos(input_file=input_file, output_file=output_file, time_window=time_window)


def convert_videos(input_file: str, output_file: str, time_window: TimeWindow = None):
    try:
        input_file = ffmpeg.input(input_file)
        if time_window:
            output_file = ffmpeg.output(
                input_file.trim(start_frame=time_window.start_frame, end_frame=time_window.end_frame), output_file,
                vcodec='libx264')
        else:
            output_file = ffmpeg.output(input_file, output_file, vcodec='libx264')
        ffmpeg.run(output_file)
        print(f"Conversion successful! File saved as {output_file}")
        return True
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr()}")
        return True
