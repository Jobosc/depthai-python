"""
This module provides functions to read and list directories and files related to the application's storage.

It defines functions to check if a folder already exists, extract a list of directories, and list days, people, and sessions.

Functions:
    check_if_folder_already_exists: Checks if a folder already exists for a given day and folder ID.
    create_date_selection_for_saved_sessions: Creates a date selection dictionary for saved sessions.
    create_date_selection_for_unsaved_sessions: Creates a date selection dictionary for unsaved sessions.
    extract_list_of_directories: Extracts a list of directories from a given path.
    list_days: Lists the amount of days recorded.
    list_people_for_a_specific_day: Lists the people recorded for a specific day.
    list_people_in_total: Lists the total amount of recorded people.
    list_sessions_for_a_specific_person: Lists the sessions recorded for a specific person on a specific day.
    list_sessions_in_total: Lists the total amount of recorded sessions.
    __create_date_dictionary: Helper function to create a date dictionary from a list of dates.
"""

import glob
from datetime import datetime
from typing import List

from . import os, logging, storage_path, today, date_format, temporary_path, env


def check_if_folder_already_exists(folder_id: str, day: str = today) -> bool:
    """
    Checks if a folder already exists for a given day and folder ID.

    Args:
        folder_id (str): The ID of the folder to check.
        day (str, optional): The day to check the folder for. Defaults to today.

    Returns:
        bool: True if the folder exists, False otherwise.
    """
    return os.path.exists(os.path.join(storage_path, day, folder_id))


def extract_list_of_directories(path: str) -> List[str]:
    """
    Extracts a list of directories from a given path.

    Args:
        path (str): The path to extract directories from.

    Returns:
        List[str]: A list of directory names.
    """
    result = []
    logging.debug(f"Extracting list of directories from: {path}")
    if os.path.exists(path) and os.path.isdir(path):
        result = os.listdir(path)
        result = [x for x in result if os.path.isdir(os.path.join(path, x))]
        result.sort()
    if env.log_filename in result:  # Remove folder that is used for logging
        result.remove(env.log_filename)
    elif '.DS_Store' in result:  # Remove folder that is used for logging
        result.remove('.DS_Store')
    return result


def list_days() -> List[str]:
    """
    Lists the amount of days recorded.

    Returns:
        List[str]: A list of recorded days.
    """
    logging.debug(f"Collected the amount of days recorded, from: {storage_path}")
    return extract_list_of_directories(path=storage_path)


def list_people_for_a_specific_day(day: str = today) -> List[str]:
    """
    Lists the people recorded for a specific day.

    Args:
        day (str, optional): The day to list people for. Defaults to today.

    Returns:
        List[str]: A list of recorded people for the specified day.
    """
    path = os.path.join(storage_path, day)
    logging.debug(f"Collect amount of recorded people on {day} from: {path}")
    return extract_list_of_directories(path=path)


def list_sessions_for_a_specific_person(day: str = today, person_name: str = "") -> List[str]:
    """
    Lists the sessions recorded for a specific person on a specific day.

    Args:
        day (str, optional): The day to list sessions for. Defaults to today.
        person_name (str, optional): The name of the person to list sessions for. Defaults to an empty string.

    Returns:
        List[str]: A list of recorded sessions for the specified person on the specified day.
    """
    result = []
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
    result.sort()
    result = [None] + result
    return result


def list_people_in_total() -> List[str]:
    """
    Lists the total amount of recorded people.

    Returns:
        List[str]: A list of all recorded people.
    """
    all_people = []
    logging.debug(f"Collect amount of total recorded people from: {storage_path}")
    if os.path.exists(storage_path):
        for directory in os.listdir(storage_path):
            if os.path.isdir(os.path.join(storage_path, directory)):
                all_people.extend(os.listdir(os.path.join(storage_path, directory)))
                if env.log_filename in all_people:  # Remove folder that is used for logging
                    all_people.remove(env.log_filename)
                elif '.DS_Store' in all_people:  # Remove folder that is used for logging
                    all_people.remove('.DS_Store')
    return all_people


def list_sessions_in_total() -> List[str]:
    """
    Lists the total amount of recorded sessions.

    Returns:
        List[str]: A list of all recorded sessions.
    """
    logging.debug(f"Collect amount of total sessions from: {storage_path}")
    return glob.glob(os.path.join(storage_path, "**", env.metadata_file_name), recursive=True)


def create_date_selection_for_saved_sessions() -> dict:
    """
    Creates a date selection dictionary for saved sessions.

    Returns:
        dict: A dictionary with dates as keys and formatted date strings as values.
    """
    temp_dates = []
    dates = list_days()

    for day in dates:
        if extract_list_of_directories(os.path.join(storage_path, day)):
            temp_dates.append(day)

    return __create_date_dictionary(dates=temp_dates)


def create_date_selection_for_unsaved_sessions() -> dict:
    """
    Creates a date selection dictionary for unsaved sessions.

    Returns:
        dict: A dictionary with dates as keys and formatted date strings as values.
    """
    dates = extract_list_of_directories(temporary_path)
    return __create_date_dictionary(dates=dates)


def __create_date_dictionary(dates: list) -> dict:
    """
    Helper function to create a date dictionary from a list of dates.

    Args:
        dates (list): A list of date strings.

    Returns:
        dict: A dictionary with dates as keys and formatted date strings as values.
    """
    dict_dates = dict()
    for date in dates:
        real_date = datetime.strptime(date, date_format)
        dict_dates[date] = real_date.strftime("%Y-%m-%d")
    return dict_dates