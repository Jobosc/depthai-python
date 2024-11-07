"""
This module provides the `ENVParser` class, which is a singleton used to parse environment variables.

The `ENVParser` class loads environment variables from a `.env` file and provides properties to access these variables.

Classes:
    ENVParser: A singleton class that parses and provides access to environment variables.
"""

import os
import platform
from datetime import datetime

from dotenv import load_dotenv

from utils.singleton import singleton


@singleton
class ENVParser:
    """
    A singleton class to parse and provide access to environment variables.

    This class loads environment variables from a `.env` file and provides properties to access these variables.
    """

    _temp_path = None
    _main_path = None
    _date_format = None
    _log_path = None
    _log_mode = None
    _log_filename = None
    _video_delta_start = None
    _video_delta_end = None
    _conversion_file_prefix = None
    _metadata_file_name = None

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
        self._video_delta_start = datetime.strptime(os.getenv("VIDEO_DELTA_START"), "%H:%M:%S.%f").time()
        self._video_delta_end = datetime.strptime(os.getenv("VIDEO_DELTA_END"), "%H:%M:%S.%f").time()
        self._conversion_file_prefix = os.getenv("CONVERSION_FILE_PREFIX")
        self._metadata_file_name = os.getenv("METADATA_FILE_NAME")

        if platform.system() == "Linux":
            today_string = datetime.now().strftime(self._date_format)
            self._log_path = os.path.join(self._main_path, self._temp_path, today_string, self._log_filename)
        else:
            self._log_path = self._log_filename

    @property
    def temp_path(self) -> str:
        """
        Gets or sets the temporary storage path.
        """
        return self._temp_path

    @temp_path.setter
    def temp_path(self, value) -> None:
        self._temp_path = value

    @property
    def main_path(self) -> str:
        """
        Gets or sets the main storage path.
        """
        return self._main_path

    @main_path.setter
    def main_path(self, value) -> None:
        self._main_path = value

    @property
    def date_format(self) -> str:
        """
        Gets or sets the date format.
        """
        return self._date_format

    @date_format.setter
    def date_format(self, value) -> None:
        self._date_format = value

    @property
    def log_path(self) -> str:
        """
        Gets the log file path.
        """
        return self._log_path

    @property
    def log_mode(self) -> str:
        """
        Gets the log mode.
        """
        return self._log_mode

    @property
    def log_filename(self) -> str:
        """
        Gets the log file name.
        """
        return self._log_filename

    @property
    def video_delta_start(self) -> datetime.time:
        """
        Gets the video delta start time.
        """
        return self._video_delta_start

    @property
    def video_delta_end(self) -> datetime.time:
        """
        Gets the video delta end time.
        """
        return self._video_delta_end

    @property
    def conversion_file_prefix(self) -> str:
        """
        Gets the conversion file prefix.
        """
        return self._conversion_file_prefix

    @property
    def metadata_file_name(self) -> str:
        """
        Gets the metadata file name.
        """
        return self._metadata_file_name