import os
import logging
from datetime import datetime

from utils.parser import ENVParser

env = ENVParser()
temporary_path = env.temp_path
storage_path = os.path.join(env.main_path, env.temp_path)
today = datetime.now().strftime(env.date_format)

__all__ = ['os', 'logging', 'temporary_path', 'storage_path', 'today']