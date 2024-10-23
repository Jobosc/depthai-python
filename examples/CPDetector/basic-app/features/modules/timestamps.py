from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from features.modules.time_window import TimeWindow
import logging


class Timestamps(BaseModel):
    activate_recording: datetime = None
    camera_start: Optional[datetime] = None
    time_windows: Optional[List[TimeWindow]] = []

    def start_recording(self):
        logging.info("Start recording timestamps for the current session.")
        self.activate_recording = datetime.now()
        self.camera_start = None
        self.time_windows = []
