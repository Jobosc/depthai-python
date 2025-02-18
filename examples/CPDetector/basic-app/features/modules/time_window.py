"""
This module provides the TimeWindow class for managing time intervals.

Classes:
    TimeWindow: Represents a time interval with a start and end datetime.
"""

from datetime import datetime

from pydantic import BaseModel


class TimeWindow(BaseModel):
    """
    Represents a time interval with a start and end datetime.

    Attributes:
        start (datetime): The start time of the interval.
        end (datetime): The end time of the interval.
    """
    start: datetime
    end: datetime
