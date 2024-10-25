from datetime import datetime
from typing import List

from . import os, logging, storage_path, today, date_format, temporary_path, env


def check_if_folder_already_exists(folder_id: str, day: str = today) -> bool:
    return os.path.exists(os.path.join(storage_path, day, folder_id))


def extract_list_of_directories(path: str) -> List[str]:
    result = []
    logging.debug(f"Extracting list of directories from: {path}")
    if os.path.exists(path) and os.path.isdir(path):
        result = os.listdir(path)
        result = [x for x in result if os.path.isdir(os.path.join(path, x))]
    return result


"""
List amount of objects
"""


def list_days() -> List[str]:
    logging.debug(f"Collected the amount of days recorded, from: {storage_path}")
    return extract_list_of_directories(path=storage_path)


def list_people_for_a_specific_day(day: str = today) -> List[str]:
    path = os.path.join(storage_path, day)
    logging.debug(f"Collect amount of recorded people on {day} from: {path}")
    return extract_list_of_directories(path=path)


def list_sessions_for_a_specific_person(day: str = today, person_name: str = ""):
    # TODO: Improve following lines of code
    result = [None]
    hard_drive_folder = os.path.join(storage_path, day, person_name)
    logging.debug(f"Collect recordings for {person_name}.")
    if os.path.exists(hard_drive_folder) and os.path.isdir(hard_drive_folder):
        for root, _, files in os.walk(hard_drive_folder):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext == ".mp4":
                    folder = os.path.join(root, file)
                    temp_result = os.path.relpath(folder, env.main_path)
                    result.append(temp_result)
    return result


"""
List total amount of objects
"""


def list_people_in_total() -> List[str]:
    all_people = []
    logging.debug(f"Collect amount of total recorded people from: {storage_path}")
    if os.path.exists(storage_path):
        for directory in os.listdir(storage_path):
            if os.path.isdir(os.path.join(storage_path, directory)):
                all_people.extend(os.listdir(os.path.join(storage_path, directory)))
    return all_people


def list_sessions_in_total() -> List[str]:
    sessions = []
    logging.debug(f"Collect amount of total sessions from: {storage_path}")

    # TODO: Simplify by looking for all metadata files
    if os.path.exists(storage_path):
        for date_dir in os.listdir(storage_path):
            people_paths = os.path.join(storage_path, date_dir)
            if os.path.isdir(people_paths):
                for person_dir in os.listdir(people_paths):
                    if os.path.isdir(os.path.join(people_paths, person_dir)):
                        sessions.extend(
                            os.listdir(os.path.join(people_paths, person_dir))
                        )
    return sessions

"""
Create Date Selectors for views
"""

def create_date_selection_for_saved_sessions() -> dict:
    dates = list_days()
    return __create_date_dictionary(dates=dates)


def create_date_selection_for_unsaved_sessions() -> dict:
    dates = extract_list_of_directories(temporary_path)
    return __create_date_dictionary(dates=dates)

def __create_date_dictionary(dates: list):
    dict_dates = dict()
    for date in dates:
        real_date = datetime.strptime(date, date_format)
        dict_dates[date] = real_date.strftime("%Y-%m-%d")
    return dict_dates