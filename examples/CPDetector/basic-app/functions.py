import datetime
import os
from dotenv import load_dotenv
import shutil
from participant import Participant
import json

load_dotenv("./depthai-python/examples/CPDetector/basic-app/.env")

temp_path = os.getenv("TEMP_STORAGE")
main_path = os.getenv("MAIN_STORAGE")
date_format = os.getenv("DATE_FORMAT")
today = datetime.datetime.now().strftime(date_format)


def get_recorded_days():
    result = []
    if os.path.exists(os.path.join(main_path, temp_path)):
        result = os.listdir(os.path.join(main_path, temp_path))
    return result


def get_recorded_people_for_a_specific_day(required_day: str = today):
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
    for _, _, files in os.walk(os.path.join(temp_path, today)):
        for file in files:
            all_files.append(file)

    return all_files


def move_data_from_temp_to_main_storage(
    folder_name: str, participant: Participant, day: str = today
):

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


def create_date_selection_for_saved_sessions() -> dict:
    dates = get_recorded_days()

    return __create_date_dictionary(dates=dates)


def create_date_selection_for_unsaved_sessions() -> dict:
    dates = __get_unsaved_local_session_days()
    if today in dates:
        dates.remove(today)

    return __create_date_dictionary(dates=dates)


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


def delete_session_on_date_folder(day: str) -> bool:
    try:
        folder = os.path.join(temp_path, day)
        for root, dirs, files in os.walk(folder):
            for file in files:
                os.remove(os.path.join(root, file))

        # Delete folders
        shutil.rmtree(folder)
        return True
    except:
        return False


def read_participant_metadata(date: str, person: str):
    load_file = open(
        os.path.join(main_path, temp_path, date, person, "metadata.json"), "r"
    )
    data = json.load(fp=load_file)
    load_file.close()

    return data


def __create_date_dictionary(dates: list):
    dict_dates = dict()
    for date in dates:
        real_date = datetime.datetime.strptime(date, date_format)
        dict_dates[date] = real_date.strftime("%Y-%m-%d")

    return dict_dates


def store_participant_metadata(path: str, metadata: Participant):
    save_file = open(os.path.join(path, "metadata.json"), "w")
    json.dump(vars(metadata), fp=save_file)
    save_file.close()


def __get_unsaved_local_session_days():
    result = []
    if os.path.exists(os.path.join(temp_path)):
        result = os.listdir(temp_path)
    return result
