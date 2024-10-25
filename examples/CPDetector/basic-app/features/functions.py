import datetime
import os
import shutil

from utils.parser import ENVParser

env = ENVParser()


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
