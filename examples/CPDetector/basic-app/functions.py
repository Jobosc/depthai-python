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
date_format = os.getenv("DATE_FORMAT")
day = datetime.datetime.now().strftime("%Y%m%d")


def get_recorded_days():
    result = []
    if os.path.exists(os.path.join(main_path, temp_path)):
        result = os.listdir(os.path.join(main_path, temp_path))
    return result


def get_recorded_people_for_a_specific_day(required_day: str = day):
    result = []
    if os.path.exists(os.path.join(main_path, temp_path, required_day)):
        result = os.listdir(os.path.join(main_path, temp_path, required_day))
    return result


def get_recorded_people_in_total():
    all_people = []
    recordings_path = os.path.join(main_path, temp_path)

    for directory in os.listdir(recordings_path):
        all_people.extend(os.listdir(os.path.join(recordings_path, directory)))
    return all_people


def get_all_recorded_sessions_so_far():
    sessions = []
    recordings_path = os.path.join(main_path, temp_path)

    for date_dir in os.listdir(recordings_path):
        people_paths = os.path.join(recordings_path, date_dir)
        for person_dir in os.listdir(people_paths):
            sessions.extend(os.listdir(os.path.join(people_paths, person_dir)))
    return sessions


def get_files_to_move():
    all_files = []
    for _, _, files in os.walk(os.path.join(temp_path, day)):
        for file in files:
            all_files.append(file)

    return all_files


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


def create_date_selection() -> dict:
    dates = get_recorded_days()

    dict_dates = dict()
    for date in dates:
        real_date = datetime.datetime.strptime(date, date_format)
        dict_dates[date] = real_date.strftime("%Y-%m-%d")

    return dict_dates


def delete_person_on_day_folder(day: str, person: str) -> bool:
    try:
        folder = os.path.join(main_path, temp_path, day, person)
        for root, dirs, files in os.walk(folder):
            for file in files:
                os.remove(os.path.join(root, file))

        # Delete folders
        shutil.rmtree(folder)
        return True
    except:
        return False
