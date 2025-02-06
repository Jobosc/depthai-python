"""
This module initializes the file operations package and sets up environment variables.

It imports necessary modules and defines global variables for temporary and storage paths, date format, and today's date.

Modules:
    os: Provides a way of using operating system dependent functionality.
    logging: Provides a way of logging messages.
    datetime: Supplies classes for manipulating dates and times.
    ENVParser: Parses environment variables from a configuration file.

Attributes:
    env (ENVParser): An instance of the ENVParser class to access environment variables.
    temporary_path (str): The path to the temporary storage.
    storage_path (str): The path to the main storage.
    date_format (str): The format for dates.
    today (str): Today's date in the specified date format.
"""

import logging
import os
from datetime import datetime

from utils.parser import ENVParser

env = ENVParser()
temporary_path = env.temp_path
storage_path = os.path.join(env.main_path, env.temp_path)
date_format = env.date_format
today = datetime.now().strftime(env.date_format)

__all__ = ['os', 'logging', 'temporary_path', 'storage_path', 'today', 'date_format']
