from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from features.modules.time_window import TimeWindow

class Timestamps(BaseModel):
    activate_recording: datetime = None
    camera_start: Optional[datetime] = None
    time_windows: Optional[List[TimeWindow]] = []

    def start_recording(self):
        self.activate_recording = datetime.now()
        self.camera_start = None
        self.time_windows = []
