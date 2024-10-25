import datetime
import os
import shutil

from features.file_operations.read_storage import list_days, extract_list_of_directories
from utils.parser import ENVParser

env = ENVParser()
today = datetime.datetime.now().strftime(env.date_format)


def create_date_selection_for_saved_sessions() -> dict:
    dates = list_days()

    return __create_date_dictionary(dates=dates)


def create_date_selection_for_unsaved_sessions() -> dict:
    dates = extract_list_of_directories(env.temp_path)
    """if today in dates:
        dates.remove(today)"""

    return __create_date_dictionary(dates=dates)


# TODO: Remove as soon as possible
def delete_session_on_date_folder(day: str) -> bool:
    try:
        folder = os.path.join(env.temp_path, day)
        for root, dirs, files in os.walk(folder):
            for file in files:
                os.remove(os.path.join(root, file))

        # Delete folders
        shutil.rmtree(folder)
        return True
    except:
        return False


def get_hard_drive_space():
    if os.path.exists(env.main_path):
        total, used, free = shutil.disk_usage(env.main_path)
        return total, used, free
    return 0, 0, 0


def __create_date_dictionary(dates: list):
    dict_dates = dict()
    for date in dates:
        real_date = datetime.datetime.strptime(date, env.date_format)
        dict_dates[date] = real_date.strftime("%Y-%m-%d")
    return dict_dates


def __get_unsaved_local_session_days():
    result = []
    if os.path.exists(os.path.join(env.temp_path)):
        folders = os.listdir(env.temp_path)
        result = [x for x in folders if os.path.isdir(os.path.join(env.temp_path, x))]
    return result
