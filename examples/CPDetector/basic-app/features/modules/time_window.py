from pydantic import BaseModel
from datetime import datetime, timedelta


class TimeWindow(BaseModel):
    start: datetime
    end: datetime
    start_frame: int
    end_frame: int