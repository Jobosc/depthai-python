"""
This module provides functions to move data from temporary storage to main storage.

It defines functions to list files to move and move data from temporary storage to main storage.

Functions:
    list_files_to_move: Lists all files in the temporary path that need to be moved.
    move_data_from_temp_to_main_storage: Moves data from the temporary storage to the main storage and deletes the temporary recordings.
"""

import shutil
from typing import List

from features.file_operations.delete import delete_temporary_recordings
from features.file_operations.video_processing import convert_npy_files_to_video
from features.modules.participant import Participant
from . import os, today, temporary_path, logging, storage_path


def list_files_to_move() -> List[str]:
    """
    Lists all files in the temporary path that need to be moved.

    Returns:
        List[str]: A list of file names that need to be moved.
    """
    all_files = []
    for _, _, files in os.walk(os.path.join(temporary_path, str(today))):
        for file in files:
            all_files.append(file)
    logging.debug(f"A list of {len(all_files)} files has been collected to be moved.")
    return all_files


def move_data_from_temp_to_main_storage(folder_id: str, participant: Participant, day: str = today):
    """
    Moves data from the temporary storage to the main storage and deletes the temporary recordings.

    Args:
        folder_id (str): The ID of the folder to move the data to.
        participant (Participant): The participant object containing metadata.
        day (str, optional): The day of the folder to move the data to. Defaults to today.
    """
    destination_path = os.path.join(storage_path, day, folder_id)
    os.makedirs(destination_path, exist_ok=True)

    # Create the disparity video before moving all files
    convert_npy_files_to_video(os.path.join(temporary_path, day, "depth_frames"), "depth.mp4", True)
    convert_npy_files_to_video(os.path.join(temporary_path, day, "rgb_frames"), "rgb.mp4", False)

    for root, _, files in os.walk(os.path.join(temporary_path, day)):
        for file in files:

            shutil.copy2(os.path.join(root, file), os.path.join(destination_path, file))  # Copy file
            logging.debug(
                f"Moving file: {os.path.join(root, file)} to {os.path.join(destination_path, file)} complete.")
            yield True
    participant.store_participant_metadata(os.path.join(storage_path, day, folder_id))

    delete_temporary_recordings()
