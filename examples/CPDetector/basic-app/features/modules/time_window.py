from datetime import datetime

from pydantic import BaseModel


class TimeWindow(BaseModel):
    start: datetime
    end: datetime
    start_frame: int
    end_frame: int
