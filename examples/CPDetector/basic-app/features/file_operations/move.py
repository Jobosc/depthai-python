import shutil
from typing import List

from features.modules.participant import Participant
from . import os, today, temporary_path, logging, storage_path, env


def list_files_to_move() -> List[str]:
    all_files = []
    for _, _, files in os.walk(os.path.join(temporary_path, str(today))):
        for file in files:
            all_files.append(file)
    logging.debug("Collected all the files that need to be moved.")
    return all_files


def move_data_from_temp_to_main_storage(
        temporary_folder: str, participant: Participant, day: str = today
):
    for root, dirs, files in os.walk(os.path.join(temporary_path, day)):
        # Copy files
        for file in files:
            #session_path = os.path.normpath(root).split("/")
            #session_path.insert(-1, temporary_folder)
            #session_path = os.path.join(*session_path)

            session_path = os.path.dirname(root)

            destination_path = os.path.join(env.main_path, session_path)
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            logging.debug(
                f"Moving file: {os.path.join(root, file)} to {os.path.join(destination_path, file)}"
            )
            shutil.copy2(os.path.join(root, file), os.path.join(destination_path, file))
            os.remove(os.path.join(root, file))
            yield True
    participant.store_participant_metadata(os.path.join(storage_path, day, temporary_folder))

    # Delete folders
    folder_path = os.path.join(temporary_path, day)
    shutil.rmtree(folder_path)
