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
