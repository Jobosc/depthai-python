"""
This module provides functions to delete temporary recordings and specific folders.

It defines functions to delete temporary recordings, delete a person's folder on a specific day, and delete files and folders in a given path.

Functions:
    delete_person_on_day_folder: Deletes a person's folder on a specific day.
    delete_temporary_recordings: Deletes all files and folders in the temporary path.
    __delete_files_and_folders_in_path: Deletes all files and folders in a given path.
"""

import shutil

from . import os, logging, storage_path, temporary_path


def delete_temporary_recordings() -> bool:
    """
    Deletes all files and folders in the temporary path.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    return __delete_files_and_folders_in_path(temporary_path)


def delete_person_on_day_folder(day: str, person: str) -> bool:
    """
    Deletes a person's folder on a specific day.

    Args:
        day (str): The day of the folder to be deleted.
        person (str): The person whose folder is to be deleted.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    folder = os.path.join(storage_path, day, person)
    __delete_files_and_folders_in_path(folder)
    try:
        root_folder = os.path.dirname(folder)
        if len(os.listdir(root_folder)) == 0:
            shutil.rmtree(root_folder)
        return True
    except:
        return False


def __delete_files_and_folders_in_path(path: str) -> bool:
    """
    Helper function which deletes all files and folders in a given path.

    Args:
        path (str): The path to delete files and folders from.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    try:
        # Delete files
        for root, dirs, files in os.walk(path):
            for file in files:
                logging.debug(os.path.join(root, file))
                os.remove(os.path.join(root, file))
        # Delete folders
        shutil.rmtree(path)
        logging.debug(f"Deleting folder content in: {path} was successful")
        return True
    except:
        return False
