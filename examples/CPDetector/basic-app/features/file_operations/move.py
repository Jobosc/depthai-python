"""
This module provides functions to move data from temporary storage to main storage.

It defines functions to list files to move and move data from temporary storage to main storage.

Functions:
    list_files_to_move: Lists all files in the temporary path that need to be moved.
    move_data_from_temp_to_main_storage: Moves data from the temporary storage to the main storage and deletes the temporary recordings.
"""

import shutil
from multiprocessing import Pool, cpu_count
from typing import List

from features.file_operations.delete import delete_temporary_recordings
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

    files_to_move = []
    for root, directory, files in os.walk(os.path.join(temporary_path, day)):
        for dir in directory:
            os.makedirs(os.path.join(destination_path, dir), exist_ok=True)
        for file in files:
            norm_path = os.path.normpath(root)
            folder = os.path.basename(norm_path)
            src_file = os.path.join(root, file)
            dest_file = os.path.join(destination_path, folder, file)
            files_to_move.append((src_file, dest_file))

    with Pool(processes=cpu_count()) as pool:
        for _ in pool.imap(__move_file, files_to_move):
            yield True

    participant.store_participant_metadata(os.path.join(storage_path, day, folder_id))
    delete_temporary_recordings()


def __move_file(args: tuple) -> None:
    src_file, dest_file = args
    shutil.copy2(src_file, dest_file)
    logging.debug(f"Moved file: {src_file} to {dest_file}")
