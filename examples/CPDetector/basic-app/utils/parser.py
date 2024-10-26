import os
import platform
from datetime import datetime

from dotenv import load_dotenv

from utils.singleton import singleton


@singleton
class ENVParser:
    _temp_path = None
    _main_path = None
    _date_format = None
    _log_path = None
    _log_mode = None
    _log_filename = None

    def __init__(self) -> None:
        if platform.system() == "Linux":
            load_dotenv("/home/pi/depthai-python/examples/CPDetector/basic-app/.env")
        else:
            load_dotenv("examples/CPDetector/basic-app/.env")

        self._temp_path = os.getenv("TEMP_STORAGE")
        self._main_path = os.getenv("MAIN_STORAGE")
        self._date_format = os.getenv("DATE_FORMAT")
        self._log_mode = os.getenv("LOG_MODE")
        self._log_filename = os.getenv("LOG_FILENAME")

        if platform.system() == "Linux":
            today_string = datetime.now().strftime(self._date_format)
            self._log_path = os.path.join(self._main_path, self._temp_path, today_string, self._log_filename)
        else:
            self._log_path = self._log_filename
        

    @property
    def temp_path(self):
        return self._temp_path

    @temp_path.setter
    def temp_path(self, value):
        self._temp_path = value

    @property
    def main_path(self):
        return self._main_path

    @main_path.setter
    def main_path(self, value):
        self._main_path = value

    @property
    def date_format(self):
        return self._date_format

    @date_format.setter
    def date_format(self, value):
        self._date_format = value
    
    @property
    def log_path(self):
        return self._log_path
    
    @property
    def log_mode(self):
        return self._log_mode
    
    @property
    def log_filename(self):
        return self._log_filename
