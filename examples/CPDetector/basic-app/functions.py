import datetime
import os
from dotenv import load_dotenv
import shutil

load_dotenv(
    "/home/pi/Desktop/luxonis/depthai-python/examples/CPDetector/basic-app/.env"
)

temp_path = os.getenv("TEMP_STORAGE")
main_path = os.getenv("MAIN_STORAGE")
day = datetime.datetime.now().strftime("%Y%m%d")


def get_amount_of_days_recorded():
    return len(os.listdir(temp_path))


def get_amount_of_sessions_recorded_today():
    return len(os.listdir(f"{temp_path}/{day}/"))


def move_data_from_temp_to_main_storage(folder_name: str):

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

    # Delete folders
    try:
        folder_path = os.path.join(temp_path, day)
        shutil.rmtree(folder_path)
        print("Folder and its content removed")
    except:
        print("Folder not deleted")
