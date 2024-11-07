"""
This module provides the Timestamps class for managing recording timestamps.

Classes:
    Timestamps: Represents the timestamps for recording sessions, including activation time, camera start time, and time windows.

Methods:
    start_recording: Starts recording timestamps for the current session.
"""

import logging
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from features.modules.time_window import TimeWindow


class Timestamps(BaseModel):
    """
    Represents the timestamps for recording sessions, including activation time, camera start time, and time windows.

    Attributes:
        activate_recording (datetime): The time when recording was activated.
        camera_start (Optional[datetime]): The time when the camera started.
        time_windows (Optional[List[TimeWindow]]): A list of time windows during the recording session.
    """
    activate_recording: datetime = None
    camera_start: Optional[datetime] = None
    time_windows: Optional[List[TimeWindow]] = []

    def start_recording(self) -> None:
        """
        Starts recording timestamps for the current session.

        Sets the activation time to the current time and resets the camera start time and time windows.
        """
        logging.info("Start recording timestamps for the current session.")
        self.activate_recording = datetime.now()
        self.camera_start = None
        self.time_windows = []