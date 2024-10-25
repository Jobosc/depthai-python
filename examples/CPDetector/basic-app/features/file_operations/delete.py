import logging
import os
import shutil

from . import temporary_path, storage_path


def __delete_files_and_folders_in_path(path: str) -> bool:
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

def delete_temporary_recordings() -> bool:
    return __delete_files_and_folders_in_path(temporary_path)


def delete_person_on_day_folder(day: str, person: str) -> bool:
    folder = os.path.join(storage_path, day, person)
    __delete_files_and_folders_in_path(folder)
    try:
        root_folder = os.path.dirname(folder)
        if len(os.listdir(root_folder)) == 0:
            shutil.rmtree(root_folder)
        return True
    except:
        return False