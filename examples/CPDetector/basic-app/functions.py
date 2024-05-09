import datetime
import os
from dotenv import load_dotenv
import shutil
from participant import Participant
import json

load_dotenv(
    "/home/pi/Desktop/luxonis/depthai-python/examples/CPDetector/basic-app/.env"
)

temp_path = os.getenv("TEMP_STORAGE")
main_path = os.getenv("MAIN_STORAGE")
day = datetime.datetime.now().strftime("%Y%m%d")


def get_amount_of_days_recorded():
    if os.path.exists(os.path.join(main_path)):
        return len(os.listdir(os.path.join(main_path)))
    else:
        return 0


def get_amount_of_people_recorded_today():
    if os.path.exists(os.path.join(main_path, temp_path, day)):
        return len(os.listdir(os.path.join(main_path, temp_path, day)))
    else:
        return 0


def get_amount_of_people_recorded_in_total():
    all_people = []
    recordings_path = os.path.join(main_path, temp_path)

    for directory in os.listdir(recordings_path):
        all_people.extend(os.listdir(os.path.join(recordings_path, directory)))
    return len(all_people)


def get_amount_of_sessions_recorded_in_total():
    sessions = []
    recordings_path = os.path.join(main_path, temp_path)

    for date_dir in os.listdir(recordings_path):
        people_paths = os.path.join(recordings_path, date_dir)
        for person_dir in os.listdir(people_paths):
            sessions.extend(os.listdir(os.path.join(people_paths, person_dir)))
    return len(sessions)


def get_amount_of_files_to_move():
    all_files = []
    for _, _, files in os.walk(os.path.join(temp_path, day)):
        for file in files:
            all_files.append(file)

    return len(all_files)


def move_data_from_temp_to_main_storage(folder_name: str, participant: Participant):

    for root, dirs, files in os.walk(os.path.join(temp_path, day)):
        # Copy files
        for file in files:
            session_path = os.path.normpath(root).split("/")
            session_path.insert(-1, folder_name)
            session_path = os.path.join(*session_path)

            destination_path = os.path.join(main_path, session_path)
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            shutil.copy2(os.path.join(root, file), os.path.join(destination_path, file))
            os.remove(os.path.join(root, file))
            yield True
    store_participant_metadata(
        os.path.join(main_path, temp_path, day, folder_name), participant
    )

    # Delete folders
    folder_path = os.path.join(temp_path, day)
    shutil.rmtree(folder_path)


def store_participant_metadata(path: str, metadata: Participant):
    save_file = open(os.path.join(path, "metadata.json"), "w")
    json.dump(vars(metadata), fp=save_file)
    save_file.close()
