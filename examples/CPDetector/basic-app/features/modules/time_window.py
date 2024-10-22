from datetime import datetime, timedelta

from pydantic import BaseModel


class TimeWindow(BaseModel):
    start: datetime
    end: datetime
    start_seconds: int
    end_seconds: int
