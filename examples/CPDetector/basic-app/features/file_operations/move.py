import shutil
from typing import List

from features.file_operations.delete import delete_temporary_recordings
from features.modules.participant import Participant
from . import os, today, temporary_path, logging, storage_path


def list_files_to_move() -> List[str]:
    all_files = []
    for _, _, files in os.walk(os.path.join(temporary_path, str(today))):
        for file in files:
            all_files.append(file)
    logging.debug("Collected all the files that need to be moved.")
    return all_files


def move_data_from_temp_to_main_storage(
        folder_id: str, participant: Participant, day: str = today
) -> bool:
    destination_path = os.path.join(storage_path, day, folder_id)
    if not os.path.exists(destination_path):  # Create missing folder
        os.makedirs(destination_path)

    for root, dirs, files in os.walk(os.path.join(temporary_path, day)):
        for file in files:
            shutil.copy2(os.path.join(root, file), os.path.join(destination_path, file))  # Copy file
            logging.debug(
                f"Moving file: {os.path.join(root, file)} to {os.path.join(destination_path, file)} complete.")
            yield True
    participant.store_participant_metadata(os.path.join(storage_path, day, folder_id))

    delete_temporary_recordings()
