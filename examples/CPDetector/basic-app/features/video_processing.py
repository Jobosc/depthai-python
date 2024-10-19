import datetime
import ffmpeg
import os

from utils.parser import ENVParser



def convert_videos(input_file, output_file):
    try:
        ffmpeg.input(input_file).output(output_file, vcodec='libx264').run()
        print(f"Conversion successful! File saved as {output_file}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")

def convert_individual_videos(day, person):
    env = ENVParser()
    file_extension = [".hevc", ".mp4"]
    input_path = os.path.join(env.main_path, env.temp_path, day, person)
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

    # Find all files with existent mp4s which already have a hvec
    list_of_duplicate_mp4s = []
    for idx, file_np in enumerate(file_normpaths):
        index = None
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
    timestamp = datetime.datetime.now()
    time_string = timestamp.strftime("%Y%m%d%H%M")
    for input_file in input_files:
        base, _ = os.path.splitext(input_file)
        output_file = f"{base}_{time_string}.mp4"
        print(input_file, output_file)

    convert_videos(input_file=input_file, output_file=output_file)