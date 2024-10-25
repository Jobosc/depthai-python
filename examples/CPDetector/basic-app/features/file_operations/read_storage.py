from typing import List

from . import os, logging, storage_path, today


def __extract_list_of_directories(path: str) -> List[str]:
    result = []
    logging.debug(f"Extracting list of directories from: {path}")
    if os.path.exists(path) and os.path.isdir(path):
        result = os.listdir(path)
        result = [
            x for x in result if os.path.isdir(os.path.join(path, x))
        ]
    return result


def list_days() -> List[str]:
    logging.debug(f"Collected the amount of days recorded, from: {storage_path}")
    return __extract_list_of_directories(path=storage_path)


def list_people_for_a_specific_day(required_day: str = today) -> List[str]:
    path = os.path.join(storage_path, required_day)
    logging.debug(f"Collect amount of recorded people on {required_day} from: {path}")
    return __extract_list_of_directories(path=path)


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

    #TODO: Simplify by looking for all metadata files
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