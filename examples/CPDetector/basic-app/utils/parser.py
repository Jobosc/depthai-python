import os
from dotenv import load_dotenv
from utils.singleton import singleton


@singleton
class ENVParser:
    _temp_path = None
    _main_path = None
    _date_format = None
    
    def __init__(self) -> None:
        load_dotenv("/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/examples/CPDetector/basic-app/.env")

        self._temp_path = os.getenv("TEMP_STORAGE")
        self._main_path = os.getenv("MAIN_STORAGE")
        self._date_format = os.getenv("DATE_FORMAT")
    
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